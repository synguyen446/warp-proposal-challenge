

from __future__ import annotations

import argparse
import json
import threading
import webbrowser
from solution.update_log_pipeline import run_compare_pipeline
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Warp Live Proposal</title><style>
:root{--ink:#17221d;--muted:#68756e;--line:#dfe6e1;--bg:#f3f6f4;--green:#157347;--soft:#e9f6ef;--red:#a43232}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}.page{max-width:1100px;margin:auto;padding:24px}.top,.lane-head,.price,.controls{display:flex;justify-content:space-between;gap:18px}.top{align-items:center;margin-bottom:18px}.controls{align-items:center}.picker{min-width:220px;padding:8px 32px 8px 10px;border:1px solid var(--line);border-radius:8px;background:white;color:var(--ink);font:inherit}.button{padding:9px 13px;border:0;border-radius:8px;background:var(--ink);color:white;font:inherit;font-weight:700;cursor:pointer}.button.secondary{border:1px solid var(--line);background:white;color:var(--ink)}.live{padding:7px 11px;border-radius:99px;background:var(--soft);color:var(--green);font-weight:700}.card{background:white;border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:14px;box-shadow:0 8px 25px #1c30260b}.hero{display:grid;grid-template-columns:2fr 1fr;gap:14px}.summary{font-size:16px;border-left:4px solid var(--green);padding-left:15px}.total{background:var(--ink);color:white}.money{font-size:31px;font-weight:800}.muted{color:var(--muted)}h1,h2,h3,p{margin-top:0}h1{margin-bottom:0;font-size:22px}h2{font-size:17px}.route{font-size:18px;font-weight:750}.ok{color:var(--green);font-weight:750}.bad{color:var(--red);font-weight:750}.facts{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.pill{padding:5px 8px;border-radius:7px;background:#eef3f0;font-size:13px}.price{padding-top:12px;border-top:1px solid var(--line);flex-wrap:wrap}.price div{min-width:110px}.price small{display:block;color:var(--muted)}.columns{display:grid;grid-template-columns:1fr 1fr;gap:14px}ul{margin:0;padding-left:20px}li{margin:6px 0}.error{padding:20px;color:var(--red)}dialog{width:min(600px,calc(100% - 30px));border:0;border-radius:15px;padding:0;box-shadow:0 24px 70px #0004}dialog::backdrop{background:#17221d88}.dialog-body{padding:22px}.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.compare-grid label{display:grid;gap:5px;color:var(--muted);font-size:13px}.compare-grid .picker{width:100%;min-width:0}.dialog-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:18px}.compare-result{margin-top:18px;padding:14px;border-left:4px solid var(--green);border-radius:0 8px 8px 0;background:#f1f8f4}.compare-result[hidden]{display:none}@media(max-width:760px){.hero,.columns,.compare-grid{grid-template-columns:1fr}.top,.lane-head{align-items:flex-start;flex-direction:column}.controls{width:100%;flex-wrap:wrap}.picker{min-width:0;flex:1}.page{padding:14px}}
</style></head><body><main class="page"><header class="top"><div><h1>Warp Live Proposal</h1><span class="muted" id="call"></span></div><div class="controls"><select class="picker" id="proposalPicker" aria-label="Select proposal"></select><button class="button" id="openCompare">Compare</button><span class="live">● Live · <span id="updated">waiting</span></span></div></header><div id="app"></div></main><dialog id="compareDialog"><div class="dialog-body"><h2>Compare proposals</h2><p class="muted">Choose the earlier and updated proposal. The comparison pipeline will summarize the customer-facing impact.</p><div class="compare-grid"><label>Old proposal<select class="picker" id="oldProposal"></select></label><label>New proposal<select class="picker" id="newProposal"></select></label></div><div class="compare-result" id="compareResult" hidden></div><div class="dialog-actions"><button class="button secondary" id="closeCompare">Close</button><button class="button" id="runCompare">Run comparison</button></div></div></dialog>
<script>
const $=s=>document.querySelector(s),money=v=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(Number(v||0)),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const asList=items=>Array.isArray(items)?items:(items?[items]:[]);
const list=(title,items)=>{const values=asList(items);return `<section class="card"><h2>${title}</h2>${values.length?`<ul>${values.map(x=>`<li>${esc(typeof x==='string'?x:[x.description,x.reason].filter(Boolean).join(' — '))}</li>`).join('')}</ul>`:'<span class="muted">None</span>'}</section>`};
function lane(x){const p=x.pricing;return `<section class="card"><div class="lane-head"><div class="route">${esc(x.origin_metro)}, ${esc(x.origin_state)} → ${esc(x.dest_metro)}, ${esc(x.dest_state)}</div><div class="${x.serviceable?'ok':'bad'}">${x.serviceable?'SERVICEABLE':'NOT SERVICEABLE'}</div></div><div class="facts"><span class="pill">${esc(x.mode_quoted||'Mode pending')}</span><span class="pill">${esc(x.service_level||'Service pending')}</span><span class="pill">${esc(x.pallets_per_shipment)} pallets</span><span class="pill">${esc(x.weight_lb_per_shipment)} lb/shipment</span><span class="pill">${esc(x.shipments_per_month)} shipments/month</span><span class="pill">${esc(x.transit_days)} transit days</span></div><p>${esc(x.rationale||'')}</p>${p?`<div class="price"><div><small>Linehaul</small><strong>${money(p.linehaul)}</strong></div><div><small>Fuel</small><strong>${money(p.fuel_surcharge)}</strong></div><div><small>Accessorials</small><strong>${money(p.accessorials_total)}</strong></div><div><small>Discount</small><strong>−${money(p.discount)}</strong></div><div><small>Per shipment</small><strong>${money(p.shipment_total)}</strong></div><div><small>Monthly</small><strong>${money(p.monthly_total)}</strong></div></div>`:`<div class="bad">${esc((x.unserviceable_reason||'Pricing unavailable').replaceAll('_',' '))}</div>`}</section>`}
function render(d){$('#call').textContent=d.call_id||'';const c=d.customer||{},tier=d.volume_tier||{};$('#app').innerHTML=`<div class="hero"><section class="card"><h2>${esc(c.company||'Customer pending')}</h2><p class="muted">${esc([c.contact,c.industry].filter(Boolean).join(' · '))}</p><div class="summary"><small class="ok">READ ALOUD</small><br>${esc(d.deal_summary||'Summary pending.')}</div></section><section class="card total"><small>MONTHLY TOTAL</small><div class="money">${money(d.monthly_total)}</div><p>Annual: <strong>${money(d.annual_total)}</strong></p><span>${esc(tier.tier_name||'No')} tier · ${esc(tier.discount_pct||0)}% discount</span></section></div><h2>Lane pricing</h2>${(d.lanes||[]).map(lane).join('')||'<div class="card muted">No lanes yet.</div>'}<div class="columns">${list('Confirm on this call',d.open_questions)}${list('Assumptions',d.assumptions)}</div>${d.excluded?.length?list('Not included',d.excluded):''}`;$('#updated').textContent=new Date().toLocaleTimeString()}
let selected='',proposalFiles=[];const options=()=>proposalFiles.map(x=>`<option value="${esc(x.file)}">${esc(x.label)}</option>`).join('');async function loadChoices(){const r=await fetch('/api/proposals',{cache:'no-store'});const data=await r.json();proposalFiles=data.proposals;const picker=$('#proposalPicker'),previous=selected;picker.innerHTML=options();selected=proposalFiles.some(x=>x.file===previous)?previous:(data.selected||proposalFiles[0]?.file||'');picker.value=selected;picker.onchange=()=>{selected=picker.value;refresh()}}
async function refresh(){try{if(!selected)await loadChoices();if(!selected)throw Error('No proposal JSON files found.');const r=await fetch(`/api/proposal?file=${encodeURIComponent(selected)}`,{cache:'no-store'});if(!r.ok)throw Error(await r.text());render(await r.json())}catch(e){$('#app').innerHTML=`<div class="card error">${esc(e.message)}</div>`}}loadChoices().then(refresh);setInterval(()=>loadChoices().then(refresh),2000);
const dialog=$('#compareDialog');$('#openCompare').onclick=()=>{const old=$('#oldProposal'),newer=$('#newProposal');old.innerHTML=options();newer.innerHTML=options();old.value=selected;newer.value=proposalFiles.find(x=>x.file!==selected)?.file||selected;$('#compareResult').hidden=true;dialog.showModal()};$('#closeCompare').onclick=()=>dialog.close();$('#runCompare').onclick=async()=>{const result=$('#compareResult');result.hidden=false;result.textContent='Running comparison…';try{const r=await fetch('/api/compare',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({old_file:$('#oldProposal').value,new_file:$('#newProposal').value})});if(!r.ok)throw Error(await r.text());const data=await r.json();result.innerHTML=`<strong>Summary</strong><p>${esc(data.summary)}</p>`}catch(e){result.textContent=e.message}};
</script></body></html>"""


class ProposalHandler(BaseHTTPRequestHandler):
    proposal_dir: Path
    initial_file: str | None

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/" or self.path.startswith("/?"):
            self.send_content(HTML.encode(), "text/html; charset=utf-8")
        elif self.path.startswith("/api/proposals"):
            files = sorted(self.proposal_dir.glob("*.json"))
            result = {
                "selected": self.initial_file,
                "proposals": [
                    {"file": path.name, "label": path.stem.replace("_", " ").title()}
                    for path in files
                ],
            }
            self.send_content(json.dumps(result).encode(), "application/json")
        elif self.path.startswith("/api/proposal"):
            try:
                query = parse_qs(urlparse(self.path).query)
                filename = query.get("file", [self.initial_file])[0]
                if (
                    not filename
                    or Path(filename).name != filename
                    or not filename.endswith(".json")
                ):
                    raise ValueError("Invalid proposal filename")
                proposal_path = self.proposal_dir / filename
                data = json.loads(proposal_path.read_text(encoding="utf-8"))
                self.send_content(json.dumps(data).encode(), "application/json")
            except (OSError, ValueError, json.JSONDecodeError) as error:
                self.send_error(500, f"Could not read proposal: {error}")
        else:
            self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/compare":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length))
            if not isinstance(request, dict):
                raise ValueError("Comparison request must be a JSON object")
            old_path = self.safe_proposal_path(request.get("old_file"))
            new_path = self.safe_proposal_path(request.get("new_file"))
            old_proposal = json.loads(old_path.read_text(encoding="utf-8"))
            new_proposal = json.loads(new_path.read_text(encoding="utf-8"))
            result = run_compare_pipeline(old_proposal, new_proposal)
            self.send_content(json.dumps(result).encode(), "application/json")
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            self.send_error(400, f"Could not compare proposals: {error}")

    def safe_proposal_path(self, filename: object) -> Path:
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise ValueError("Invalid proposal filename")
        if not filename.endswith(".json"):
            raise ValueError("Proposal must be a JSON file")
        path = self.proposal_dir / filename
        if not path.is_file():
            raise ValueError(f"Proposal not found: {filename}")
        return path

    def send_content(self, content: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, message: str, *args: object) -> None:
        print(f"[proposal-ui] {message % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Display a live proposal JSON file.")
    parser.add_argument("proposal", type=Path, help="Proposal JSON file or directory")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not args.proposal.exists():
        parser.error(f"Proposal path not found: {args.proposal}")

    target = args.proposal.resolve()
    ProposalHandler.proposal_dir = target if target.is_dir() else target.parent
    ProposalHandler.initial_file = None if target.is_dir() else target.name
    if not list(ProposalHandler.proposal_dir.glob("*.json")):
        parser.error(f"No JSON proposal files found in: {ProposalHandler.proposal_dir}")
    server = ThreadingHTTPServer((args.host, args.port), ProposalHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Displaying proposals from {ProposalHandler.proposal_dir}")
    print(f"Open {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping proposal UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
