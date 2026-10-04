"use client";
import type { ReactNode } from "react";
import { FileText, ShieldAlert, FileImage, FileSpreadsheet } from "lucide-react";

export type CatalogDoc = {
  id: string; doc_title: string; equipment_tag: string; doc_type: string;
  division_access: string; access_reviewed: boolean; version: string;
  status: string; page_count: number;
};

export default function DocTable({ docs, empty, actions }: {
  docs: CatalogDoc[]; empty?: string; actions?: (d: CatalogDoc) => ReactNode;
}) {
  if (!docs.length) {
    return (
      <div className="p-12 text-center text-slate-500">
        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-line">
          <FileText size={32} className="text-slate-400" />
        </div>
        <p className="text-base font-medium text-slate-900 mb-1">{empty || "No documents found."}</p>
        <p className="text-sm">Try adjusting your filters or search terms.</p>
      </div>
    );
  }
  
  return (
    <div className="divide-y divide-line w-full bg-white">
      {docs.map((d) => {
        const titleLower = d.doc_title.toLowerCase();
        const isPdf = titleLower.endsWith(".pdf");
        const isPng = titleLower.endsWith(".png") || titleLower.endsWith(".jpg");
        const Icon = isPdf ? FileText : isPng ? FileImage : FileSpreadsheet;
        const iconColor = isPdf ? "text-red-500" : isPng ? "text-blue-500" : "text-emerald-500";
        
        return (
          <div key={d.id} className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors w-full group">
            <div className="w-12 h-12 rounded-xl bg-slate-50 border border-line flex items-center justify-center shrink-0">
              <Icon size={24} className={iconColor} />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1.5 flex-wrap">
                <a href={`/knowledge/${d.id}`} className="font-bold text-slate-900 text-sm hover:text-industrial truncate max-w-sm">
                  {d.doc_title}
                </a>
                {d.version && <span className="text-[10px] font-mono font-medium text-slate-500 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">v{d.version}</span>}
                {d.equipment_tag && <span className="text-[10px] font-semibold text-industrial bg-cyan-50 border border-cyan-100 px-2 py-0.5 rounded-full">{d.equipment_tag}</span>}
                {!d.access_reviewed && (
                  <span className="flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                    <ShieldAlert size={10} /> UNREVIEWED
                  </span>
                )}
              </div>
              
              <div className="text-xs text-slate-500 flex items-center gap-2 flex-wrap font-medium">
                <span className="uppercase tracking-wider">{d.doc_type || "UNKNOWN"}</span>
                <span className="text-slate-300">•</span>
                <span>{d.division_access}</span>
                <span className="text-slate-300">•</span>
                <span className={d.status === "READY" ? "text-emerald-600" : d.status === "FAILED" ? "text-red-600" : "text-industrial"}>
                  {d.status}
                </span>
                {d.page_count > 0 && (
                  <>
                    <span className="text-slate-300">•</span>
                    <span>{d.page_count} Pages</span>
                  </>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-2 shrink-0 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
              {actions?.(d)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
