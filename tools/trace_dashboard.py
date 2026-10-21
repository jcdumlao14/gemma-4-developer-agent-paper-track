from __future__ import annotations

import json
import os
import re
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = int(os.environ.get("TRACE_DASHBOARD_PORT", "8765"))
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "workspaces"}
MAX_REPORT_BYTES = 2_000_000

HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#090e1d"><title>TRACE | Evidence Command Center</title>
<style>
:root{--bg:#090e1d;--panel:#10192c;--panel2:#131f35;--line:#293754;--text:#edf3ff;--muted:#9aabc6;--teal:#54e0c1;--blue:#81adff;--purple:#c0a5ff;--amber:#ffd18b;--red:#ff9aaa;--green:#82e6ae}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 8% -15%,#1c3458 0,transparent 42%),radial-gradient(ellipse at 100% 0,#30204b 0,transparent 28%),var(--bg);color:var(--text);font:14px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}.wrap{max-width:1500px;margin:auto;padding:26px 24px 45px}.top{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:22px}.brand{display:flex;align-items:center;gap:13px}.logo{width:47px;height:47px;border-radius:15px;background:linear-gradient(140deg,var(--teal),#7898ff 62%,var(--purple));display:grid;place-items:center;color:#081324;font-weight:950;font-size:23px;box-shadow:0 8px 35px #54e0c12b}.eyebrow{text-transform:uppercase;letter-spacing:.18em;color:var(--teal);font-size:10px;font-weight:850}.title{font-size:24px;letter-spacing:-.045em;font-weight:850;margin:0}.subtitle{color:var(--muted);margin-top:3px;font-size:12px}.topright{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.pill{border:1px solid var(--line);border-radius:999px;padding:7px 11px;color:var(--muted);font-size:11px;background:#0d1526}.live{display:inline-block;width:7px;height:7px;background:var(--green);border-radius:50%;margin-right:7px;box-shadow:0 0 10px #82e6ae}.hero{display:grid;grid-template-columns:1.5fr .8fr;gap:16px}.hero-main,.hero-side,.panel,.metric{border:1px solid var(--line);background:linear-gradient(145deg,#131e34f5,#0f1729f5);border-radius:19px;box-shadow:0 16px 50px #0002}.hero-main{padding:25px;position:relative;overflow:hidden}.hero-main:after{content:"TRACE";position:absolute;right:10px;bottom:-39px;font-size:116px;font-weight:950;letter-spacing:-.1em;color:#fff06;pointer-events:none}.hero h2{font-size:clamp(25px,3vw,38px);letter-spacing:-.055em;line-height:1.12;margin:11px 0}.hero p{max-width:730px;color:#b3c1d8;margin:0}.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:19px}.chip{border-radius:8px;padding:6px 9px;font-size:11px;font-weight:750;border:1px solid #29465a;background:#112b37;color:var(--teal)}.chip.purple{border-color:#433a66;background:#211d3b;color:var(--purple)}.chip.amber{border-color:#665039;background:#30271c;color:var(--amber)}.hero-side{padding:21px;display:flex;flex-direction:column;justify-content:space-between;gap:17px}.side-label{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.14em}.progress-title{display:flex;justify-content:space-between;gap:10px;font-weight:750;margin:8px 0}.bar{height:8px;background:#25324b;border-radius:20px;overflow:hidden}.bar span{display:block;height:100%;border-radius:20px;background:linear-gradient(90deg,var(--teal),var(--blue));width:75%}.side-note{color:var(--muted);font-size:11px;margin-top:8px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0}.metric{padding:17px 18px}.metric-top{display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:11px}.metric-icon{width:29px;height:29px;border-radius:9px;display:grid;place-items:center;background:#1c2a42;color:var(--teal);font-size:15px}.number{font-size:29px;font-weight:850;letter-spacing:-.045em;margin:9px 0 1px}.metric-foot{font-size:10px;color:var(--muted)}.layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(300px,.75fr);gap:16px;margin-top:16px}.panel{padding:19px;min-width:0}.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;margin-bottom:15px}.panel h3{margin:0;font-size:15px;letter-spacing:-.025em}.panel-desc{font-size:11px;color:var(--muted);margin-top:4px}.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:13px}input,select{background:#0a1222;border:1px solid #2a3955;color:var(--text);border-radius:10px;padding:10px 12px;outline:none;font:inherit;font-size:12px}input{min-width:180px;flex:1}input:focus,select:focus{border-color:var(--teal);box-shadow:0 0 0 3px #54e0c11c}.btn{border:1px solid #334360;background:#18243a;color:#e4ecfa;border-radius:9px;padding:8px 11px;font-weight:750;font-size:11px;cursor:pointer}.btn:hover{border-color:var(--teal);color:var(--teal)}.cases{display:grid;gap:10px}.case{border:1px solid var(--line);background:#0c1425;border-radius:14px;padding:14px;transition:border-color .2s,transform .2s}.case:hover{border-color:#536c91;transform:translateY(-1px)}.case-row{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.case-title{font-size:13px;font-weight:850}.case-repo{font-size:10px;color:var(--muted);margin-top:3px;overflow-wrap:anywhere}.badge{display:inline-flex;align-items:center;white-space:nowrap;border-radius:999px;padding:4px 8px;font-size:10px;font-weight:800;background:#153329;color:var(--green);border:1px solid #285a49}.badge.info{background:#182847;color:var(--blue);border-color:#304c7d}.badge.warn{background:#352919;color:var(--amber);border-color:#604b2c}.case-bottom{display:flex;gap:6px;flex-wrap:wrap;margin-top:11px}.mini{font-size:10px;padding:4px 7px;border:1px solid #293750;color:#aab9d1;border-radius:6px}.details{margin-top:11px;padding-top:10px;border-top:1px solid #202d45;color:#b8c5da;font-size:10px;display:grid;grid-template-columns:1fr 1fr;gap:9px}.detail strong{display:block;color:#f0f4ff;font-size:11px;margin-top:2px;font-weight:750}.empty{padding:27px;text-align:center;color:var(--muted);border:1px dashed var(--line);border-radius:12px}.stack{display:grid;gap:16px;align-content:start}.legend{display:grid;gap:12px}.legend-row{display:flex;align-items:center;gap:9px}.dot{width:9px;height:9px;border-radius:3px;background:var(--teal);flex-shrink:0}.legend-text{flex:1;color:#c4cee0;font-size:11px}.legend-num{font-weight:850;font-size:12px}.barline{height:5px;background:#26334b;border-radius:20px;margin-top:5px;overflow:hidden}.barline span{display:block;height:100%;border-radius:20px;background:var(--teal)}.note{background:#171c30;border:1px solid #3d365f;border-radius:12px;padding:12px;color:#c7c4e9;font-size:11px}.note strong{color:#e5dcff}.sources{display:grid;gap:8px}.source{display:flex;gap:9px;align-items:flex-start;padding:9px 0;border-bottom:1px solid #202d45}.source:last-child{border-bottom:0}.fileicon{width:27px;height:31px;border:1px solid #30415e;border-radius:6px;display:grid;place-items:center;color:var(--blue);font-size:9px;flex-shrink:0}.source-name{font-size:11px;font-weight:750;overflow-wrap:anywhere}.source-path{font-size:10px;color:var(--muted);overflow-wrap:anywhere;margin-top:3px}.footer{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;color:#71819e;font-size:10px;margin-top:20px;padding:0 3px}.error{border:1px solid #6c3946;background:#2b1723;color:#ffc3cd;padding:12px;border-radius:12px;margin-bottom:13px;font-size:12px;display:none}.tiny{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em}.timeline{display:grid;gap:12px}.timeitem{display:grid;grid-template-columns:13px 1fr;gap:10px}.rail{position:relative;display:flex;justify-content:center}.rail:after{content:"";position:absolute;top:12px;bottom:-15px;width:1px;background:#2d3b56}.timeitem:last-child .rail:after{display:none}.time-dot{width:9px;height:9px;border-radius:50%;background:var(--teal);margin-top:5px;z-index:1;box-shadow:0 0 0 4px #54e0c11c}.timeitem:nth-child(2) .time-dot{background:var(--purple)}.timeitem:nth-child(3) .time-dot{background:var(--amber)}.timeitem:nth-child(4) .time-dot{background:var(--blue)}.time-title{font-weight:750;font-size:11px}.time-desc{color:var(--muted);font-size:10px;margin-top:2px}.file-list{max-height:300px;overflow:auto}.smallprint{font-size:10px;color:var(--muted);margin-top:10px}@media(max-width:980px){.hero{grid-template-columns:1fr}.layout{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}}@media(max-width:580px){.wrap{padding:16px 11px 30px}.top{align-items:flex-start}.topright{display:none}.title{font-size:20px}.hero-main{padding:19px}.hero-side{padding:17px}.metrics{gap:7px}.metric{padding:12px}.number{font-size:24px}.panel{padding:13px}.details{grid-template-columns:1fr 1fr}.case-row{flex-direction:column}.badge{white-space:normal}}
</style></head><body><div class="wrap">
<header class="top"><div class="brand"><div class="logo">T</div><div><div class="eyebrow">Research operations</div><h1 class="title">TRACE Evidence Command Center</h1><div class="subtitle">Test-guided repository exploration  |  evidence-grounded repair</div></div></div><div class="topright"><a class="pill" href="/methodology" target="_blank" rel="noopener noreferrer" style="text-decoration:none;color:inherit">Methodology / README</a><div class="pill"><span class="live"></span>Local  |  read-only</div><div class="pill" id="updated">Loading reports…</div></div></header>
<div id="error" class="error"></div>
<section class="hero"><div class="hero-main"><div class="eyebrow">Pilot overview  |  research workspace</div><h2>Every repair claim.<br>Grounded in evidence.</h2><p>Explore historical pilot records, candidate provenance, regression checks, source restoration, and local model-proposal artifacts in one place. TRACE separates what was proposed, what was tested, and what the evidence actually supports.</p><div class="chips"><span class="chip">Evidence first</span><span class="chip purple">Regression aware</span><span class="chip amber">No automatic patching</span></div></div><div class="hero-side"><div><div class="side-label">Implementation status</div><div class="progress-title"><span>Local quality checks</span><span id="readiness">Report-driven</span></div><div class="bar"><span id="readinessBar"></span></div><div class="side-note">The bar summarizes the recorded local-check report only. It is not a benchmark score or research-completion percentage.</div></div><div><div class="side-label">Study scope</div><div class="side-note">Four-case pilot  |  controlled baseline comparison not complete  |  no benchmark-wide effectiveness claim.</div></div></div></section>
<section class="metrics"><div class="metric"><div class="metric-top"><span>Unique pilot issues</span><span class="metric-icon">ID</span></div><div class="number" id="mIssues">—</div><div class="metric-foot">From project evidence summary</div></div><div class="metric"><div class="metric-top"><span>Evidence JSON files</span><span class="metric-icon">Files</span></div><div class="number" id="mReports">—</div><div class="metric-foot">Relevant report files discovered locally</div></div><div class="metric"><div class="metric-top"><span>Proposal artifacts</span><span class="metric-icon" style="position:relative;left:-24px;width:auto;min-width:29px;padding:0 8px;white-space:nowrap">Proposals</span></div><div class="number" id="mProposals">—</div><div class="metric-foot">Proposal/smoke reports found</div></div><div class="metric"><div class="metric-top"><span>Baseline comparison</span><span class="metric-icon" style="position:relative;left:-20px;width:auto;min-width:29px;padding:0 8px;white-space:nowrap">Baseline</span></div><div class="number" style="color:var(--amber);font-size:22px">Not complete</div><div class="metric-foot">As recorded in finalization report</div></div></section>
<div class="layout"><main class="panel"><div class="panel-head"><div><h3>Evidence explorer</h3><div class="panel-desc">Search local report files and filter by case or evidence type.</div></div><button class="btn" id="refresh">Refresh Refresh</button></div><div class="filters"><input id="search" placeholder="Search issue, report, result, provenance…" aria-label="Search evidence"><select id="kind"><option value="all">All evidence types</option><option value="pilot">Pilot / validation</option><option value="proposal">Model proposal / smoke</option><option value="audit">Audit / finalization</option></select></div><div id="count" class="tiny" style="margin-bottom:10px">Discovering report files…</div><div id="records" class="cases"><div class="empty">Loading local evidence…</div></div></main>
<aside class="stack"><section class="panel"><div class="panel-head"><div><h3>Pilot interpretation</h3><div class="panel-desc">Attribution and validation are not interchangeable.</div></div></div><div class="timeline"><div class="timeitem"><div class="rail"><span class="time-dot"></span></div><div><div class="time-title">SQLFluff  |  1733</div><div class="time-desc">Successful candidate came from subsequent rule-isolation investigation, not a successful original Gemma repair.</div></div></div><div class="timeitem"><div class="rail"><span class="time-dot"></span></div><div><div class="time-title">SQLFluff  |  1625</div><div class="time-desc">Gemma candidate was guided by diagnostic wording; avoid describing it as unprompted discovery.</div></div></div><div class="timeitem"><div class="rail"><span class="time-dot"></span></div><div><div class="time-title">Marshmallow  |  1343</div><div class="time-desc">Model proposal and later candidate validation are separate stages; do not imply the adapter ran tests.</div></div></div><div class="timeitem"><div class="rail"><span class="time-dot"></span></div><div><div class="time-title">Marshmallow  |  1359</div><div class="time-desc">Initial candidate failed relationship controls; refined candidate passed recorded checks and source was restored.</div></div></div></div></section>
<section class="panel"><div class="panel-head"><div><h3>Integrity guardrails</h3><div class="panel-desc">Keep the dashboard honest.</div></div></div><div class="note"><strong>Recorded pass is not equal to reproduced benchmark.</strong><br>Dashboard counts describe available files, not independently rerun tests.</div><div class="note" style="margin-top:9px"><strong>Proposal is not equal to applied patch.</strong><br>TRACE's proposal workflow does not automatically apply diffs or execute target-repository commands.</div><div class="note" style="margin-top:9px"><strong>Missing fields stay missing.</strong><br>When a report does not provide a value, the dashboard labels it as not recorded instead of guessing.</div></section>
<section class="panel"><div class="panel-head"><div><h3>Discovered report files</h3><div class="panel-desc">Filtered, bounded local JSON inventory.</div></div></div><div id="sources" class="sources file-list"></div><div class="smallprint">Hidden environments, Git internals, caches, and workspace virtual environments are excluded.</div></section></aside></div>
<footer class="footer"><span>TRACE  |  Local research dashboard  |  Read-only evidence viewer</span><span id="foot">Waiting for reports</span></footer></div>
<script>
let DATA=null;const $=id=>document.getElementById(id);function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}function shortPath(p){return p.length>100?'…'+p.slice(-97):p}function badge(t,c='info'){return `<span class="badge ${c}">${esc(t)}</span>`}function render(){if(!DATA)return;const items=DATA.reports||[];$('mIssues').textContent=DATA.uniqueIssues;$('mReports').textContent=items.length;$('mProposals').textContent=DATA.proposalCount;$('readiness').textContent=DATA.localChecks?'Local checks passed':'Needs review';$('readinessBar').style.width=DATA.localChecks?'82%':'42%';$('updated').textContent='Refreshed '+new Date(DATA.generatedAt).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});$('foot').textContent=`${items.length} report files  |  ${DATA.skippedLarge} large/unreadable files skipped`;const q=$('search').value.toLowerCase().trim(),k=$('kind').value;const visible=items.filter(x=>{if(q&&!(`${x.path} ${x.name} ${x.preview} ${x.caseId||''}`).toLowerCase().includes(q))return false;if(k==='pilot'&&!x.pilot)return false;if(k==='proposal'&&!x.proposal)return false;if(k==='audit'&&!x.audit)return false;return true;});$('count').textContent=`SHOWING ${visible.length} OF ${items.length} REPORT FILES`; $('records').innerHTML=visible.length?visible.map(x=>`<article class="case"><div class="case-row"><div><div class="case-title">${esc(x.name)}</div><div class="case-repo">${esc(x.caseId||'Project report')}  |  ${esc(x.path)}</div></div>${badge(x.type,x.proposal?'warn':x.audit?'info':'')}</div><div class="case-bottom">${x.pilot?'<span class="mini">Pilot evidence</span>':''}${x.proposal?'<span class="mini">Proposal / smoke</span>':''}${x.audit?'<span class="mini">Audit / finalization</span>':''}<span class="mini">${esc(x.bytesLabel)}</span></div><div class="details"><div class="detail">Detected outcome<strong>${esc(x.outcome||'Not recorded')}</strong></div><div class="detail">Test / validation fields<strong>${esc(x.testSummary||'Not recorded')}</strong></div><div class="detail">Model / candidate fields<strong>${esc(x.modelSummary||'Not recorded')}</strong></div><div class="detail">Report timestamp<strong>${esc(x.timestamp||'Not recorded')}</strong></div></div><div class="source-path">Preview: ${esc(x.preview||'No text preview')}</div></article>`).join(''):'<div class="empty">No reports match your search or filter.</div>';$('sources').innerHTML=visible.slice(0,80).map(x=>`<div class="source"><div class="fileicon">JSON</div><div><div class="source-name">${esc(x.name)}</div><div class="source-path">${esc(shortPath(x.path))}</div></div></div>`).join('')||'<div class="empty">No report files found yet.</div>';}async function load(){$('refresh').disabled=true;$('refresh').textContent='Loading…';try{const r=await fetch('/api/data',{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);DATA=await r.json();$('error').style.display='none';render()}catch(e){$('error').style.display='block';$('error').textContent='Could not read local report inventory: '+e.message}finally{$('refresh').disabled=false;$('refresh').textContent='Refresh Refresh'}}$('refresh').addEventListener('click',load);$('search').addEventListener('input',render);$('kind').addEventListener('change',render);load();
</script></body></html>'''


def iter_report_files():
    results = ROOT / "experiments" / "results"
    if not results.exists():
        return
    for base, dirs, files in os.walk(results):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.lower().startswith(".venv")]
        for name in files:
            if not name.lower().endswith(".json"):
                continue
            path = Path(base) / name
            try:
                if path.stat().st_size > MAX_REPORT_BYTES:
                    continue
            except OSError:
                continue
            yield path


def walk_values(obj, prefix=""):
    """Return a bounded set of scalar JSON fields for safe display summaries."""
    out = []
    if isinstance(obj, dict):
        for k, v in list(obj.items())[:120]:
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (str, int, float, bool)) or v is None:
                out.append((key, v))
            elif isinstance(v, (dict, list)):
                out.extend(walk_values(v, key))
            if len(out) >= 500:
                break
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:100]):
            out.extend(walk_values(v, f"{prefix}[{i}]"))
            if len(out) >= 500:
                break
    return out


def summarize(path: Path, data: object) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    name = path.name
    low = (rel + " " + name).lower()
    vals = walk_values(data)
    scalar = {k.lower(): v for k, v in vals}
    strings = [str(v) for _, v in vals if isinstance(v, (str, int, float, bool))]
    compact = "  |  ".join(re.sub(r"\s+", " ", s).strip() for s in strings if s and len(str(s)) < 130)[:380]
    proposal = any(t in low for t in ("proposal", "smoke", "model_adapter")) or any("model_invoked" in k and v is True for k, v in scalar.items())
    audit = any(t in low for t in ("audit", "finalization", "milestone", "reconcile"))
    pilot = any(t in low for t in ("sqlfluff", "marshmallow", "pilot", "case_record", "validation")) and not proposal
    issue = None
    match = re.search(r"(sqlfluff|marshmallow)[^/\\]*?(?:-|_)(1733|1625|1343|1359)", low)
    if match:
        issue = f"{match.group(1).title()} #{match.group(2)}"
    elif "1733" in low:
        issue = "SQLFluff #1733"
    elif "1625" in low:
        issue = "SQLFluff #1625"
    elif "1343" in low:
        issue = "Marshmallow #1343"
    elif "1359" in low:
        issue = "Marshmallow #1359"
    # Use exact field names rather than broad substring matching.
    outcome = None
    outcome_keys = {"status", "outcome", "final_status", "overall_status", "validation_status"}
    for key, value in vals:
        terminal = key.rsplit(".", 1)[-1].lower()
        if terminal in outcome_keys and isinstance(value, str) and value.strip():
            outcome = value.strip()
            break

    # Show test evidence, not unrelated patch-audit exit codes.
    tests = []
    test_keys = {
        "passed", "suite_passed", "tests_passed", "test_count",
        "tests_passed_count", "target_test", "control_test",
        "exit_code", "full_marshalling_module"
    }
    for key, value in vals:
        kl = key.lower()
        terminal = kl.rsplit(".", 1)[-1]
        is_test_field = (
            terminal in test_keys
            and (
                "test" in kl
                or "suite" in kl
                or "validation" in kl
                or (terminal == "exit_code" and any(
                    marker in kl for marker in (
                        ".tests.", ".target.", ".control.",
                        "full_suite", "full_marshalling_module"
                    )
                ))
            )
        )
        if is_test_field and isinstance(value, (str, int, float, bool)):
            tests.append(f"{key.rsplit('.', 1)[-1]}={value}")
        if len(tests) >= 4:
            break

    models = []
    for key, value in vals:
        kl = key.lower()
        terminal = kl.rsplit(".", 1)[-1]
        if (
            any(word in terminal for word in (
                "model", "candidate", "patch_applied",
                "repair_verified", "source_restored"
            ))
            and isinstance(value, (str, int, float, bool))
        ):
            models.append(f"{terminal}={value}")
        if len(models) >= 4:
            break

    # Accept only known timestamp field names with parseable ISO date/time values.
    timestamp = None
    timestamp_keys = {
        "generated_at", "generated_at_utc", "timestamp",
        "timestamp_utc", "created_at", "created_at_utc"
    }
    for key, value in vals:
        terminal = key.rsplit(".", 1)[-1].lower()
        if terminal not in timestamp_keys or not isinstance(value, str):
            continue
        candidate_time = value.strip()
        try:
            datetime.fromisoformat(candidate_time.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        timestamp = candidate_time
        break

    # Keep field names in the preview so values remain interpretable.
    preview_items = []
    for key, value in vals:
        if value is None or not isinstance(value, (str, int, float, bool)):
            continue
        value_text = re.sub(r"\s+", " ", str(value)).strip()
        if not value_text or len(value_text) >= 130:
            continue
        field_name = key.rsplit(".", 1)[-1]
        preview_items.append(f"{field_name}={value_text}")
        if len(preview_items) >= 12:
            break
    compact = " | ".join(preview_items)[:380]
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return {"path": rel, "name": name, "caseId": issue, "proposal": proposal, "audit": audit,
            "pilot": pilot, "type": "Proposal / smoke" if proposal else "Audit / finalization" if audit else "Pilot / validation" if pilot else "Research report",
            "outcome": outcome, "testSummary": "; ".join(tests) or None,
            "modelSummary": "; ".join(models) or None, "timestamp": timestamp,
            "preview": compact, "bytesLabel": f"{size:,} bytes"}


def read_data():
    reports = []
    skipped_large = 0
    results_dir = ROOT / "experiments" / "results"
    if results_dir.exists():
        for path in iter_report_files() or []:
            try:
                raw = path.read_text(encoding="utf-8-sig")
                data = json.loads(raw)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                skipped_large += 1
                continue
            reports.append(summarize(path, data))
    reports.sort(key=lambda x: (not x["audit"], not x["proposal"], x["path"].lower()))
    unique_issues = {r["caseId"] for r in reports if r["caseId"]}
    final = None
    for r in reports:
        if r["name"].lower() == "trace_finalization_report.json":
            try:
                final = json.loads((ROOT / r["path"]).read_text(encoding="utf-8-sig"))
            except Exception:
                pass
    local_checks = isinstance(final, dict) and final.get("status") == "local_checks_passed"
    proposal_count = sum(1 for r in reports if r["proposal"])
    return {"generatedAt": datetime.now().astimezone().isoformat(), "reports": reports,
            "uniqueIssues": len(unique_issues), "proposalCount": proposal_count,
            "localChecks": local_checks, "skippedLarge": skipped_large}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/data":
            body = json.dumps(read_data(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif route in ("/", "/index.html"):
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif route == "/methodology":
            doc_path = Path(__file__).resolve().with_name("TRACE_DASHBOARD_README.md")
            if not doc_path.is_file():
                self.send_error(404, "Methodology README not found")
                return
            body = doc_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not found")

    def log_message(self, fmt, *args):
        print("[TRACE dashboard] " + (fmt % args))


def main():
    if not (ROOT / "pyproject.toml").exists():
        raise SystemExit(f"TRACE project root not found: {ROOT}")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print("\nTRACE Evidence Command Center")
    print(f"Project:   {ROOT}")
    print(f"Dashboard: {url}")
    print("Mode:      local read-only; no dependencies; no patch/test/commit actions")
    print("Stop with Ctrl+C.\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping TRACE dashboard.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
