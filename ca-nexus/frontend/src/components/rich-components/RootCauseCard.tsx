"use client";
/** T6.9 — Record refs + limitations required; hypothesis always labeled unverified. */
export default function RootCauseCard({ details }: { details: Record<string, unknown> }) {
  const refs = (details.record_refs as string[]) || [];
  return (
    <div className="border rounded p-2 text-sm space-y-1">
      <p className="font-semibold">{String(details.title || "Root Cause")}</p>
      {details.anomaly ? <p><b>Anomaly:</b> {String(details.anomaly)}</p> : null}
      {details.recorded_cause ? <p><b>Recorded cause:</b> {String(details.recorded_cause)}</p> : <p className="text-slate-500">Recorded cause: unknown</p>}
      {details.hypothesis ? <p><b>AI hypothesis (unverified):</b> {String(details.hypothesis)}</p> : null}
      {details.recommendation ? <p><b>Recommendation:</b> {String(details.recommendation)}</p> : null}
      {refs.length > 0 && <p className="text-xs text-slate-500">Records: {refs.join(", ")}</p>}
      {details.limitations ? <p className="text-xs text-slate-500">Limitations: {String(details.limitations)}</p> : null}
      {!details.anomaly && !details.recorded_cause && <p className="text-xs text-slate-500">No RCA fields in payload — see summary and citations.</p>}
    </div>
  );
}
