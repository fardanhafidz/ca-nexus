"use client";
import { useState } from "react";
import { Package, Search, ArrowDownAZ, ArrowUpAZ, AlertCircle } from "lucide-react";

const U = (v: unknown) => (v === null || v === undefined || v === "" ? "unknown" : String(v));
type Item = { item_no?: string | null; description?: string; part_number?: string | null;
  quantity?: string | null; unit?: string | null; material?: string | null; source?: string | null };

export default function SparePartBOMTable({ details }: { details: Record<string, unknown> }) {
  const rows = ((details.items as Item[]) || (details.rows as Item[]) || []) as Item[];
  const [sortAsc, setSortAsc] = useState(true);
  const [filter, setFilter] = useState("");
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
    <div className="bg-white border border-line rounded-xl shadow-sm overflow-hidden my-3">
      <div className="bg-slate-50 border-b border-line p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-teal-100 text-teal-600 flex items-center justify-center shrink-0">
            <Package size={18} />
          </div>
          <div>
            <p className="font-bold text-slate-800 leading-tight">{String(details.drawing || details.title || "Spare Part BOM")}</p>
            {details.revision ? <p className="text-[11px] font-medium text-slate-500 mt-0.5">Revision {String(details.revision)}</p> : null}
          </div>
        </div>
        
        {rows.length > 0 && (
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setSortAsc(!sortAsc)} 
              className="p-1.5 border border-line rounded-md bg-white text-slate-600 hover:bg-slate-50 transition-colors"
              title={`Sort ${sortAsc ? "Descending" : "Ascending"}`}
            >
              {sortAsc ? <ArrowDownAZ size={16}/> : <ArrowUpAZ size={16}/>}
            </button>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-slate-400">
                <Search size={14} />
              </div>
              <input 
                value={filter} 
                onChange={(e) => setFilter(e.target.value)} 
                placeholder="Filter parts..." 
                className="border border-line rounded-md pl-8 pr-3 py-1.5 text-xs bg-white focus:outline-none focus:border-industrial focus:ring-1 focus:ring-industrial/30 w-full sm:w-48 transition-all shadow-sm" 
              />
            </div>
          </div>
        )}
      </div>

      <div className="p-0 overflow-x-auto">
        {rows.length > 0 ? (
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 bg-slate-50 border-b border-line uppercase font-semibold">
              <tr>
                <th className="px-4 py-3 whitespace-nowrap">Item</th>
                <th className="px-4 py-3 whitespace-nowrap min-w-[200px]">Description</th>
                <th className="px-4 py-3 whitespace-nowrap">Part No</th>
                <th className="px-4 py-3 whitespace-nowrap text-center">Qty</th>
                <th className="px-4 py-3 whitespace-nowrap">Material</th>
                {showSource && <th className="px-4 py-3 whitespace-nowrap text-right">Source</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {sorted.map((r) => {
                const rowKey = `${r.item_no || "?"}|${r.description || ""}|${r.part_number || ""}`;
                const hasValue = (val: string) => val !== "unknown" && val !== "—";
                const qtyVal = r.quantity === null || r.quantity === undefined || r.quantity === "" ? "unknown" : String(r.quantity);
                
                return (
                  <tr key={rowKey} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center justify-center min-w-[24px] h-6 px-1.5 rounded bg-slate-100 text-slate-700 font-bold text-xs">
                        {U(r.item_no)}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-800">{U(r.description)}</td>
                    <td className="px-4 py-3 font-mono text-industrial font-semibold text-xs">{U(r.part_number)}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-bold ${qtyVal === "unknown" ? "bg-slate-100 text-slate-400 italic" : "bg-teal-50 text-teal-700 border border-teal-100"}`}>
                        {qtyVal}{r.unit && qtyVal !== "unknown" ? ` ${r.unit}` : ""}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600 text-xs">
                      {hasValue(U(r.material)) ? U(r.material) : <span className="text-slate-400 italic">unknown</span>}
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
            <p className="text-sm">No BOM rows in payload — see summary and citations.</p>
          </div>
        )}
        
        {rows.length > 0 && sorted.length === 0 && (
          <div className="flex flex-col items-center justify-center p-8 text-slate-500 bg-slate-50/50">
            <Search size={24} className="text-slate-300 mb-2" />
            <p className="text-sm font-medium">No parts match your filter</p>
            <button onClick={() => setFilter("")} className="text-xs text-industrial hover:underline mt-1">Clear filter</button>
          </div>
        )}
      </div>
    </div>
  );
}
