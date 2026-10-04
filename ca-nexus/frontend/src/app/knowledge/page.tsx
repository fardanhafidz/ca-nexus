"use client";
import { useEffect, useState } from "react";
import SlimRail from "@/components/layout/SlimRail";
import DocTable from "@/components/knowledge/DocTable";
import { api, downloadFile, ApiError } from "@/lib/api";

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
    <div className="flex h-screen">
      <SlimRail />
      <main className="flex-1 bg-canvas p-4 overflow-auto">
        <h1 className="font-semibold text-industrial mb-2">Knowledge Repository</h1>
        <div className="flex gap-2 mb-3 flex-wrap">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search title..." aria-label="Search title" className="border rounded p-2 text-sm flex-1" />
          <input value={tag} onChange={(e) => setTag(e.target.value)} placeholder="Tag e.g. KC-4501" aria-label="Equipment tag" className="border rounded p-2 text-sm w-40" />
          <select value={docType} onChange={(e) => setDocType(e.target.value)} aria-label="Document type" className="border rounded p-2 text-sm">
            <option value="">All types</option>
            {["opl", "datasheet", "drawing", "interlock", "plot_plan", "pid", "other"].map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={docStatus} onChange={(e) => setDocStatus(e.target.value)} aria-label="Ingestion status" className="border rounded p-2 text-sm">
            <option value="">All statuses</option>
            <option value="READY">Ready</option>
            <option value="PARSING">Parsing</option>
            <option value="VECTORIZING">Vectorizing</option>
            <option value="FAILED">Failed</option>
            <option value="ARCHIVED">Archived</option>
          </select>
          <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort" className="border rounded p-2 text-sm">
            <option value="newest">Newest</option>
            <option value="title">Title</option>
            <option value="equipment">Equipment</option>
          </select>
          <button onClick={() => load(1)} className="bg-industrial text-white px-3 rounded text-sm">Search</button>
        </div>
        {err && <p role="alert" className="text-xs text-red-600 mb-2">{err}</p>}
        <p className="text-xs text-slate-500 mb-2">{total} document(s) visible for your division.</p>
        <DocTable docs={docs} empty="No documents visible for your division."
          actions={(d) => (
            <button onClick={() => downloadFile(d.id, d.doc_title)} className="text-industrial underline text-xs shrink-0">Open</button>
          )} />
        <div className="flex gap-2 mt-2 text-sm">
          <button disabled={page <= 1} onClick={() => load(page - 1)} className="border rounded px-2 py-1 disabled:opacity-50">Prev</button>
          <span className="text-xs self-center">Page {page}</span>
          <button disabled={page * perPage >= total} onClick={() => load(page + 1)} className="border rounded px-2 py-1 disabled:opacity-50">Next</button>
        </div>
      </main>
    </div>
  );
}
