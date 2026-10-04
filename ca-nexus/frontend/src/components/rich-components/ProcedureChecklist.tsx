"use client";
import { useState } from "react";
/** T6.6 — Source fields (prerequisites, parameters, warnings); instruction state
 *  is per-session UI only (resets on refresh — not an official work record). */
type Step = { step?: number | null; instruction?: string; action?: string; parameter?: string | null; unit?: string | null };
export default function ProcedureChecklist({ details }: { details: Record<string, unknown> }) {
  const steps = ((details.steps as Step[]) || (details.items as Step[]) || []) as Step[];
  const prereq = (details.prerequisites as string[]) || [];
  const warnings = (details.warnings as string[]) || [];
  const [done, setDone] = useState<Record<string, boolean>>({});
  return (
    <div className="border rounded p-2">
      <p className="font-semibold text-sm">{String(details.procedure || details.title || "Procedure Checklist")}</p>
      {prereq.length > 0 && <p className="text-xs text-slate-600 mt-1">Prerequisites: {prereq.join("; ")}</p>}
      <ol className="list-decimal ml-5 text-sm space-y-1 mt-1">
        {steps.map((s, i) => {
          const key = `${s.step ?? i}`;
          return (
            <li key={key} className="flex gap-2 items-start">
              <input type="checkbox" aria-label={`Step ${key}`} checked={!!done[key]} onChange={() => setDone({ ...done, [key]: !done[key] })} />
              <span>{typeof s === "string" ? s : (s.instruction || s.action || "unknown step")}
                {(s as Step).parameter ? <em className="text-slate-500"> [{(s as Step).parameter}{(s as Step).unit ? ` ${(s as Step).unit}` : ""}]</em> : null}
              </span>
            </li>
          );
        })}
      </ol>
      {steps.length === 0 && <p className="text-xs text-slate-500">No steps in payload — see summary and citations.</p>}
      {warnings.length > 0 && <p className="text-xs text-amber-700 mt-1">Warnings: {warnings.join("; ")}</p>}
      <p className="text-[11px] text-slate-400 mt-1">Checks live in this session only and reset on refresh — not an official work record (see docs/SCOPE.md).</p>
    </div>
  );
}
