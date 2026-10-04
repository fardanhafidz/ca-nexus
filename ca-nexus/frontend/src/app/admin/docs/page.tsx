"use client";
import { useEffect, useState, useRef } from "react";
import AppSidebar from "@/components/layout/AppSidebar";
import DocTable from "@/components/knowledge/DocTable";
import { api, API, ApiError } from "@/lib/api";
import { CloudUpload, ChevronRight, HelpCircle, FileText, FileImage, FileSpreadsheet, CheckCircle2, CircleDashed } from "lucide-react";

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
  const [fileName, setFileName] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const upload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); setErr(""); setBusy(true);
    try {
      const fd = new FormData(e.currentTarget);
      const name = String((fd.get("file") as File)?.name || "");
      if (!/\.(pdf|png)$/i.test(name)) throw new ApiError(400, "Supported here: PDF, PNG.");
      const r = await fetch(`${API}/api/v1/admin/upload`, { method: "POST", credentials: "include", body: fd });
      if (!r.ok) throw new ApiError(r.status, await r.text());
      e.currentTarget.reset(); setFileName(""); await load();
    } catch (ex) { setErr(ex instanceof ApiError ? ex.message : "Upload failed."); }
    setBusy(false);
  };
  return (
    <div className="flex h-screen w-full bg-canvas">
      <AppSidebar />
      <main className="flex-1 flex flex-col bg-canvas min-w-0 overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-line px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">CA Nexus</span>
            <ChevronRight size={14} className="text-slate-400" />
            <span className="font-semibold text-slate-800">Ingestion Pipeline</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 border border-emerald-100 rounded-full text-emerald-700 text-xs font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.5)]"></span>
              Node #04 Active
            </div>
            <button className="text-slate-400 hover:text-slate-700 transition-colors"><HelpCircle size={20} /></button>
            <div className="w-8 h-8 rounded-full bg-slate-200 overflow-hidden shadow-sm flex items-center justify-center font-bold text-slate-500 text-xs">
              AD
            </div>
          </div>
        </header>

        <div className="p-8 max-w-5xl mx-auto w-full space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight mb-2">Ingestion Pipeline</h1>
            <p className="text-slate-500 text-base">Upload and process factory schematics, SOPs, and compliance manuals</p>
          </div>

          {err && <div role="alert" className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl shadow-sm text-sm">{err}</div>}

          {/* Upload Form styled as Drop Zone */}
          <form onSubmit={upload} className="bg-white border border-line rounded-2xl p-6 shadow-sm flex flex-col">
            <div 
              className="border-2 border-dashed border-line rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors flex flex-col items-center justify-center p-12 cursor-pointer relative"
              onClick={() => fileInputRef.current?.click()}
            >
              <input ref={fileInputRef} name="file" type="file" accept=".pdf,.png" required className="hidden" onChange={(e) => setFileName(e.target.files?.[0]?.name || "")} />
              <div className="w-16 h-16 bg-cyan-50 text-cyan-600 rounded-full flex items-center justify-center mb-4">
                <CloudUpload size={32} />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-1">
                {fileName ? fileName : "Upload SOPs, P&IDs, or Factory Manuals"}
              </h3>
              <p className="text-slate-500 text-sm mb-4">Supported: PDF, PNG (up to 250MB)</p>
              <button type="button" className="px-5 py-2 bg-white border border-line rounded-full text-sm font-medium text-slate-700 shadow-sm hover:border-slate-300">
                Browse Files
              </button>
            </div>

            <div className="flex items-end justify-between mt-6 gap-4">
              <div className="flex gap-4 flex-1">
                <div className="flex-1">
                  <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Target Division</label>
                  <select name="division_access" className="w-full border border-line rounded-lg p-2.5 text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-industrial/20" defaultValue="QA/QC Division">
                    <option value="QA/QC Division">QA/QC Division</option>
                    <option value="Plant Maintenance">Plant Maintenance</option>
                    <option value="Line 2 Engineering">Line 2 Engineering</option>
                    <option value="All">All Divisions</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Equipment Tag (Opt)</label>
                  <input name="equipment_tag" placeholder="e.g. KC-4501" className="w-full border border-line rounded-lg p-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-industrial/20" />
                </div>
                <div className="flex-1">
                  <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">Doc Type</label>
                  <input name="doc_type" placeholder="e.g. opl, sop" defaultValue="opl" className="w-full border border-line rounded-lg p-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-industrial/20" />
                </div>
              </div>
              <button disabled={busy || !fileName} className="bg-industrial hover:bg-industrial-dark text-white px-6 py-2.5 rounded-lg font-semibold text-sm shadow-md transition-colors disabled:opacity-50 shrink-0 flex items-center gap-2">
                <CloudUpload size={18} /> {busy ? "Uploading..." : "Upload & Ingest"}
              </button>
            </div>
          </form>

          {/* Jobs List styled to match design */}
          <div className="bg-white border border-line rounded-2xl shadow-sm overflow-hidden">
            <div className="flex items-center justify-between p-5 border-b border-line bg-slate-50/50">
              <h2 className="text-lg font-bold text-slate-900">Recent Ingestion Tasks</h2>
              <span className="text-xs font-medium text-slate-400 flex items-center gap-1"><CircleDashed size={14} className="animate-spin" /> Auto-refreshing</span>
            </div>
            <div className="divide-y divide-line">
              {jobs.map((j) => {
                const isReady = j.stage === "READY";
                const isFail = j.stage === "FAILED" || j.stage === "CANCELLED";
                const Icon = isReady ? FileText : isFail ? FileImage : FileSpreadsheet;
                
                return (
                  <div key={j.id} className="p-5 flex items-center gap-5 hover:bg-slate-50 transition-colors">
                    <div className="w-12 h-12 rounded-xl bg-cyan-50 text-cyan-600 flex items-center justify-center shrink-0 border border-cyan-100">
                      <Icon size={24} className={isReady ? "text-emerald-500" : "text-industrial"} />
                    </div>
                    <div className="w-48 shrink-0">
                      <p className="font-semibold text-slate-900 text-sm truncate">{j.document_id}</p>
                      <p className="text-xs text-slate-500 truncate">Stage: {j.stage}</p>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs font-medium text-industrial">{isReady ? "Completed" : isFail ? j.error?.slice(0,40) || "Failed" : `Processing: ${j.stage}`}</span>
                        <span className="text-xs font-semibold text-slate-500">{j.progress}%</span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all duration-500 ${isReady ? 'bg-emerald-500' : isFail ? 'bg-red-500' : 'bg-industrial'}`} style={{ width: `${j.progress}%` }} />
                      </div>
                    </div>
                    <div className="w-32 shrink-0 flex justify-end">
                      {isReady ? (
                        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 border border-emerald-100 rounded-full text-emerald-700 text-xs font-semibold">
                          <CheckCircle2 size={14} /> Synced & Ready
                        </div>
                      ) : isFail ? (
                        <button onClick={async () => { setErr(""); try { await api(`/api/v1/admin/jobs/${j.id}/retry`, { method: "POST" }); await load(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Retry failed."); } }}
                          className="px-4 py-1.5 bg-white border border-line rounded-full text-xs font-semibold text-slate-700 shadow-sm hover:border-slate-300">Retry</button>
                      ) : (
                        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-50 border border-cyan-100 rounded-full text-industrial text-xs font-semibold">
                          <span className="w-1.5 h-1.5 rounded-full bg-industrial shadow-[0_0_4px_rgba(14,115,153,0.5)] animate-pulse"></span> Processing
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
              {jobs.length === 0 && <div className="p-8 text-center text-sm text-slate-500">No jobs yet. Upload a document to start ingestion.</div>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column: Docs & Stats */}
            <div className="space-y-6">
              <div className="bg-white border border-line rounded-2xl shadow-sm p-5">
                <h2 className="text-base font-bold text-slate-900 mb-4">Document Repository</h2>
                <DocTable docs={docs} empty="No documents yet."
                  actions={(d) => (
                    <>
                      <span className="text-[11px] text-slate-500">{STAGE_ORDER.includes(d.status) ? `stage ${STAGE_ORDER.indexOf(d.status) + 1}/3` : ""}</span>
                      {d.status !== "ARCHIVED" && (
                        <div className="flex gap-1 ml-2">
                          <button onClick={async () => { setErr(""); try { await api(`/api/v1/admin/documents/${d.id}/archive`, { method: "POST" }); await load(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Archive failed."); } }} className="text-[10px] uppercase font-bold tracking-wider text-slate-500 bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded">Arch</button>
                          <button onClick={async () => { if (!confirm(`Delete ${d.doc_title}?`)) return; setErr(""); try { await api(`/api/v1/admin/documents/${d.id}/delete`, { method: "POST" }); await load(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Delete failed."); } }} className="text-[10px] uppercase font-bold tracking-wider text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 px-2 py-1 rounded">Del</button>
                        </div>
                      )}
                    </>
                  )} />
              </div>
              
              {stats && (
                <div className="bg-white border border-line rounded-2xl shadow-sm p-5">
                  <h2 className="text-base font-bold text-slate-900 mb-4">System Stats</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-3 rounded-lg border border-line">
                      <p className="text-xs text-slate-500 font-medium">Total Users</p>
                      <p className="text-xl font-bold text-industrial">{stats.total_users}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-line">
                      <p className="text-xs text-slate-500 font-medium">Total Docs</p>
                      <p className="text-xl font-bold text-industrial">{stats.total_documents}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Usage, Audit, Gateway */}
            <div className="space-y-6">
              {usage && (
                <div className="bg-white border border-line rounded-2xl shadow-sm p-5">
                  <div className="flex justify-between items-end mb-4">
                    <div>
                      <h2 className="text-base font-bold text-slate-900">LLM Usage</h2>
                      <p className="text-xs text-slate-500">Last 30 days ({usage.total_answers} answers)</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-0.5">Est. Spend</p>
                      <p className="text-xl font-bold text-emerald-600">${usage.spend_30d_usd}</p>
                    </div>
                  </div>
                  <div className="divide-y divide-line">
                    {usage.by_model.map((m) => (
                      <div key={`${m.provider}/${m.model}`} className="py-2 text-xs flex justify-between items-center">
                        <span className="font-medium text-slate-700">{m.model}</span>
                        <span className="text-slate-500">{m.answers} calls • ${m.est_cost_usd}</span>
                      </div>
                    ))}
                    {usage.by_model.length === 0 && <p className="py-2 text-xs text-slate-500">No usage recorded.</p>}
                  </div>
                </div>
              )}

              {role === "super_admin" && gw && (
                <div className="bg-white border border-line rounded-2xl shadow-sm p-5">
                  <h2 className="text-base font-bold text-slate-900 mb-1">Gateway Config</h2>
                  <p className="text-xs text-slate-500 mb-4">SuperAdmin only</p>
                  <form className="flex flex-col gap-3"
                    onSubmit={async (e) => {
                      e.preventDefault(); setErr("");
                      try {
                        await api("/api/v1/admin/gateway", { method: "PUT", body: JSON.stringify({ ...gwForm, timeout_s: Number(gwForm.timeout_s), max_retries: Number(gwForm.max_retries) }) });
                        await load();
                      } catch (ex) { setErr(ex instanceof ApiError ? ex.message : "Gateway update failed."); }
                    }}>
                    <input value={gwForm.primary_model} onChange={(e) => setGwForm({ ...gwForm, primary_model: e.target.value })} aria-label="Primary model" className="border border-line rounded-lg p-2 text-sm" />
                    <input value={gwForm.fallback_model} onChange={(e) => setGwForm({ ...gwForm, fallback_model: e.target.value })} aria-label="Fallback model" className="border border-line rounded-lg p-2 text-sm" />
                    <div className="flex gap-3">
                      <input value={gwForm.timeout_s} onChange={(e) => setGwForm({ ...gwForm, timeout_s: e.target.value })} placeholder="Timeout" className="border border-line rounded-lg p-2 text-sm w-full" />
                      <input value={gwForm.max_retries} onChange={(e) => setGwForm({ ...gwForm, max_retries: e.target.value })} placeholder="Retries" className="border border-line rounded-lg p-2 text-sm w-full" />
                    </div>
                    <button className="bg-industrial hover:bg-industrial-dark text-white p-2 rounded-lg text-sm font-semibold transition-colors mt-1">Apply Config</button>
                  </form>
                </div>
              )}

              <div className="bg-white border border-line rounded-2xl shadow-sm p-5">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-base font-bold text-slate-900">Audit Trail</h2>
                  <span className="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-0.5 rounded-full">{audit.total} events</span>
                </div>
                <div className="flex gap-2 mb-3">
                  <input value={auditAction} onChange={(e) => setAuditAction(e.target.value)} placeholder="Filter action..." className="border border-line rounded-lg p-1.5 text-xs flex-1 bg-slate-50" />
                  <button onClick={() => { setAuditPage(0); loadAudit(auditAction, 0); }} className="bg-slate-200 text-slate-700 px-3 rounded-lg text-xs font-semibold">Filter</button>
                </div>
                <div className="divide-y divide-line text-xs font-mono max-h-40 overflow-auto">
                  {audit.items.map((a) => (
                    <div key={a.id} className="py-1.5 flex gap-2">
                      <span className="text-slate-400 shrink-0">{a.created_at.split('T')[1]?.slice(0,5)}</span>
                      <span className="text-industrial shrink-0">{a.action}</span>
                      <span className="text-slate-600 truncate">{a.actor}</span>
                    </div>
                  ))}
                  {audit.items.length === 0 && <p className="py-2 text-slate-500 font-sans">No audit events.</p>}
                </div>
                <div className="flex gap-2 mt-3 pt-3 border-t border-line">
                  <button disabled={auditPage <= 0} onClick={() => { const p = auditPage - 1; setAuditPage(p); loadAudit(auditAction, p); }} className="flex-1 bg-slate-50 border border-line rounded-lg py-1.5 text-xs font-semibold text-slate-600 disabled:opacity-50">Prev</button>
                  <button disabled={(auditPage + 1) * AUDIT_PER >= audit.total} onClick={() => { const p = auditPage + 1; setAuditPage(p); loadAudit(auditAction, p); }} className="flex-1 bg-slate-50 border border-line rounded-lg py-1.5 text-xs font-semibold text-slate-600 disabled:opacity-50">Next</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
