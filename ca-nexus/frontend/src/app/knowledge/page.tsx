"use client";
import { useEffect, useState } from "react";
import AppSidebar from "@/components/layout/AppSidebar";
import DocTable from "@/components/knowledge/DocTable";
import { api, downloadFile, ApiError } from "@/lib/api";
import { ChevronRight, HelpCircle, Search, Filter, BookOpen } from "lucide-react";

export default function Knowledge() {
  const [docs, setDocs] = useState<Parameters<typeof DocTable>[0]["docs"]>([]);
  const [total, setTotal] = useState(0);
  const [q, setQ] = useState("");
  const [tag, setTag] = useState("");
  const [docType, setDocType] = useState("");
  const [docStatus, setDocStatus] = useState("");
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(1);
  const [err, setErr] = useState("");
  const perPage = 20;

  const load = async (p = 1) => {
    setErr("");
    try {
      const j = await api(`/api/v1/knowledge/documents?q=${encodeURIComponent(q)}&equipment_tag=${encodeURIComponent(tag)}&doc_type=${encodeURIComponent(docType)}&status=${encodeURIComponent(docStatus)}&sort=${sort}&page=${p}&per_page=${perPage}`);
      setDocs(j.items); setTotal(j.total); setPage(j.page);
    } catch (e) { setErr(e instanceof ApiError ? e.message : "Search failed."); }
  };
  useEffect(() => { load(1); }, []);

  return (
    <div className="flex h-screen w-full bg-canvas">
      <AppSidebar />
      <main className="flex-1 flex flex-col bg-canvas min-w-0 overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-line px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">CA Nexus</span>
            <ChevronRight size={14} className="text-slate-400" />
            <span className="font-semibold text-slate-800">Knowledge Base</span>
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

        <div className="p-8 max-w-7xl mx-auto w-full space-y-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 tracking-tight mb-2">Knowledge Repository</h1>
              <p className="text-slate-500 text-base">Search and explore verified factory documents, manuals, and SOPs.</p>
            </div>
            <div className="bg-white border border-line rounded-xl shadow-sm p-3 flex gap-2">
               <div className="bg-industrial/10 text-industrial px-4 py-2 rounded-lg font-bold text-sm flex items-center gap-2">
                 <BookOpen size={18} /> {total} Indexed Documents
               </div>
            </div>
          </div>

          <div className="bg-white border border-line rounded-2xl shadow-sm p-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative flex-1 min-w-[200px]">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Search size={18} />
                </div>
                <input 
                  value={q} 
                  onChange={(e) => setQ(e.target.value)} 
                  onKeyDown={(e) => { if (e.key === "Enter") load(1); }}
                  placeholder="Search document title..." 
                  className="w-full border border-line rounded-xl pl-10 pr-4 py-2.5 text-sm bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-industrial/20 shadow-sm transition-all" 
                />
              </div>
              <input value={tag} onChange={(e) => setTag(e.target.value)} placeholder="Tag e.g. KC-4501" className="border border-line rounded-xl px-4 py-2.5 text-sm bg-slate-50 focus:bg-white focus:outline-none shadow-sm w-40" />
              
              <div className="flex items-center gap-2 bg-slate-50 border border-line rounded-xl px-3 py-1 shadow-sm">
                <Filter size={16} className="text-slate-400" />
                <select value={docType} onChange={(e) => setDocType(e.target.value)} className="bg-transparent border-none focus:outline-none text-sm text-slate-700 py-1.5 cursor-pointer">
                  <option value="">All types</option>
                  {["opl", "datasheet", "drawing", "interlock", "plot_plan", "pid", "other"].map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              <div className="flex items-center gap-2 bg-slate-50 border border-line rounded-xl px-3 py-1 shadow-sm">
                <select value={docStatus} onChange={(e) => setDocStatus(e.target.value)} className="bg-transparent border-none focus:outline-none text-sm text-slate-700 py-1.5 cursor-pointer">
                  <option value="">All statuses</option>
                  <option value="READY">Ready</option>
                  <option value="PARSING">Parsing</option>
                  <option value="VECTORIZING">Vectorizing</option>
                  <option value="FAILED">Failed</option>
                  <option value="ARCHIVED">Archived</option>
                </select>
              </div>

              <div className="flex items-center gap-2 bg-slate-50 border border-line rounded-xl px-3 py-1 shadow-sm">
                <select value={sort} onChange={(e) => setSort(e.target.value)} className="bg-transparent border-none focus:outline-none text-sm text-slate-700 py-1.5 cursor-pointer">
                  <option value="newest">Newest First</option>
                  <option value="title">Alphabetical</option>
                  <option value="equipment">By Equipment</option>
                </select>
              </div>

              <button onClick={() => load(1)} className="bg-industrial hover:bg-industrial-dark text-white px-6 py-2.5 rounded-xl text-sm font-bold shadow-md transition-all shrink-0">
                Search
              </button>
            </div>
          </div>

          {err && <div role="alert" className="bg-red-50 text-red-600 text-sm p-4 rounded-xl border border-red-100">{err}</div>}
          
          <div className="bg-white border border-line rounded-2xl shadow-sm overflow-hidden">
            <DocTable docs={docs} empty="No documents found."
              actions={(d) => (
                <button onClick={() => downloadFile(d.id, d.doc_title)} className="bg-white border border-line text-slate-600 hover:text-industrial hover:border-industrial px-3 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition-colors shrink-0">
                  Open
                </button>
              )} 
            />
            
            <div className="p-4 bg-slate-50 border-t border-line flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500">Showing page {page}</span>
              <div className="flex gap-2">
                <button disabled={page <= 1} onClick={() => load(page - 1)} className="bg-white border border-line rounded-lg px-4 py-2 text-xs font-semibold text-slate-700 disabled:opacity-50 hover:bg-slate-50 shadow-sm transition-colors">Previous</button>
                <button disabled={page * perPage >= total} onClick={() => load(page + 1)} className="bg-white border border-line rounded-lg px-4 py-2 text-xs font-semibold text-slate-700 disabled:opacity-50 hover:bg-slate-50 shadow-sm transition-colors">Next</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
