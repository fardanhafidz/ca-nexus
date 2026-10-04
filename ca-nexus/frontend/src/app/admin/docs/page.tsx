"use client";
import { useEffect, useState } from "react";
import SlimRail from "@/components/layout/SlimRail";
import DocTable from "@/components/knowledge/DocTable";
import { api, API, ApiError } from "@/lib/api";

type Doc = { id: string; doc_title: string; equipment_tag: string; doc_type: string; status: string; version: string; division_access: string; access_reviewed: boolean; page_count: number };
const STAGE_ORDER = ["PARSING", "VECTORIZING", "READY"];

export default function AdminDocs() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [stats, setStats] = useState<{ total_users: number; pending_users: number; total_documents: number; llm_primary: string } | null>(null);
  const [audit, setAudit] = useState<{ total: number; items: { id: string; actor: string; action: string; status: string; created_at: string }[] }>({ total: 0, items: [] });
  const [auditAction, setAuditAction] = useState("");
  const [auditPage, setAuditPage] = useState(0);
  const AUDIT_PER = 20;
  const [usage, setUsage] = useState<{
    total_answers: number; spend_30d_usd: number; budget_cap_usd: number;
    by_model: { provider: string; model: string; answers: number; failures: number; est_cost_usd: number }[];
  } | null>(null);
  const [gw, setGw] = useState<{ stored: { primary_model: string; fallback_model: string; timeout_s: number; max_retries: number } | null; effective: { primary_model: string; fallback_model: string; timeout_s: number; max_retries: number } } | null>(null);
  const [gwForm, setGwForm] = useState({ primary_model: "openai/gpt-4o", fallback_model: "anthropic/claude-sonnet-4.5", timeout_s: "45", max_retries: "1" });
  const [role, setRole] = useState("admin");
  const [jobs, setJobs] = useState<{ id: string; document_id: string; actor: string; stage: string; progress: number; total_chunks: number; error: string }[]>([]);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const loadAudit = async (action = auditAction, page = auditPage) => {
    try {
      setAudit(await api(`/api/v1/admin/audit?action=${encodeURIComponent(action)}&limit=${AUDIT_PER}&offset=${page * AUDIT_PER}`));
    } catch (e) { setErr(e instanceof ApiError ? e.message : "Audit load failed."); }
  };
  const load = async () => {
    try {
      setDocs(await api("/api/v1/admin/documents"));
      setStats(await api("/api/v1/admin/stats"));
      await loadAudit();
      try { setJobs((await api("/api/v1/admin/jobs?limit=30")).items); } catch { /* jobs optional */ }
      try { setUsage(await api("/api/v1/admin/usage?days=30")); } catch { /* admin-only */ }
      try {
        setGw(await api("/api/v1/admin/gateway"));
        setRole("super_admin");
      } catch { setRole("admin"); }  // gateway endpoint is SuperAdmin-only
    } catch (e) { setErr(e instanceof ApiError ? e.message : "Load failed."); }
  };
  useEffect(() => { load(); }, []);
  const upload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); setErr(""); setBusy(true);
    try {
      const fd = new FormData(e.currentTarget);
      const name = String((fd.get("file") as File)?.name || "");
      if (!/\.(pdf|png)$/i.test(name)) throw new ApiError(400, "Supported here: PDF, PNG. Workbook XLSX goes via seed_maintenance.");
      // Multipart: no JSON Content-Type (boundary set by browser); cookie attached
      const r = await fetch(`${API}/api/v1/admin/upload`, { method: "POST", credentials: "include", body: fd });
      if (!r.ok) throw new ApiError(r.status, await r.text());
      e.currentTarget.reset(); await load();
    } catch (ex) { setErr(ex instanceof ApiError ? ex.message : "Upload failed."); }
    setBusy(false);
  };
  return (
    <div className="flex h-screen">
      <SlimRail />
      <main className="flex-1 bg-canvas p-4 overflow-auto">
        <h1 className="font-semibold text-industrial mb-2">Ingestion Dashboard</h1>
        {stats && <p className="text-xs mb-2">Users: {stats.total_users} | Pending: {stats.pending_users} | Docs: {stats.total_documents} | LLM: {stats.llm_primary}</p>}
        {err && <p role="alert" className="text-xs text-red-600 mb-2">{err}</p>}
        <form onSubmit={upload} className="bg-white border rounded p-3 flex flex-wrap gap-2 text-sm mb-3">
          <input name="file" type="file" accept=".pdf,.png" required aria-label="Document file" />
          <input name="equipment_tag" placeholder="TAG e.g. KC-4501" aria-label="Equipment tag" className="border rounded p-1" />
          <input name="doc_type" placeholder="opl" aria-label="Document type" className="border rounded p-1" />
          <input name="division_access" placeholder="All" aria-label="Division access" className="border rounded p-1" />
          <button disabled={busy} className="bg-industrial text-white px-3 rounded disabled:opacity-50">{busy ? "Uploading..." : "Upload"}</button>
        </form>
        <DocTable docs={docs} empty="No documents yet."
          actions={(d) => (
            <>
              <span className="text-[11px] text-slate-500">{STAGE_ORDER.includes(d.status) ? `stage ${STAGE_ORDER.indexOf(d.status) + 1}/3` : d.status === "FAILED" ? "failed — re-upload to retry" : ""}</span>
              {d.status !== "ARCHIVED" && (
                <>
                  <button onClick={async () => { setErr(""); try { await api(`/api/v1/admin/documents/${d.id}/archive`, { method: "POST" }); await load(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Archive failed."); } }}
                    className="text-xs border rounded px-1.5 py-0.5">Archive</button>
                  <button onClick={async () => { if (!confirm(`Delete ${d.doc_title} and its index points?`)) return; setErr(""); try { await api(`/api/v1/admin/documents/${d.id}/delete`, { method: "POST" }); await load(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Delete failed."); } }}
                    className="text-xs border border-red-300 text-red-600 rounded px-1.5 py-0.5">Delete</button>
                </>
              )}
            </>
          )} />
        <h2 className="font-semibold text-sm mb-1">Ingestion jobs</h2>
        <div className="bg-white border rounded mb-3">
          {jobs.map((j) => (
            <div key={j.id} className="p-2 border-b text-xs flex gap-2 items-center flex-wrap">
              <span className="flex-1 min-w-[160px]">{j.document_id.slice(0, 8)}… — {j.stage} {j.progress}%{j.total_chunks ? ` (${j.total_chunks} chunks)` : ""}{j.error ? ` — ${j.error.slice(0, 120)}` : ""}</span>
              <span className="w-24 h-2 bg-canvas rounded overflow-hidden" role="progressbar" aria-valuenow={j.progress} aria-valuemin={0} aria-valuemax={100}>
                <span className="block h-full bg-industrial" style={{ width: `${j.progress}%` }} />
              </span>
              {(j.stage === "FAILED" || j.stage === "CANCELLED") && (
                <button onClick={async () => { setErr(""); try { await api(`/api/v1/admin/jobs/${j.id}/retry`, { method: "POST" }); await load(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Retry failed."); } }}
                  className="text-xs border rounded px-1.5 py-0.5">Retry</button>
              )}
              {!["READY", "FAILED", "CANCELLED"].includes(j.stage) && (
                <button onClick={async () => { setErr(""); try { await api(`/api/v1/admin/jobs/${j.id}/cancel`, { method: "POST" }); await load(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Cancel failed."); } }}
                  className="text-xs border rounded px-1.5 py-0.5">Cancel</button>
              )}
            </div>
          ))}
          {jobs.length === 0 && <p className="p-2 text-xs text-slate-500">No jobs yet.</p>}
        </div>
        {usage && (
          <>
            <h2 className="font-semibold text-sm mb-1">Usage last 30 days ({usage.total_answers} answers)</h2>            <p className="text-xs text-slate-500 mb-1">
              Spend est. ${usage.spend_30d_usd}{usage.budget_cap_usd > 0 ? ` of $${usage.budget_cap_usd} cap (LLM stops at cap; SQL/extractive keep working)` : " (no cap set — BUDGET_USD_CAP)"}
            </p>
            <div className="bg-white border rounded mb-3">
              {usage.by_model.map((m) => (
                <div key={`${m.provider}/${m.model}`} className="p-1.5 border-b text-xs">
                  {m.provider}/{m.model}: {m.answers} answers, {m.failures} failures, est. ${m.est_cost_usd} (rates: docs/PRICING.md)
                </div>
              ))}
              {usage.by_model.length === 0 && <p className="p-2 text-xs text-slate-500">No usage recorded.</p>}
            </div>
          </>
        )}
        {role === "super_admin" && gw && (
          <>
            <h2 className="font-semibold text-sm mb-1">Gateway config (SuperAdmin — keys stay in environment)</h2>
            <p className="text-[11px] text-slate-500 mb-1">Effective: {gw.effective.primary_model} / {gw.effective.fallback_model}, timeout {gw.effective.timeout_s}s, retries {gw.effective.max_retries}</p>
            <form className="bg-white border rounded p-2 flex flex-wrap gap-2 text-sm mb-3"
              onSubmit={async (e) => {
                e.preventDefault(); setErr("");
                try {
                  await api("/api/v1/admin/gateway", {
                    method: "PUT",
                    body: JSON.stringify({ ...gwForm, timeout_s: Number(gwForm.timeout_s), max_retries: Number(gwForm.max_retries) }),
                  });
                  await load();
                } catch (ex) { setErr(ex instanceof ApiError ? ex.message : "Gateway update failed."); }
              }}>
              <input value={gwForm.primary_model} onChange={(e) => setGwForm({ ...gwForm, primary_model: e.target.value })} aria-label="Primary model" className="border rounded p-1" />
              <input value={gwForm.fallback_model} onChange={(e) => setGwForm({ ...gwForm, fallback_model: e.target.value })} aria-label="Fallback model" className="border rounded p-1" />
              <input value={gwForm.timeout_s} onChange={(e) => setGwForm({ ...gwForm, timeout_s: e.target.value })} aria-label="Timeout seconds" className="border rounded p-1 w-24" />
              <input value={gwForm.max_retries} onChange={(e) => setGwForm({ ...gwForm, max_retries: e.target.value })} aria-label="Max retries" className="border rounded p-1 w-24" />
              <button className="bg-industrial text-white px-2 rounded text-xs">Apply</button>
            </form>
          </>
        )}
        <h2 className="font-semibold text-sm mb-1">Audit trail ({audit.total})</h2>
        <div className="flex gap-2 mb-1 text-sm">
          <input value={auditAction} onChange={(e) => setAuditAction(e.target.value)}
            placeholder="Filter action e.g. chat.ask" aria-label="Filter audit by action"
            className="border rounded p-1.5 text-sm flex-1" />
          <button onClick={() => { setAuditPage(0); loadAudit(auditAction, 0); }} className="bg-industrial text-white px-2 rounded text-xs">Filter</button>
        </div>
        <div className="bg-white border rounded">
          {audit.items.map((a) => <div key={a.id} className="p-1.5 border-b text-xs">{a.created_at} — {a.actor} — {a.action} [{a.status}]</div>)}
          {audit.items.length === 0 && <p className="p-2 text-xs text-slate-500">No audit events.</p>}
        </div>
        <div className="flex gap-2 mt-1 text-sm">
          <button disabled={auditPage <= 0} onClick={() => { const p = auditPage - 1; setAuditPage(p); loadAudit(auditAction, p); }} className="border rounded px-2 py-1 disabled:opacity-50">Prev</button>
          <button disabled={(auditPage + 1) * AUDIT_PER >= audit.total} onClick={() => { const p = auditPage + 1; setAuditPage(p); loadAudit(auditAction, p); }} className="border rounded px-2 py-1 disabled:opacity-50">Next</button>
        </div>
      </main>
    </div>
  );
}
