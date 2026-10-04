"use client";
import ProcedureChecklist from "../rich-components/ProcedureChecklist";
import InterlockLogicCard from "../rich-components/InterlockLogicCard";
import SparePartBOMTable from "../rich-components/SparePartBOMTable";
import RootCauseCard from "../rich-components/RootCauseCard";
import Markdown from "./Markdown";
import { KNOWN_COMPONENTS, type Answer, type Citation } from "@/lib/contract";

const ALERT_STYLE: Record<string, string> = {
  normal: "bg-green-50 text-green-700 border-green-200",
  warning: "bg-amber-50 text-amber-700 border-amber-200",
  critical: "bg-red-50 text-red-700 border-red-200",
};

export default function MessageItem({ role, text, answer, onCite }: {
  role: string; text: string; answer?: Answer | null; onCite: (c: Citation) => void;
}) {
  if (role === "user") return <div className="bg-white border border-line rounded p-3 text-sm whitespace-pre-wrap">{text}</div>;
  if (!answer) return <div className="bg-white border border-line rounded p-3 text-sm">{text}</div>;
  if (!KNOWN_COMPONENTS.includes(answer.component_type)) {
    return (
      <div className="bg-white border border-amber-300 rounded p-3 text-sm">
        <p className="whitespace-pre-wrap">{answer.summary_text || text}</p>
        <p className="text-xs text-amber-700 mt-1">Unsupported component &apos;{answer.component_type}&apos; (schema {answer.schema_version || "?"}) — shown as text, no data guessed.</p>
      </div>
    );
  }
  const p = answer.component_payload;
  const d = (p?.details || {}) as Record<string, unknown>;
  return (
    <div className="bg-white border border-line rounded p-3 text-sm space-y-2">
      <div className="flex flex-wrap gap-1 items-center">
        {answer.equipment_tag && <span className="text-xs font-semibold border rounded px-1.5 py-0.5">{answer.equipment_tag}</span>}
        {answer.related_tags?.map((t) => <span key={t} className="text-xs border rounded px-1.5 py-0.5 text-slate-500">{t}</span>)}
        <span className={`text-xs border rounded px-1.5 py-0.5 ${ALERT_STYLE[p?.alert_level] || ALERT_STYLE.normal}`}>{p?.alert_level || "normal"}</span>
        {answer.route && <span className="text-[11px] text-slate-400">via {answer.route}</span>}
      </div>
      <Markdown text={answer.summary_text} />
      {p?.insufficient_evidence && <p className="text-xs text-amber-700 border border-amber-200 bg-amber-50 rounded p-1.5">Insufficient evidence in authorized sources — verify before acting.</p>}
      {answer.component_type === "clarification" && (
        <div className="border border-industrial rounded p-2">
          <p className="font-semibold text-sm">Clarification needed</p>
          <p className="text-sm">{String(d.question || "Which equipment or document did you mean?")}</p>
          {Array.isArray(d.options) && (d.options as string[]).length > 0 && (
            <ul className="list-disc ml-5 text-sm mt-1">
              {(d.options as string[]).map((o) => <li key={o}>{o}</li>)}
            </ul>
          )}
        </div>
      )}
      {answer.component_type === "procedure_checklist" && <ProcedureChecklist details={d} />}
      {answer.component_type === "interlock_logic" && <InterlockLogicCard details={d} />}
      {answer.component_type === "bom_table" && <SparePartBOMTable details={d} />}
      {answer.component_type === "root_cause_card" && <RootCauseCard details={d} />}
      {answer.component_type === "kpi_table" && (
        <div className="overflow-auto border rounded">
          <table className="text-xs w-full">
            <thead><tr>{Object.keys(((d.rows as Record<string, unknown>[]) || [])[0] || {}).map((k) => <th key={k} className="p-1 border bg-canvas">{k}</th>)}</tr></thead>
            <tbody>{((d.rows as Record<string, unknown>[]) || []).map((r) => {
              const rowKey = Object.entries(r).map(([k, v]) => `${k}=${String(v)}`).join("|");
              return (
                <tr key={rowKey}>{Object.entries(r).map(([k, v]) => <td key={k} className="p-1 border">{String(v)}</td>)}</tr>
              );
            })}</tbody>
          </table>
          {answer.sql_query && <pre className="text-[11px] p-2 bg-canvas overflow-auto">{answer.sql_query}</pre>}
        </div>
      )}
      {answer.citations?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {answer.citations.map((c) => (
            <button key={`${c.document_id || c.document_title}-${c.page_number ?? c.row_reference ?? ""}`} onClick={() => onCite(c)} className="text-xs border border-industrial text-industrial rounded-full px-2 py-0.5">
              {c.document_title}{c.page_number ? ` p.${c.page_number}` : ""}{c.source_type === "xlsx" && c.row_reference ? ` (${c.row_reference})` : ""}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
