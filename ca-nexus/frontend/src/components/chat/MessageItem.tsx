"use client";
import ProcedureChecklist from "../rich-components/ProcedureChecklist";
import InterlockLogicCard from "../rich-components/InterlockLogicCard";
import SparePartBOMTable from "../rich-components/SparePartBOMTable";
import RootCauseCard from "../rich-components/RootCauseCard";
import Markdown from "./Markdown";
import { KNOWN_COMPONENTS, type Answer, type Citation } from "@/lib/contract";
import { Network, Copy, ThumbsUp, ThumbsDown, Share2, Search, FileText, CheckCircle2 } from "lucide-react";

const ALERT_STYLE: Record<string, string> = {
  normal: "bg-green-50 text-green-700 border-green-200",
  warning: "bg-amber-50 text-amber-700 border-amber-200",
  critical: "bg-red-50 text-red-700 border-red-200",
};

export default function MessageItem({ role, text, answer, onCite }: {
  role: string; text: string; answer?: Answer | null; onCite: (c: Citation) => void;
}) {
  if (role === "user") {
    return (
      <div className="flex justify-end gap-3 w-full mb-6 max-w-4xl mx-auto">
        <div className="bg-white border border-line rounded-xl rounded-tr-sm p-4 text-sm shadow-sm max-w-[85%]">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-semibold text-industrial">Dr. Elena Vance</span>
            <span className="text-xs text-slate-400">03:19 UTC</span>
          </div>
          <p className="whitespace-pre-wrap text-slate-700 leading-relaxed">{text}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-500 shrink-0 shadow-sm flex items-center justify-center text-white text-xs font-bold mt-1">
          {/* Avatar Placeholder */}
          EV
        </div>
      </div>
    );
  }

  // Assistant Message Layout
  return (
    <div className="flex gap-3 w-full mb-6 max-w-4xl mx-auto">
      <div className="bg-white border border-line rounded-xl rounded-tl-sm shadow-sm w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-line/50 pb-3">
          <div className="flex items-center gap-3">
            <div className="bg-canvas p-1.5 rounded-lg border border-line/50 text-industrial">
              <Network size={16} />
            </div>
            <span className="font-bold text-slate-800">CA Nexus</span>
            <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
              <CheckCircle2 size={12} /> Verified Factory RAG
            </span>
          </div>
          <div className="text-[11px] font-medium text-slate-500 bg-slate-100 border border-line px-2 py-0.5 rounded-md">
            Model v1.2
          </div>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {!answer ? (
            <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{text}</div>
          ) : !KNOWN_COMPONENTS.includes(answer.component_type) ? (
            <div className="bg-white border border-amber-300 rounded p-3 text-sm">
              <p className="whitespace-pre-wrap">{answer.summary_text || text}</p>
              <p className="text-xs text-amber-700 mt-1">Unsupported component '{answer.component_type}'</p>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap gap-1 items-center mb-2">
                {answer.equipment_tag && <span className="text-xs font-semibold border border-line bg-canvas rounded px-2 py-0.5">{answer.equipment_tag}</span>}
                {answer.related_tags?.map((t) => <span key={t} className="text-xs border rounded px-2 py-0.5 text-slate-500">{t}</span>)}
                {answer.component_payload?.alert_level && <span className={`text-xs border rounded px-2 py-0.5 ${ALERT_STYLE[answer.component_payload.alert_level] || ALERT_STYLE.normal}`}>{answer.component_payload.alert_level}</span>}
              </div>
              
              <div className="text-sm text-slate-800 leading-relaxed">
                <Markdown text={answer.summary_text} />
              </div>

              {/* Rich Components */}
              {(() => {
                const p = answer.component_payload;
                const d = (p?.details || {}) as Record<string, unknown>;
                
                if (p?.insufficient_evidence) return <p className="text-xs text-amber-700 border border-amber-200 bg-amber-50 rounded p-2">Insufficient evidence in authorized sources — verify before acting.</p>;
                
                if (answer.component_type === "clarification") {
                  return (
                    <div className="border border-industrial rounded p-3 bg-industrial/5">
                      <p className="font-semibold text-sm mb-1">Clarification needed</p>
                      <p className="text-sm">{String(d.question || "Which equipment or document did you mean?")}</p>
                      {Array.isArray(d.options) && (d.options as string[]).length > 0 && (
                        <ul className="list-disc ml-5 text-sm mt-2 space-y-1">
                          {(d.options as string[]).map((o) => <li key={o}>{o}</li>)}
                        </ul>
                      )}
                    </div>
                  );
                }
                if (answer.component_type === "procedure_checklist") return <ProcedureChecklist details={d} />;
                if (answer.component_type === "interlock_logic") return <InterlockLogicCard details={d} />;
                if (answer.component_type === "bom_table") return <SparePartBOMTable details={d} />;
                if (answer.component_type === "root_cause_card") return <RootCauseCard details={d} />;
                
                return null;
              })()}

              {/* Citations block mimicking UI */}
              {answer.citations?.length > 0 && (
                <div className="mt-4 pt-3 border-t border-line border-dashed space-y-3">
                  <div className="flex flex-wrap gap-2">
                    {answer.citations.map((c, i) => (
                      <button key={i} onClick={() => onCite(c)} className="flex items-center gap-1.5 text-xs font-medium bg-canvas border border-line text-slate-600 hover:border-industrial hover:text-industrial rounded px-2.5 py-1.5 transition-colors">
                        <FileText size={14} className="text-red-500" />
                        <span>[{c.document_title} · {c.page_number ? `Page ${c.page_number}` : c.row_reference ? `Row ${c.row_reference}` : 'Ref'}]</span>
                      </button>
                    ))}
                  </div>
                  <button onClick={() => answer.citations?.[0] && onCite(answer.citations[0])} className="flex items-center gap-2 text-sm font-medium bg-cyan-50 border border-cyan-100 text-industrial px-4 py-2 rounded-lg hover:bg-cyan-100 transition-colors">
                    <Search size={16} /> Inspect Grounding & Evidence ({answer.citations.length} Sources Cited)
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 bg-slate-50 border-t border-line/50 rounded-b-xl flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.5)]"></span>
            Grounded on 34.2M factory vectors
          </div>
          <div className="flex items-center gap-2">
            <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-line rounded transition-colors" title="Copy"><Copy size={16} /></button>
            <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-line rounded transition-colors" title="Helpful"><ThumbsUp size={16} /></button>
            <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-line rounded transition-colors" title="Not Helpful"><ThumbsDown size={16} /></button>
            <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-line rounded transition-colors" title="Share"><Share2 size={16} /></button>
          </div>
        </div>
      </div>
    </div>
  );
}
