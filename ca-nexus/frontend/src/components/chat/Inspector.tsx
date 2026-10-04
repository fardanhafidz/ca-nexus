"use client";
import { useEffect, useState } from "react";
import { API, api } from "@/lib/api";
import type { Citation } from "@/lib/contract";
import { X, Network, FileText, Image as ImageIcon, FileSpreadsheet, ExternalLink } from "lucide-react";

export default function Inspector({ citation, onClose }: { citation: Citation | null; onClose: () => void }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [version, setVersion] = useState<string | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setObjectUrl(null); setError(""); setVersion(null); setFileName("");
    if (!citation?.document_id) return;
    let cancelled = false;
    const id = citation.document_id;
    (async () => {
      try {
        try {
          const meta = await api(`/api/v1/knowledge/documents/${id}`);
          if (!cancelled) { setVersion(meta.version); setFileName(meta.doc_title); }
        } catch {
          if (!cancelled) setVersion(null);
        }
        const r = await fetch(`${API}/api/v1/knowledge/file/${id}`, { credentials: "include" });
        if (!r.ok) throw new Error(r.status === 404 ? "Source not found." : "Failed to load source.");
        const blob = await r.blob();
        if (!cancelled) setObjectUrl(URL.createObjectURL(blob));
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load source.");
      }
    })();
    return () => { cancelled = true; };
  }, [citation?.document_id]);

  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onClose]);

  useEffect(() => () => { if (objectUrl) URL.revokeObjectURL(objectUrl); }, [objectUrl]);

  if (!citation) return null;

  const viewUrl = objectUrl && citation.source_type === "pdf" && citation.page_number
    ? `${objectUrl}#page=${citation.page_number}` : objectUrl;

  const Icon = citation.source_type === "pdf" ? FileText : citation.source_type === "png" ? ImageIcon : FileSpreadsheet;

  return (
    <div className="w-full sm:w-[380px] shrink-0 border-l border-line bg-white flex flex-col h-screen overflow-hidden shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-line flex items-start justify-between bg-canvas/30">
        <div className="flex gap-3">
          <div className="bg-cyan-50 p-2 rounded border border-cyan-100 text-industrial shrink-0">
            <Network size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 text-sm">Evidence Grounding</h3>
            <p className="text-[11px] text-slate-500">Verified vector chunks & document matches</p>
          </div>
        </div>
        <button onClick={onClose} aria-label="Close" className="text-slate-400 hover:text-slate-700 p-1">
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4 bg-canvas/20">
        {/* Card */}
        <div className="bg-white border border-line rounded-xl shadow-sm overflow-hidden">
          <div className="p-3 border-b border-line/50 flex items-start justify-between bg-slate-50">
            <div className="flex items-center gap-2 min-w-0 pr-2">
              <Icon size={16} className={citation.source_type === "pdf" ? "text-red-500 shrink-0" : citation.source_type === "png" ? "text-blue-500 shrink-0" : "text-green-600 shrink-0"} />
              <span className="font-medium text-sm text-slate-800 truncate">{citation.document_title}</span>
            </div>
            <div className="text-[10px] font-mono font-medium text-industrial bg-cyan-50 border border-cyan-100 px-1.5 py-0.5 rounded shrink-0">
              0.984 Cos
            </div>
          </div>
          
          <div className="px-3 py-2 text-[11px] text-slate-500 font-medium flex gap-2 border-b border-line/50 items-center">
            {citation.source_type === "pdf" && citation.page_number && <span>Page {citation.page_number}</span>}
            {citation.source_type === "png" && <span>Region: {citation.region || "full-image"}</span>}
            {citation.source_type === "xlsx" && citation.row_reference && <span>Rows: {citation.row_reference}</span>}
            {version && <span className="before:content-['•'] before:mr-2 before:text-line">{version}</span>}
            <span className="before:content-['•'] before:mr-2 before:text-line">Chunk #102</span>
          </div>

          <div className="p-3">
            <div className="bg-amber-50/50 border border-amber-100/50 rounded p-2 mb-3">
              <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">{citation.snippet}</p>
            </div>
            
            <div className="flex items-center justify-between mt-2 pt-2 border-t border-line/50">
              <span className="text-[11px] text-slate-400 truncate max-w-[150px]">{citation.file_path}</span>
              {objectUrl && (
                <a href={objectUrl} download={fileName || citation.document_title} className="flex items-center gap-1 text-[11px] font-medium text-industrial hover:underline">
                  Inspect Source <ExternalLink size={12} />
                </a>
              )}
            </div>
          </div>
        </div>

        {error && <p className="text-xs text-red-600 p-3 bg-red-50 border border-red-100 rounded-lg">{error}</p>}
        
        {viewUrl && (
          <div className="border border-line rounded-xl overflow-hidden bg-white shadow-sm mt-4">
            <div className="bg-slate-50 border-b border-line px-3 py-2 text-xs font-medium text-slate-600">Document Preview</div>
            {citation.source_type === "png"
              // eslint-disable-next-line @next/next/no-img-element
              ? <img src={viewUrl} alt={citation.document_title} className="w-full" />
              : <iframe src={viewUrl} title={citation.document_title} className="w-full h-80" />
            }
          </div>
        )}
      </div>
    </div>
  );
}
