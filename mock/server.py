#!/usr/bin/env python3
"""A local stand-in for the Warp pricing API.

    python mock/server.py                 # http://localhost:3002
    python mock/server.py --latency       # realistic, uneven response times
    python mock/server.py --flaky         # ~1 request in 8 fails with a 503
    python mock/server.py --require-key   # demand an apikey header (any value works)

Zero dependencies, standard library only.

It serves exactly the same numbers as the CSVs in data/, so a proposal built
against this API and one built against the files are identical. Use whichever
you prefer. The API exists because the real thing is a service, and a tool a rep
leans on during a live call has to behave when that service is slow or down.

No Warp API key is needed or issued. With --require-key the server accepts any
non-empty apikey header, so you can build the auth path without holding a secret.
"""
import argparse, csv, json, os, random, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OPTS = {"latency": False, "flaky": False, "require_key": False}
RNG = random.Random(90210)


def load(name):
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


def numify(row, fields):
    out = dict(row)
    for f in fields:
        if out.get(f) not in (None, ""):
            out[f] = float(out[f]) if "." in str(out[f]) else int(out[f])
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        sys.stderr.write("  %s\n" % (fmt % a))

    def send(self, code, payload):
        body = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        route, q = url.path.rstrip("/") or "/", parse_qs(url.query)

        if OPTS["require_key"] and route != "/health":
            key = self.headers.get("apikey") or self.headers.get("Apikey")
            if not key:
                return self.send(401, {
                    "error": "missing_api_key",
                    "message": "Send an apikey header. This mock accepts any "
                               "non-empty value; no real Warp key exists for "
                               "this exercise."})

        if OPTS["flaky"] and route.startswith("/rates") and RNG.random() < 0.125:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", "1")
            body = json.dumps({"error": "upstream_unavailable",
                               "message": "Pricing engine is briefly unavailable. "
                                          "Retry."}).encode()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if OPTS["latency"]:
            # Rate lookups are the slow call. Everything else is reference data.
            time.sleep(RNG.uniform(0.25, 1.4) if route.startswith("/rates")
                       else RNG.uniform(0.02, 0.12))

        if route == "/health":
            return self.send(200, {"ok": True})

        if route == "/rates":
            need = ["origin_metro", "origin_state", "dest_metro", "dest_state"]
            missing = [k for k in need if not q.get(k)]
            if missing:
                return self.send(400, {"error": "missing_parameters",
                                       "missing": missing})
            key = tuple(q[k][0].strip().lower() for k in need)
            for r in load("rate_card.csv"):
                if (r["origin_metro"].lower(), r["origin_state"].lower(),
                        r["dest_metro"].lower(), r["dest_state"].lower()) == key:
                    return self.send(200, numify(r, [
                        "miles", "ltl_base", "ltl_per_pallet", "ltl_min_charge",
                        "ftl_flat_rate", "transit_days_standard"]))
            return self.send(404, {
                "error": "lane_not_rated",
                "message": f"No published rate for {q[need[0]][0]} "
                           f"{q[need[1]][0]} to {q[need[2]][0]} {q[need[3]][0]}. "
                           f"This lane has to be built before it can be quoted.",
                "origin_metro": q[need[0]][0], "dest_metro": q[need[2]][0]})

        if route == "/lanes":
            return self.send(200, {"lanes": [
                numify(r, ["miles", "ltl_base", "ltl_per_pallet",
                           "ltl_min_charge", "ftl_flat_rate",
                           "transit_days_standard"]) for r in load("rate_card.csv")]})

        if route == "/accessorials":
            return self.send(200, {"accessorials":
                                   [numify(r, ["rate"]) for r in load("accessorials.csv")]})

        if route == "/service-levels":
            return self.send(200, {"service_levels": [
                numify(r, ["linehaul_multiplier", "transit_days_delta"])
                for r in load("service_levels.csv")]})

        if route == "/volume-tiers":
            return self.send(200, {"volume_tiers": [
                numify(r, ["min_monthly_shipments", "max_monthly_shipments",
                           "discount_pct"]) for r in load("volume_tiers.csv")]})

        if route == "/config":
            return self.send(200, {r["key"]: float(r["value"])
                                   for r in load("pricing_config.csv")})

        if route == "/accounts":
            return self.send(200, {"accounts": [
                numify(r, ["monthly_shipments", "avg_cost_per_shipment",
                           "tenure_months", "on_time_pct"])
                for r in load("account_history.csv")]})

        self.send(404, {"error": "unknown_route", "path": route,
                        "routes": ["/health", "/rates", "/lanes", "/accessorials",
                                   "/service-levels", "/volume-tiers", "/config",
                                   "/accounts"]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=3002)
    ap.add_argument("--latency", action="store_true",
                    help="uneven response times, like a real pricing engine")
    ap.add_argument("--flaky", action="store_true",
                    help="about 1 rate lookup in 8 returns a 503")
    ap.add_argument("--require-key", action="store_true",
                    help="require an apikey header; any non-empty value passes")
    a = ap.parse_args()
    OPTS.update(latency=a.latency, flaky=a.flaky, require_key=a.require_key)

    on = [n for n, v in (("latency", a.latency), ("flaky", a.flaky),
                         ("require-key", a.require_key)) if v]
    print(f"Warp pricing mock on http://localhost:{a.port}")
    print(f"  modes: {', '.join(on) if on else 'none (fast, reliable, open)'}")
    print(f"  data:  {os.path.normpath(DATA)}")
    print("  stop:  ctrl-c\n")
    try:
        ThreadingHTTPServer(("localhost", a.port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
