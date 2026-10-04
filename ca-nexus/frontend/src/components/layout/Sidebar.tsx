"use client";
import { useState } from "react";
import { api, ApiError } from "@/lib/api";

export type SessionItem = { id: string; title: string };

export default function Sidebar({ sessions, active, onSelect, onNew, onChanged, collapsed, onToggle }: {
  sessions: SessionItem[]; active: string | null;
  onSelect: (id: string) => void; onNew: () => void;
  onChanged: () => void; collapsed: boolean; onToggle: () => void;
}) {
  const [q, setQ] = useState("");
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [err, setErr] = useState("");
  if (collapsed) {
    return (
      <aside className="w-10 border-r border-line bg-white p-1 shrink-0 hidden md:block">
        <button onClick={onToggle} aria-label="Expand history" className="p-1.5 text-sm w-full">»</button>
      </aside>
    );
  }
  const shown = q
    ? sessions.filter((s) => (s.title || "").toLowerCase().includes(q.toLowerCase()))
    : sessions;
  const act = async (fn: () => Promise<unknown>) => {
    setErr("");
    try { await fn(); onChanged(); } catch (e) { setErr(e instanceof ApiError ? e.message : "Action failed."); }
  };
  return (
    <aside className="w-60 border-r border-line bg-white p-3 flex-col gap-2 overflow-auto shrink-0 hidden md:flex">
      <div className="flex gap-1">
        <button onClick={onNew} className="flex-1 bg-industrial text-white rounded px-3 py-2 text-sm">New Session</button>
        <button onClick={onToggle} aria-label="Collapse history" className="border rounded px-2 text-sm">«</button>
      </div>
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search history..." aria-label="Search history"
        className="border border-line rounded p-1.5 text-sm" />
      {err && <p role="alert" className="text-xs text-red-600">{err}</p>}
      {shown.length === 0 && <p className="text-sm text-slate-500">{q ? "No matching sessions." : "No history yet."}</p>}
      {shown.map((s) => (
        <div key={s.id} className={`text-sm p-2 rounded border ${active === s.id ? "border-industrial bg-canvas" : "border-line"}`}>
          {editing === s.id ? (
            <form onSubmit={(e) => {
              e.preventDefault();
              if (draft.trim()) act(() => api(`/api/v1/chat/sessions/${s.id}`, { method: "PATCH", body: JSON.stringify({ title: draft.trim() }) }));
              setEditing(null);
            }} className="flex gap-1">
              <input value={draft} onChange={(e) => setDraft(e.target.value)} maxLength={120} autoFocus
                aria-label="Session title" className="flex-1 border rounded px-1 text-sm min-w-0" />
              <button className="text-xs text-industrial underline">Save</button>
            </form>
          ) : (
            <div className="flex gap-1 items-center">
              <button onClick={() => onSelect(s.id)} className="flex-1 text-left truncate">{s.title || s.id.slice(0, 8)}</button>
              <button aria-label={`Rename ${s.title || s.id}`} title="Rename"
                onClick={() => { setEditing(s.id); setDraft(s.title || ""); }} className="text-xs text-slate-400 hover:text-industrial">✎</button>
              <button aria-label={`Delete ${s.title || s.id}`} title="Delete"
                onClick={() => { if (confirm("Delete this session and its messages?")) act(() => api(`/api/v1/chat/sessions/${s.id}`, { method: "DELETE" })); }}
                className="text-xs text-slate-400 hover:text-red-600">✕</button>
            </div>
          )}
        </div>
      ))}
    </aside>
  );
}
