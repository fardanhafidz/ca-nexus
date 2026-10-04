"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import AppSidebar from "@/components/layout/AppSidebar";
import { api, downloadFile, ApiError, API } from "@/lib/api";
import { ChevronRight, HelpCircle, ArrowLeft, FileText, Download, ShieldAlert, FileImage, FileSpreadsheet, Fingerprint, Calendar } from "lucide-react";

type Doc = { id: string; doc_title: string; equipment_tag: string; doc_type: string; division_access: string;
  access_reviewed: boolean; version: string; status: string; page_count: number; checksum: string; created_at: string };

export default function KnowledgeDetail() {
  const { id } = useParams<{ id: string }>();
  const [doc, setDoc] = useState<Doc | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api(`/api/v1/knowledge/documents/${id}`)
      .then(setDoc)
      .catch((e) => setErr(e instanceof ApiError ? e.message : "Load failed."));
  }, [id]);

  const titleLower = doc?.doc_title.toLowerCase() || "";
  const isPdf = titleLower.endsWith(".pdf");
  const isPng = titleLower.endsWith(".png") || titleLower.endsWith(".jpg");
  const Icon = isPdf ? FileText : isPng ? FileImage : FileSpreadsheet;
  const iconColor = isPdf ? "text-red-500" : isPng ? "text-blue-500" : "text-emerald-500";

  return (
    <div className="flex h-screen w-full bg-canvas">
      <AppSidebar />
      <main className="flex-1 flex flex-col bg-canvas min-w-0 overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-line px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">CA Nexus</span>
            <ChevronRight size={14} className="text-slate-400" />
            <a href="/knowledge" className="text-slate-400 hover:text-industrial transition-colors">Knowledge Base</a>
            <ChevronRight size={14} className="text-slate-400" />
            <span className="font-semibold text-slate-800 truncate max-w-xs">{doc?.doc_title || "Document Detail"}</span>
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

        <div className="p-8 max-w-5xl mx-auto w-full space-y-6">
          <a href="/knowledge" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-industrial transition-colors">
            <ArrowLeft size={16} /> Back to Repository
          </a>

          {err && <div role="alert" className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl shadow-sm text-sm">{err}</div>}
          
          {doc && (
            <div className="bg-white border border-line rounded-2xl shadow-sm overflow-hidden flex flex-col md:flex-row">
              {/* Left Column - Details */}
              <div className="flex-1 p-8">
                <div className="flex items-start gap-5 mb-8">
                  <div className="w-16 h-16 rounded-2xl bg-slate-50 border border-line flex items-center justify-center shrink-0 shadow-inner">
                    <Icon size={32} className={iconColor} />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-2 leading-tight">{doc.doc_title}</h1>
                    <div className="flex items-center gap-3 flex-wrap">
                      {doc.version && <span className="text-xs font-mono font-medium text-slate-500 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded">v{doc.version}</span>}
                      {doc.equipment_tag && <span className="text-xs font-semibold text-industrial bg-cyan-50 border border-cyan-100 px-2.5 py-0.5 rounded-full">{doc.equipment_tag}</span>}
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">{doc.doc_type}</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6 mb-8">
                  <div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Division Access</p>
                    <p className="font-medium text-slate-800 flex items-center gap-2">
                      {doc.division_access}
                      {!doc.access_reviewed && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-full">
                          <ShieldAlert size={10} /> UNREVIEWED
                        </span>
                      )}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Ingestion Status</p>
                    <p className="font-medium flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${doc.status === 'READY' ? 'bg-emerald-500' : doc.status === 'FAILED' ? 'bg-red-500' : 'bg-industrial'}`}></span>
                      {doc.status}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Total Pages</p>
                    <p className="font-medium text-slate-800">{doc.page_count} Pages</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1"><Calendar size={12}/> Added On</p>
                    <p className="font-medium text-slate-800">{new Date(doc.created_at).toLocaleDateString()}</p>
                  </div>
                </div>

                <div className="bg-slate-50 rounded-xl p-4 border border-line">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1"><Fingerprint size={12}/> SHA-256 Checksum</p>
                  <p className="text-[11px] font-mono text-slate-600 break-all">{doc.checksum || "—"}</p>
                </div>
              </div>

              {/* Right Column - Actions & Preview */}
              <div className="w-full md:w-72 bg-slate-50 border-l border-line p-8 flex flex-col justify-center items-center gap-4">
                <div className="w-32 h-40 bg-white border border-line shadow-sm rounded-lg flex items-center justify-center mb-2">
                  <Icon size={48} className={`opacity-20 ${iconColor}`} />
                </div>
                <button onClick={() => downloadFile(doc.id, doc.doc_title)} className="w-full bg-industrial hover:bg-industrial-dark text-white py-3 px-4 rounded-xl font-bold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2">
                  <Download size={18} /> Download File
                </button>
                <a href={`${API}/api/v1/knowledge/file/${doc.id}`} target="_blank" rel="noreferrer" className="w-full bg-white border border-line hover:border-slate-300 text-slate-700 py-3 px-4 rounded-xl font-semibold shadow-sm transition-all flex items-center justify-center gap-2 text-sm text-center">
                  Open in Browser
                </a>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
