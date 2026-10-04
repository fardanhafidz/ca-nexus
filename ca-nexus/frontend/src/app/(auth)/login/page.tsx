"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { API, ApiError } from "@/lib/api";
import { Network, Lock, User, ArrowRight } from "lucide-react";

export default function Login() {
  const r = useRouter();
  const [id, setId] = useState(""); const [pw, setPw] = useState("");
  const [err, setErr] = useState(""); const [busy, setBusy] = useState(false);
  return (
    <main className="min-h-screen flex items-center justify-center bg-canvas p-4 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-industrial/5 blur-3xl" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-500/5 blur-3xl" />
      
      <form className="bg-white border border-line rounded-3xl p-10 w-full max-w-md shadow-xl z-10"
        onSubmit={async (e) => {
          e.preventDefault(); setErr(""); setBusy(true);
          try {
            const body = id.includes("@")
              ? { email: id, password: pw }
              : { employee_id: id, password: pw };
            const res = await fetch(`${API}/api/v1/auth/login`, {
              method: "POST", headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify(body),
            });
            if (!res.ok) {
              if (res.status === 403) { r.push("/pending"); return; }
              if (res.status === 401) throw new ApiError(401, "Wrong ID/email or password.");
              throw new ApiError(res.status, await res.text());
            }
            await res.json();
            r.push("/chat");
          } catch (ex) { setErr(ex instanceof ApiError ? ex.message : "Login failed."); }
          setBusy(false);
        }}>
        
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-tr from-industrial to-industrial-light text-white rounded-2xl flex items-center justify-center mb-4 shadow-lg">
            <Network size={32} strokeWidth={2.5} />
          </div>
          <h1 className="font-bold text-2xl text-slate-900 tracking-tight">CA Nexus</h1>
          <p className="text-sm text-slate-500 mt-1">Manufacturing Knowledge Hub</p>
        </div>

        <div className="space-y-4 mb-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <User size={18} />
            </div>
            <input 
              value={id} 
              onChange={(e) => setId(e.target.value)} 
              placeholder="Employee ID or Email" 
              required 
              className="w-full border border-line rounded-xl pl-10 pr-4 py-3 text-sm bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-industrial/20 transition-all shadow-sm" 
            />
          </div>
          
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Lock size={18} />
            </div>
            <input 
              value={pw} 
              onChange={(e) => setPw(e.target.value)} 
              type="password" 
              placeholder="Password" 
              required 
              minLength={8} 
              className="w-full border border-line rounded-xl pl-10 pr-4 py-3 text-sm bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-industrial/20 transition-all shadow-sm" 
            />
          </div>
        </div>

        {err && <div role="alert" className="bg-red-50 text-red-600 text-xs p-3 rounded-lg mb-4 border border-red-100 font-medium">{err}</div>}
        
        <button disabled={busy} className="w-full bg-industrial hover:bg-industrial-dark text-white rounded-xl p-3.5 text-sm font-bold shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:hover:shadow-md flex items-center justify-center gap-2">
          {busy ? "Authenticating..." : "Sign In"} 
          {!busy && <ArrowRight size={16} />}
        </button>
        
        <div className="mt-6 text-center text-sm text-slate-500">
          Need an access? <a href="/register" className="text-industrial font-semibold hover:underline">Request clearance</a>
        </div>
      </form>
    </main>
  );
}
