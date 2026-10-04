"use client";
import { useEffect, useState } from "react";
import SlimRail from "@/components/layout/SlimRail";
import { api, ApiError } from "@/lib/api";

const DIVISIONS = ["Mechanical", "Electrical & Instrumentation", "Process / Operations", "HSE & Reliability"];
type U = { id: string; full_name: string; employee_id: string; email: string; role: string; division: string; division_requested: string; status: string };

export default function AdminUsers() {
  const [users, setUsers] = useState<U[]>([]);
  const [filter, setFilter] = useState("pending");
  const [detail, setDetail] = useState<U | null>(null);
  const [division, setDivision] = useState(DIVISIONS[0]);
  const [rolePick, setRolePick] = useState("admin");
  const [myRole, setMyRole] = useState("admin");
  const [selected, setSelected] = useState<string[]>([]);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState<string | null>(null);  // DEL-F9: per-action loading, no double submit
  const load = async () => {
    setErr("");
    try {
      setUsers(await api(`/api/v1/admin/users?status=${filter}`));
      try { setMyRole((await api("/api/v1/auth/me")).role); } catch { /* keep default */ }
    }
    catch (e) { setErr(e instanceof ApiError ? e.message : "Load failed."); }
  };
  useEffect(() => { load(); }, [filter]);
  const act = async (key: string, url: string, body?: object) => {
    setErr(""); setBusy(key);
    try { await api(url, { method: "POST", body: body ? JSON.stringify(body) : undefined }); await load(); }
    catch (e) { setErr(e instanceof ApiError ? e.message : "Action failed."); }
    setBusy(null);
  };
  const toggle = (id: string) => setSelected((s) => s.includes(id) ? s.filter((x) => x !== id) : [...s, id]);
  return (
    <div className="flex h-screen">
      <SlimRail />
      <main className="flex-1 bg-canvas p-4 overflow-auto">
        <h1 className="font-semibold text-industrial mb-2">User Access Control</h1>
        <div className="flex gap-2 mb-2 text-sm">
          {(["pending", "approved", "rejected", "disabled", ""] as string[]).map((s) => (
            <button key={s} onClick={() => setFilter(s)} className={`border rounded px-2 py-1 ${filter === s ? "bg-industrial text-white" : ""}`}>{s || "all"}</button>
          ))}
        </div>
        {err && <p role="alert" className="text-xs text-red-600 mb-2">{err}</p>}
        <div className="bg-white border rounded mb-2">
          {users.map((u) => (
            <div key={u.id} className="p-2 border-b text-sm flex gap-2 items-center">
              <input type="checkbox" aria-label={`Select ${u.email}`} checked={selected.includes(u.id)} onChange={() => toggle(u.id)} />
              <button onClick={async () => setDetail(await api(`/api/v1/admin/users/${u.id}`))} className="flex-1 text-left">
                <span className="font-medium">{u.full_name}</span> ({u.employee_id}) — req: {u.division_requested} → {u.division} [{u.status}/{u.role}]
              </button>
              <select value={division} onChange={(e) => setDivision(e.target.value)} aria-label="Division to allocate" className="border rounded text-xs p-1">
                {DIVISIONS.map((d) => <option key={d}>{d}</option>)}
              </select>
              <button disabled={busy !== null} onClick={() => act(`ap-${u.id}`, `/api/v1/admin/users/${u.id}/approve`, { division })} className="bg-industrial text-white px-2 py-1 rounded text-xs disabled:opacity-50">
                {busy === `ap-${u.id}` ? "..." : "Approve+allocate"}</button>
              <button disabled={busy !== null} onClick={() => act(`rj-${u.id}`, `/api/v1/admin/users/${u.id}/reject`)} className="border px-2 py-1 rounded text-xs disabled:opacity-50">Reject</button>
              {myRole === "super_admin" && (  // DEL-F9: role change gated to SuperAdmin (backend enforces too)
                <>
                  <select value={rolePick} onChange={(e) => setRolePick(e.target.value)} aria-label="Role to assign" className="border rounded text-xs p-1">
                    {["user", "admin", "super_admin"].map((r) => <option key={r}>{r}</option>)}
                  </select>
                  <button disabled={busy !== null} onClick={() => act(`rl-${u.id}`, `/api/v1/admin/users/${u.id}/status`, { status: u.status, role: rolePick })} className="border px-2 py-1 rounded text-xs disabled:opacity-50">Set role</button>
                </>
              )}
            </div>
          ))}
          {users.length === 0 && <p className="p-3 text-sm text-slate-500">No users in this filter.</p>}
        </div>
        {selected.length > 0 && (
          <div className="flex gap-2 text-sm mb-2">
            <button disabled={busy !== null} onClick={() => act("bulk-ap", "/api/v1/admin/users/bulk", { ids: selected, status: "approved", division })} className="bg-industrial text-white px-2 py-1 rounded text-xs disabled:opacity-50">Bulk approve ({selected.length})</button>
            <button disabled={busy !== null} onClick={() => act("bulk-rj", "/api/v1/admin/users/bulk", { ids: selected, status: "rejected" })} className="border px-2 py-1 rounded text-xs disabled:opacity-50">Bulk reject</button>
          </div>
        )}
        {detail && <pre className="text-xs bg-white border rounded p-2 overflow-auto">{JSON.stringify(detail, null, 2)}</pre>}
      </main>
    </div>
  );
}
