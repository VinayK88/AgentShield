from fastapi import Body, FastAPI
from fastapi.responses import HTMLResponse

from .engine import RuntimePolicyEngine
from .models import ToolCall
from .report import build_report

app = FastAPI(title="AgentShield", version="0.2.0")


def _tool_call(payload: dict) -> ToolCall:
    return ToolCall(**payload)


def evaluate_payload(payload: dict) -> dict:
    engine = RuntimePolicyEngine()
    for item in payload.get("history", []):
        engine.evaluate(_tool_call(item))
    decision = engine.evaluate(_tool_call(payload["call"]))
    return decision.__dict__


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/report")
def report():
    return build_report()


@app.post("/evaluate")
def evaluate(payload: dict = Body(...)):
    return evaluate_payload(payload)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    r = build_report()
    s = r["summary"]
    rows = "".join(
        f"<tr><td>{d['call_id']}</td><td>{d['decision']}</td><td>{d['risk_score']}</td><td>{'; '.join(d['reasons'])}</td></tr>"
        for d in r["decisions"]
    )
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AgentShield</title><style>
body{{font-family:Inter,system-ui;background:#0b1020;color:#e5e7eb;margin:0}} .wrap{{max-width:1100px;margin:auto;padding:36px}} .hero{{padding:28px;border:1px solid #24304a;border-radius:18px;background:#10182d}} .grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:20px 0}} .card{{padding:18px;border:1px solid #24304a;border-radius:14px;background:#111827}} .k{{font-size:28px;font-weight:800}} table{{width:100%;border-collapse:collapse;background:#111827;border-radius:14px;overflow:hidden}} th,td{{padding:12px;border-bottom:1px solid #24304a;text-align:left;vertical-align:top}} th{{color:#93c5fd}} .muted{{color:#9ca3af}} @media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><div class="wrap"><div class="hero"><h1>AgentShield</h1><p class="muted">Runtime security gateway for AI agents and MCP-style tool calls</p><p>Intent-aware policy, trajectory analysis, sensitive-data controls, least privilege, and human approval before tool execution.</p></div><div class="grid"><div class="card"><div class="k">{s['scenarios']}</div><div>Scenarios</div></div><div class="card"><div class="k">{s['blocked']}</div><div>Blocked</div></div><div class="card"><div class="k">{s['approval_required']}</div><div>Approval</div></div><div class="card"><div class="k">{s['redacted']}</div><div>Redacted</div></div><div class="card"><div class="k">{s['allowed']}</div><div>Allowed</div></div></div><table><thead><tr><th>Call</th><th>Decision</th><th>Risk</th><th>Why</th></tr></thead><tbody>{rows}</tbody></table></div></body></html>'''
