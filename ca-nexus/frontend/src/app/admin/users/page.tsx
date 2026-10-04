"use client";
import { useEffect, useState } from "react";
import AppSidebar from "@/components/layout/AppSidebar";
import { api, ApiError } from "@/lib/api";
import { ChevronRight, HelpCircle, Check, X, ShieldAlert, Users, UserX } from "lucide-react";

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
    <div className="flex h-screen w-full bg-canvas">
      <AppSidebar />
      <main className="flex-1 flex flex-col bg-canvas min-w-0 overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-line px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">CA Nexus</span>
            <ChevronRight size={14} className="text-slate-400" />
            <span className="font-semibold text-slate-800">Personnel Clearance</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 border border-emerald-100 rounded-full text-emerald-700 text-xs font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.5)]"></span>
              Node #04 Active
            </div>
            <button className="text-slate-400 hover:text-slate-700 transition-colors"><HelpCircle size={20} /></button>
            <div className="w-8 h-8 rounded-full bg-slate-200 overflow-hidden shadow-sm flex items-center justify-center font-bold text-slate-500 text-xs">
              AD
            </div>
          </div>
        </header>

        <div className="p-8 max-w-6xl mx-auto w-full space-y-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 tracking-tight mb-2">Personnel Clearance</h1>
              <p className="text-slate-500 text-base">Review and approve factory data access requests.</p>
            </div>
            <div className="flex bg-slate-100 p-1 rounded-xl shadow-inner text-sm font-medium">
              <button onClick={() => setFilter("pending")} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${filter === "pending" ? "bg-white text-blue-600 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}>
                <ShieldAlert size={16} /> Pending
              </button>
              <button onClick={() => setFilter("approved")} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${filter === "approved" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}>
                <Users size={16} /> Active
              </button>
              <button onClick={() => setFilter("disabled")} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${filter === "disabled" ? "bg-white text-red-600 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}>
                <UserX size={16} /> Suspended
              </button>
            </div>
          </div>

          {err && <div role="alert" className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl shadow-sm text-sm">{err}</div>}

          <div className="bg-white border border-line rounded-2xl shadow-sm overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-5 border-b border-line bg-slate-50/50">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                {filter === "pending" ? "Pending Requests Awaiting Verification" : filter === "approved" ? "Active Personnel" : "Suspended Accounts"}
                <span className="text-xs font-bold text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full">{users.length} items</span>
              </h2>
              <span className="text-xs font-medium text-slate-400">Sorted by submission date</span>
            </div>
            
            <div className="divide-y divide-line">
              {users.map((u) => (
                <div key={u.id} className={`p-5 flex items-center gap-5 transition-colors ${selected.includes(u.id) ? "bg-blue-50/50" : "hover:bg-slate-50"}`}>
                  <input type="checkbox" aria-label={`Select ${u.email}`} checked={selected.includes(u.id)} onChange={() => toggle(u.id)} className="w-4 h-4 rounded border-slate-300 text-industrial focus:ring-industrial" />
                  
                  <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-slate-200 to-slate-300 flex items-center justify-center font-bold text-slate-600 text-lg shadow-inner shrink-0">
                    {u.full_name.charAt(0).toUpperCase()}
                  </div>
                  
                  <div className="flex-1 min-w-0 cursor-pointer" onClick={async () => setDetail(await api(`/api/v1/admin/users/${u.id}`))}>
                    <div className="flex items-center gap-3 mb-1.5 flex-wrap">
                      <span className="font-bold text-slate-900 text-base">{u.full_name}</span>
                      <span className="text-xs font-mono font-medium text-slate-500 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded">#{u.employee_id}</span>
                      <span className="text-xs font-semibold text-industrial bg-cyan-50 border border-cyan-100 px-2 py-0.5 rounded-full">{u.division_requested || u.division} • Level 2</span>
                    </div>
                    <div className="text-sm text-slate-500 flex items-center gap-2 flex-wrap">
                      <span className="text-slate-700 font-medium">{u.email}</span>
                      <span className="text-slate-300">•</span>
                      <span>{u.role}</span>
                      <span className="text-slate-300">•</span>
                      <span>Status: {u.status}</span>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2 shrink-0">
                    {filter === "pending" && (
                      <div className="flex items-center gap-2">
                        <select value={division} onChange={(e) => setDivision(e.target.value)} aria-label="Division to allocate" className="border border-line rounded-lg text-xs p-2 bg-white shadow-sm focus:outline-none focus:ring-1 focus:ring-industrial">
                          {DIVISIONS.map((d) => <option key={d}>{d}</option>)}
                        </select>
                        <button disabled={busy !== null} onClick={() => act(`rj-${u.id}`, `/api/v1/admin/users/${u.id}/reject`)} className="px-4 py-2 bg-white border border-line rounded-lg text-sm font-semibold text-slate-600 shadow-sm hover:bg-slate-50 transition-colors disabled:opacity-50">
                          Decline
                        </button>
                        <button disabled={busy !== null} onClick={() => act(`ap-${u.id}`, `/api/v1/admin/users/${u.id}/approve`, { division })} className="px-4 py-2 bg-industrial hover:bg-industrial-dark text-white rounded-lg text-sm font-semibold shadow-md transition-colors disabled:opacity-50">
                          {busy === `ap-${u.id}` ? "..." : "Approve"}
                        </button>
                      </div>
                    )}
                    
                    {myRole === "super_admin" && filter !== "pending" && (
                      <div className="flex items-center gap-2">
                        <select value={rolePick} onChange={(e) => setRolePick(e.target.value)} aria-label="Role to assign" className="border border-line rounded-lg text-xs p-2 bg-white shadow-sm focus:outline-none">
                          {["user", "admin", "super_admin"].map((r) => <option key={r}>{r}</option>)}
                        </select>
                        <button disabled={busy !== null} onClick={() => act(`rl-${u.id}`, `/api/v1/admin/users/${u.id}/status`, { status: u.status, role: rolePick })} className="px-3 py-2 bg-white border border-line rounded-lg text-xs font-semibold text-slate-600 shadow-sm hover:bg-slate-50 disabled:opacity-50">
                          Set role
                        </button>
                        {u.status === "approved" ? (
                          <button disabled={busy !== null} onClick={() => act(`dis-${u.id}`, `/api/v1/admin/users/${u.id}/status`, { status: "disabled", role: u.role })} className="px-3 py-2 bg-white border border-red-200 text-red-600 rounded-lg text-xs font-semibold shadow-sm hover:bg-red-50 disabled:opacity-50">
                            Suspend
                          </button>
                        ) : (
                          <button disabled={busy !== null} onClick={() => act(`ap-${u.id}`, `/api/v1/admin/users/${u.id}/approve`, { division: u.division })} className="px-3 py-2 bg-white border border-emerald-200 text-emerald-600 rounded-lg text-xs font-semibold shadow-sm hover:bg-emerald-50 disabled:opacity-50">
                            Re-activate
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {users.length === 0 && (
                <div className="p-12 text-center text-slate-500">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <ShieldAlert size={32} className="text-slate-400" />
                  </div>
                  <p className="text-base font-medium text-slate-900 mb-1">No personnel found</p>
                  <p className="text-sm">There are no users matching the '{filter}' status.</p>
                </div>
              )}
            </div>
            
            <div className="p-4 bg-slate-50 border-t border-line text-xs font-medium text-slate-400 text-center">
              {filter === "pending" ? "Requests automatically expire if unreviewed after 7 days" : "All personnel identity checks verified via SSO"}
            </div>
          </div>

          {selected.length > 0 && (
            <div className="bg-white border border-line rounded-xl shadow-md p-4 flex items-center justify-between sticky bottom-6 animate-in fade-in slide-in-from-bottom-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold flex items-center justify-center text-sm">{selected.length}</div>
                <span className="text-sm font-semibold text-slate-700">Personnel Selected</span>
              </div>
              <div className="flex gap-3">
                {filter === "pending" && (
                  <select value={division} onChange={(e) => setDivision(e.target.value)} aria-label="Division to allocate" className="border border-line rounded-lg text-sm px-3 bg-white shadow-sm focus:outline-none">
                    {DIVISIONS.map((d) => <option key={d}>{d}</option>)}
                  </select>
                )}
                <button disabled={busy !== null} onClick={() => act("bulk-rj", "/api/v1/admin/users/bulk", { ids: selected, status: filter === "pending" ? "rejected" : "disabled" })} className="px-5 py-2.5 bg-white border border-red-200 text-red-600 rounded-lg text-sm font-semibold shadow-sm hover:bg-red-50 disabled:opacity-50">
                  {filter === "pending" ? "Bulk Reject" : "Bulk Suspend"}
                </button>
                {filter !== "approved" && (
                  <button disabled={busy !== null} onClick={() => act("bulk-ap", "/api/v1/admin/users/bulk", { ids: selected, status: "approved", division })} className="px-5 py-2.5 bg-industrial hover:bg-industrial-dark text-white rounded-lg text-sm font-semibold shadow-md disabled:opacity-50 flex items-center gap-2">
                    <Check size={16} /> Bulk Approve
                  </button>
                )}
              </div>
            </div>
          )}

          {detail && (
            <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
                <div className="p-5 border-b border-line flex justify-between items-center">
                  <h3 className="font-bold text-slate-900 text-lg">Personnel Details</h3>
                  <button onClick={() => setDetail(null)} className="text-slate-400 hover:text-slate-700"><X size={20} /></button>
                </div>
                <div className="p-6 overflow-auto">
                  <pre className="text-xs bg-slate-50 border border-line rounded-lg p-4 overflow-auto font-mono text-slate-700">{JSON.stringify(detail, null, 2)}</pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
