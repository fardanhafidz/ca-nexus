"use client";
import type { ReactNode } from "react";

/** DEL-F8/T7.3 — shared catalog table for user Knowledge and Admin views.
 *  Same columns + division/revision labels everywhere; admin-only extras
 *  (status, lifecycle actions) come through props, never a forked table. */
export type CatalogDoc = {
  id: string; doc_title: string; equipment_tag: string; doc_type: string;
  division_access: string; access_reviewed: boolean; version: string;
  status: string; page_count: number;
};

export default function DocTable({ docs, empty, actions }: {
  docs: CatalogDoc[]; empty?: string; actions?: (d: CatalogDoc) => ReactNode;
}) {
  if (!docs.length) return <p className="p-3 text-sm text-slate-500">{empty || "No documents."}</p>;
  return (
    <div className="bg-white border rounded">
      {docs.map((d) => (
        <div key={d.id} className="p-2 border-b text-sm flex justify-between gap-2">
          <div className="min-w-0">
            <p className="font-medium"><a href={`/knowledge/${d.id}`} className="hover:underline">{d.doc_title}</a></p>
            <p className="text-xs text-slate-500">
              {d.equipment_tag || "—"} | {d.doc_type} | {d.division_access}
              {d.access_reviewed ? "" : " (UNREVIEWED)"} | v{d.version} | {d.status}
            </p>
          </div>
          <div className="flex gap-1 items-start shrink-0">{actions?.(d)}</div>
        </div>
      ))}
    </div>
  );
}
