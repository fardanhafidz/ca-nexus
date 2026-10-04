"use client";
/** T6.7 — Explicit contract fields; voting/delay only when evidenced;
 *  unknown shown as "unknown", never as 0/false/normal. */
const U = (v: unknown) => (v === null || v === undefined || v === "" ? "unknown" : String(v));
type Cause = { instrument_tag?: string | null; condition?: string | null; comparator?: string | null;
  setpoint?: string | null; unit?: string | null; voting?: string | null; delay?: string | null; effect?: string | null;
  source?: string | null };
export default function InterlockLogicCard({ details }: { details: Record<string, unknown> }) {
  const rows = ((details.causes as Cause[]) || (details.rows as Cause[]) || []) as Cause[];
  const showVoting = rows.some((r) => r.voting);
  const showDelay = rows.some((r) => r.delay);
  const showSource = rows.some((r) => r.source);  // DEL-F6: per-relation source when provided
  return (
    <div className="border rounded p-2">
      <p className="font-semibold text-sm">{String(details.interlock_id || details.title || "Interlock Logic")}</p>
      {details.reset ? <p className="text-xs text-slate-500">Reset: {String(details.reset)}</p> : null}
      {rows.length > 0 ? (
        <table className="text-xs w-full mt-1">
          <thead><tr className="bg-canvas">
            <th className="p-1 border">Instrument</th><th className="p-1 border">Condition</th>
            <th className="p-1 border">Setpoint</th>
            {showVoting && <th className="p-1 border">Voting</th>}
            {showDelay && <th className="p-1 border">Delay</th>}
            <th className="p-1 border">Effect</th>
            {showSource && <th className="p-1 border">Source</th>}
          </tr></thead>
          <tbody>{rows.map((r) => {
            const rowKey = `${r.instrument_tag || "?"}|${r.condition || r.comparator || ""}|${r.effect || ""}`;
            return (
            <tr key={rowKey}>
              <td className="p-1 border">{U(r.instrument_tag)}</td>
              <td className="p-1 border">{U(r.condition || (r.comparator ? `${r.comparator}` : null))}</td>
              <td className="p-1 border">{r.setpoint ? `${r.setpoint}${r.unit ? ` ${r.unit}` : ""}` : "unknown"}</td>
              {showVoting && <td className="p-1 border">{U(r.voting)}</td>}
              {showDelay && <td className="p-1 border">{U(r.delay)}</td>}
              <td className="p-1 border">{U(r.effect)}</td>
              {showSource && <td className="p-1 border text-slate-500">{r.source || "—"}</td>}
            </tr>
            );
          })}</tbody>
        </table>
      ) : <p className="text-xs text-slate-500">No cause rows in payload — see summary and citations.</p>}
    </div>
  );
}
