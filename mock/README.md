# The pricing API mock

A local stand-in for Warp's pricing service. Zero dependencies.

```bash
python mock/server.py
```

It serves on `http://localhost:3002` and reads the same files as `data/`, so
**the numbers are identical either way**. A proposal built against this API and
one built straight from the CSVs will validate the same.

**You do not need a Warp API key.** None exists for this exercise, and none will
be issued. With `--require-key` the server accepts any non-empty `apikey` header,
so you can write and test the auth path without ever holding a secret.

## Using it or not

Reading the CSVs directly is completely acceptable and nothing in the grading
prefers one over the other. The must-haves are reachable either way.

Use the API if you want to build the more realistic thing. On a live call the
pricing engine is a service, and services are sometimes slow and sometimes down
while a customer is mid-sentence. What your tool shows the rep in that moment is
a real design question, and it is the one the flags below let you explore.

## Endpoints

| Route | Returns |
|---|---|
| `GET /health` | liveness |
| `GET /rates?origin_metro=&origin_state=&dest_metro=&dest_state=` | one lane, or `404 lane_not_rated` |
| `GET /lanes` | every lane in the rate card |
| `GET /accessorials` | accessorial codes, units and rates |
| `GET /service-levels` | multipliers and transit deltas |
| `GET /volume-tiers` | shipment count bands and discounts |
| `GET /config` | fuel surcharge, FTL thresholds, detention free hours |
| `GET /accounts` | existing accounts, for comparables |

```bash
curl "http://localhost:3002/rates?origin_metro=Chicago&origin_state=IL&dest_metro=Atlanta&dest_state=GA"
```

A lane Warp has no rate for returns **404** with a machine-readable
`lane_not_rated` error, not a guessed price. Handle it the way the spec requires:
that freight goes in `excluded`, never quoted.

## Making it behave like production

```bash
python mock/server.py --latency       # uneven response times, rate lookups are slowest
python mock/server.py --flaky         # about 1 rate lookup in 8 returns 503 with Retry-After
python mock/server.py --require-key   # demand an apikey header; any non-empty value passes
```

Combine them freely. If you build against the API, run at least once with
`--latency --flaky` before you record your demo. A rep on a call cannot stare at a
spinner, and a proposal that silently drops a lane because one request failed is
worse than one that says the lane is still loading.
