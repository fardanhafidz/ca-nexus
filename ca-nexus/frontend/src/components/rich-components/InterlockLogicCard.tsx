"use client";
import { Zap, AlertCircle } from "lucide-react";

const U = (v: unknown) => (v === null || v === undefined || v === "" ? "unknown" : String(v));
type Cause = { instrument_tag?: string | null; condition?: string | null; comparator?: string | null;
  setpoint?: string | null; unit?: string | null; voting?: string | null; delay?: string | null; effect?: string | null;
  source?: string | null };

export default function InterlockLogicCard({ details }: { details: Record<string, unknown> }) {
  const rows = ((details.causes as Cause[]) || (details.rows as Cause[]) || []) as Cause[];
  const showVoting = rows.some((r) => r.voting);
  const showDelay = rows.some((r) => r.delay);
  const showSource = rows.some((r) => r.source);

  return (
    <div className="bg-white border border-line rounded-xl shadow-sm overflow-hidden my-3">
      <div className="bg-red-50/50 border-b border-red-100 p-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-red-100 text-red-600 flex items-center justify-center shrink-0">
            <Zap size={18} />
          </div>
          <div>
            <p className="font-bold text-slate-800 leading-tight">{String(details.interlock_id || details.title || "Interlock Logic")}</p>
            {details.reset ? <p className="text-[11px] font-medium text-red-600 mt-0.5">Reset: {String(details.reset)}</p> : null}
          </div>
        </div>
      </div>

      <div className="p-0 overflow-x-auto">
        {rows.length > 0 ? (
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 bg-slate-50 border-b border-line uppercase font-semibold">
              <tr>
                <th className="px-4 py-3 whitespace-nowrap">Instrument</th>
                <th className="px-4 py-3 whitespace-nowrap">Condition</th>
                <th className="px-4 py-3 whitespace-nowrap">Setpoint</th>
                {showVoting && <th className="px-4 py-3 whitespace-nowrap">Voting</th>}
                {showDelay && <th className="px-4 py-3 whitespace-nowrap">Delay</th>}
                <th className="px-4 py-3 whitespace-nowrap">Effect</th>
                {showSource && <th className="px-4 py-3 whitespace-nowrap text-right">Source</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {rows.map((r) => {
                const rowKey = `${r.instrument_tag || "?"}|${r.condition || r.comparator || ""}|${r.effect || ""}`;
                const hasValue = (val: string) => val !== "unknown" && val !== "—";
                
                return (
                  <tr key={rowKey} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-4 py-3 font-mono text-industrial font-semibold">{U(r.instrument_tag)}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
                        {U(r.condition || (r.comparator ? `${r.comparator}` : null))}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-mono text-xs ${r.setpoint ? "text-slate-800 font-semibold" : "text-slate-400 italic"}`}>
                        {r.setpoint ? `${r.setpoint}${r.unit ? ` ${r.unit}` : ""}` : "unknown"}
                      </span>
                    </td>
                    {showVoting && (
                      <td className="px-4 py-3">
                        {hasValue(U(r.voting)) ? (
                          <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">{U(r.voting)}</span>
                        ) : <span className="text-slate-400 italic text-xs">unknown</span>}
                      </td>
                    )}
                    {showDelay && (
                      <td className="px-4 py-3 text-slate-600 text-xs">
                        {hasValue(U(r.delay)) ? U(r.delay) : <span className="text-slate-400 italic">unknown</span>}
                      </td>
                    )}
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-bold bg-red-50 text-red-700 border border-red-100 shadow-sm">
                        {U(r.effect)}
                      </span>
                    </td>
                    {showSource && <td className="px-4 py-3 text-xs text-slate-400 text-right">{r.source || "—"}</td>}
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 text-slate-500 gap-2">
            <AlertCircle size={24} className="text-slate-400" />
            <p className="text-sm">No cause rows in payload — see summary and citations.</p>
          </div>
        )}
      </div>
    </div>
  );
}
