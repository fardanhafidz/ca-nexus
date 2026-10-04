"use client";
import { SearchCode, AlertCircle, Sparkles, BookOpen } from "lucide-react";

export default function RootCauseCard({ details }: { details: Record<string, unknown> }) {
  const refs = (details.record_refs as string[]) || [];
  const hasData = details.anomaly || details.recorded_cause || details.hypothesis || details.recommendation;

  return (
    <div className="bg-white border border-line rounded-xl shadow-sm overflow-hidden my-3">
      <div className="bg-slate-50 border-b border-line p-3 flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center shrink-0">
          <SearchCode size={18} />
        </div>
        <p className="font-bold text-slate-800">{String(details.title || "Root Cause Analysis")}</p>
      </div>

      <div className="p-4 space-y-4 text-sm">
        {hasData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {details.anomaly && (
              <div className="bg-red-50/50 border border-red-100 rounded-lg p-3">
                <span className="text-[11px] font-bold text-red-600 uppercase tracking-wider block mb-1">Anomaly</span>
                <p className="text-slate-800 font-medium">{String(details.anomaly)}</p>
              </div>
            )}
            
            <div className="bg-slate-50 border border-line rounded-lg p-3">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Recorded Cause</span>
              <p className={details.recorded_cause ? "text-slate-800 font-medium" : "text-slate-400 italic"}>
                {details.recorded_cause ? String(details.recorded_cause) : "unknown"}
              </p>
            </div>

            {details.hypothesis && (
              <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-3 md:col-span-2 relative overflow-hidden">
                <div className="absolute -right-2 -top-2 text-indigo-500/10"><Sparkles size={64}/></div>
                <div className="flex items-center gap-1.5 mb-1 relative z-10">
                  <Sparkles size={14} className="text-indigo-600" />
                  <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">AI Hypothesis</span>
                  <span className="text-[9px] bg-indigo-100 text-indigo-700 px-1.5 rounded font-bold ml-1">UNVERIFIED</span>
                </div>
                <p className="text-indigo-950 font-medium relative z-10">{String(details.hypothesis)}</p>
              </div>
            )}

            {details.recommendation && (
              <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3 md:col-span-2">
                <span className="text-[11px] font-bold text-emerald-600 uppercase tracking-wider block mb-1">Recommendation</span>
                <p className="text-emerald-900 font-medium">{String(details.recommendation)}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-6 text-slate-500 gap-2 border border-dashed border-line rounded-lg">
            <AlertCircle size={24} className="text-slate-400" />
            <p className="text-sm text-center">No RCA fields in payload — see summary and citations.</p>
          </div>
        )}

        {(refs.length > 0 || details.limitations) && (
          <div className="mt-4 pt-3 border-t border-line flex flex-col gap-2">
            {refs.length > 0 && (
              <div className="flex items-start gap-2 text-xs text-slate-500">
                <BookOpen size={14} className="shrink-0 mt-0.5 text-slate-400" />
                <div><span className="font-semibold text-slate-600">Records:</span> {refs.join(", ")}</div>
              </div>
            )}
            {details.limitations && (
              <div className="flex items-start gap-2 text-xs text-amber-700">
                <AlertCircle size={14} className="shrink-0 mt-0.5" />
                <div><span className="font-semibold">Limitations:</span> {String(details.limitations)}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
