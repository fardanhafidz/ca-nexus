"use client";
import { useState } from "react";
/** T6.8 — Locked columns + drawing/revision locator; row identity kept by item_no;
 *  missing stays "unknown", real "0" stays "0". */
const U = (v: unknown) => (v === null || v === undefined || v === "" ? "unknown" : String(v));
type Item = { item_no?: string | null; description?: string; part_number?: string | null;
  quantity?: string | null; unit?: string | null; material?: string | null; source?: string | null };
export default function SparePartBOMTable({ details }: { details: Record<string, unknown> }) {
  const rows = ((details.items as Item[]) || (details.rows as Item[]) || []) as Item[];
  const [sortAsc, setSortAsc] = useState(true);
  const [filter, setFilter] = useState("");  // DEL-F6: client-side text filter, row identity kept
  const showSource = rows.some((r) => r.source);
  const filtered = rows.filter((r) => {
    if (!filter.trim()) return true;
    const hay = `${r.item_no || ""} ${r.description || ""} ${r.part_number || ""} ${r.material || ""}`.toLowerCase();
    return hay.includes(filter.trim().toLowerCase());
  });
  const sorted = [...filtered].sort((a, b) => {
    const x = String(a.item_no || ""), y = String(b.item_no || "");
    return sortAsc ? x.localeCompare(y, undefined, { numeric: true }) : y.localeCompare(x, undefined, { numeric: true });
  });
  return (
    <div className="border rounded p-2 overflow-auto">
      <p className="font-semibold text-sm">{String(details.drawing || details.title || "Spare Part BOM")}</p>
      {details.revision ? <p className="text-xs text-slate-500">Rev {String(details.revision)}</p> : null}
      {rows.length > 0 ? (
        <>
          <div className="flex gap-2 items-center mt-1">
            <button onClick={() => setSortAsc(!sortAsc)} className="text-[11px] underline">Sort by item {sortAsc ? "desc" : "asc"}</button>
            <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filter parts..." aria-label="Filter parts"
              className="border rounded px-1 py-0.5 text-[11px] flex-1" />
          </div>
          <table className="text-xs w-full mt-1">
            <thead><tr className="bg-canvas">
              <th className="p-1 border">Item</th><th className="p-1 border">Description</th>
              <th className="p-1 border">Part No</th><th className="p-1 border">Qty</th><th className="p-1 border">Material</th>
              {showSource && <th className="p-1 border">Source</th>}
            </tr></thead>
            <tbody>{sorted.map((r) => {
              const rowKey = `${r.item_no || "?"}|${r.description || ""}|${r.part_number || ""}`;
              return (
              <tr key={rowKey}>
                <td className="p-1 border">{U(r.item_no)}</td>
                <td className="p-1 border">{U(r.description)}</td>
                <td className="p-1 border">{U(r.part_number)}</td>
                <td className="p-1 border">{r.quantity === null || r.quantity === undefined || r.quantity === "" ? "unknown" : String(r.quantity)}{r.unit ? ` ${r.unit}` : ""}</td>
                <td className="p-1 border">{U(r.material)}</td>
                {showSource && <td className="p-1 border text-slate-500">{r.source || "—"}</td>}
              </tr>
              );
            })}</tbody>
          </table>
          {sorted.length === 0 && <p className="text-[11px] text-slate-500 mt-1">No rows match the filter.</p>}
        </>
      ) : <p className="text-xs text-slate-500">No BOM rows in payload — see summary and citations.</p>}
    </div>
  );
}
