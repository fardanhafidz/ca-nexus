"use client";
import { useEffect, useState } from "react";
import { API, api } from "@/lib/api";
import type { Citation } from "@/lib/contract";

/** T6.10 — Inspector loads via authorized file/{id} + cookie (never ?token=).
 *  PDF: #page= fragment. PNG: region/bbox label. XLSX: row references.
 *  DEL-F7: shows revision + explicit download; lost access/revision/invalid handled. */
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
          if (!cancelled) setVersion(null);  // revision unknown — preview may still work
        }
        const r = await fetch(`${API}/api/v1/knowledge/file/${id}`, { credentials: "include" });
        if (!r.ok) throw new Error(r.status === 404 ? "Source not found, removed, or not authorized." : r.status === 409 ? "Source not ready or archived." : "Failed to load source.");
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
  return (
    <div className="w-full sm:w-96 shrink-0 border-l border-line bg-white p-3 overflow-auto">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-sm">Source Inspector</h3>
        <button onClick={onClose} aria-label="Close inspector" className="text-xs border rounded px-2 py-1">Close (Esc)</button>
      </div>
      <p className="text-xs font-medium">{citation.document_title}</p>
      {version && <p className="text-xs text-slate-500">Revision {version}</p>}
      {citation.source_type === "pdf" && citation.page_number && <p className="text-xs text-slate-500">Page {citation.page_number}</p>}
      {citation.source_type === "png" && (
        <p className="text-xs text-slate-500">
          Image region: {citation.region || "full-image"}
          {citation.bbox ? ` [${citation.bbox.map((n) => n.toFixed(2)).join(", ")}]` : ""}
        </p>
      )}
      {citation.source_type === "xlsx" && citation.row_reference && <p className="text-xs text-slate-500">Rows: {citation.row_reference}</p>}
      <blockquote className="text-xs border-l-2 border-industrial pl-2 my-2 whitespace-pre-wrap">{citation.snippet}</blockquote>
      <p className="text-[11px] text-slate-500 break-all">{citation.file_path}</p>
      {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
      {objectUrl && (
        <a href={objectUrl} download={fileName || citation.document_title}
          className="text-xs text-industrial underline">Download source</a>
      )}
      {viewUrl && (
        citation.source_type === "png"
          // eslint-disable-next-line @next/next/no-img-element
          ? <img src={viewUrl} alt={citation.document_title} className="mt-2 max-w-full border rounded" />
          : <iframe src={viewUrl} title={citation.document_title} className="mt-2 w-full h-96 border rounded" />
      )}
      {!citation.document_id && <p className="text-[11px] text-slate-500 mt-2">Legacy citation without document id — open it from the Knowledge page.</p>}
    </div>
  );
}
