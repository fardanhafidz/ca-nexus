"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import SlimRail from "@/components/layout/SlimRail";
import { api, downloadFile, ApiError } from "@/lib/api";

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
  return (
    <div className="flex h-screen">
      <SlimRail />
      <main className="flex-1 bg-canvas p-4 overflow-auto">
        <a href="/knowledge" className="text-xs text-industrial underline">← Repository</a>
        <h1 className="font-semibold text-industrial mt-1 mb-2">Document Detail</h1>
        {err && <p role="alert" className="text-xs text-red-600">{err}</p>}
        {doc && (
          <div className="bg-white border rounded p-4 text-sm space-y-1 max-w-2xl">
            <p className="font-medium">{doc.doc_title}</p>
            <p className="text-xs text-slate-500">Tag: {doc.equipment_tag || "—"} | Type: {doc.doc_type} | v{doc.version}</p>
            <p className="text-xs text-slate-500">Access: {doc.division_access}{doc.access_reviewed ? "" : " (UNREVIEWED)"} | Status: {doc.status} | Pages: {doc.page_count}</p>
            <p className="text-[11px] text-slate-400 break-all">sha256: {doc.checksum || "—"}</p>
            <button onClick={() => downloadFile(doc.id, doc.doc_title)} className="bg-industrial text-white px-3 py-1.5 rounded text-sm mt-2">Open file</button>
          </div>
        )}
      </main>
    </div>
  );
}
