"use client";
import { useState } from "react";
import { ListChecks, AlertTriangle, Info } from "lucide-react";

type Step = { step?: number | null; instruction?: string; action?: string; parameter?: string | null; unit?: string | null };

export default function ProcedureChecklist({ details }: { details: Record<string, unknown> }) {
  const steps = ((details.steps as Step[]) || (details.items as Step[]) || []) as Step[];
  const prereq = (details.prerequisites as string[]) || [];
  const warnings = (details.warnings as string[]) || [];
  const [done, setDone] = useState<Record<string, boolean>>({});

  const progress = steps.length > 0 ? Math.round((Object.values(done).filter(Boolean).length / steps.length) * 100) : 0;

  return (
    <div className="bg-white border border-line rounded-xl shadow-sm overflow-hidden my-3">
      <div className="bg-slate-50 border-b border-line p-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
            <ListChecks size={18} />
          </div>
          <p className="font-bold text-slate-800">{String(details.procedure || details.title || "Procedure Checklist")}</p>
        </div>
        {steps.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500">{progress}%</span>
            <div className="w-20 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 space-y-4">
        {warnings.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-start gap-3">
            <AlertTriangle size={18} className="text-amber-600 shrink-0 mt-0.5" />
            <div className="text-sm text-amber-800">
              <span className="font-bold block mb-1">Critical Warnings:</span>
              <ul className="list-disc pl-4 space-y-1">
                {warnings.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          </div>
        )}

        {prereq.length > 0 && (
          <div className="bg-slate-50 border border-line rounded-lg p-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">Prerequisites</span>
            <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
              {prereq.map((p, i) => <li key={i}>{p}</li>)}
            </ul>
          </div>
        )}

        <div className="space-y-2">
          {steps.map((s, i) => {
            const key = `${s.step ?? i}`;
            const isDone = !!done[key];
            return (
              <label key={key} className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${isDone ? "bg-slate-50 border-slate-200" : "bg-white border-line hover:border-indigo-300 hover:shadow-sm"}`}>
                <div className="pt-0.5">
                  <input 
                    type="checkbox" 
                    checked={isDone} 
                    onChange={() => setDone({ ...done, [key]: !isDone })}
                    className="w-5 h-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-600 transition-all cursor-pointer"
                  />
                </div>
                <div className={`flex-1 text-sm ${isDone ? "text-slate-400 line-through" : "text-slate-700"}`}>
                  <span className="font-semibold text-slate-900 mr-2">{s.step ?? i + 1}.</span>
                  {typeof s === "string" ? s : (s.instruction || s.action || "unknown step")}
                  {(s as Step).parameter && (
                    <span className={`ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium ${isDone ? "bg-slate-100 text-slate-400" : "bg-indigo-50 text-indigo-700 border border-indigo-100"}`}>
                      {(s as Step).parameter}{(s as Step).unit ? ` ${(s as Step).unit}` : ""}
                    </span>
                  )}
                </div>
              </label>
            );
          })}
        </div>

        {steps.length === 0 && (
          <div className="text-center p-6 text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-300">
            No steps in payload — see summary and citations.
          </div>
        )}
      </div>

      <div className="bg-slate-50 px-4 py-2 border-t border-line flex items-center gap-2 text-[11px] text-slate-500">
        <Info size={14} className="shrink-0" />
        Checks live in this session only and reset on refresh — not an official work record.
      </div>
    </div>
  );
}
