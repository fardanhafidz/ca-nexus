"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { API, ApiError } from "@/lib/api";
export default function Login() {
  const r = useRouter();
  const [id, setId] = useState(""); const [pw, setPw] = useState("");
  const [err, setErr] = useState(""); const [busy, setBusy] = useState(false);
  return (
    <main className="min-h-screen flex items-center justify-center bg-canvas p-4">
      <form className="bg-white border border-line rounded p-6 w-96 space-y-3"
        onSubmit={async (e) => {
          e.preventDefault(); setErr(""); setBusy(true);
          try {
            // T6.3: exactly one identity field — email iff it looks like one
            const body = id.includes("@")
              ? { email: id, password: pw }
              : { employee_id: id, password: pw };
            const res = await fetch(`${API}/api/v1/auth/login`, {
              method: "POST", headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify(body),
            });
            if (!res.ok) {
              if (res.status === 403) { r.push("/pending"); return; }  // pending/disabled → status page
              if (res.status === 401) throw new ApiError(401, "Wrong ID/email or password.");
              throw new ApiError(res.status, await res.text());
            }
            await res.json();  // session cookie is httpOnly — nothing to store in JS
            r.push("/chat");
          } catch (ex) { setErr(ex instanceof ApiError ? ex.message : "Login failed."); }
          setBusy(false);
        }}>
        <h1 className="font-bold text-lg text-industrial">Manufacturing Knowledge Hub</h1>
        <p className="text-xs text-slate-500">Sign in with Employee ID or email.</p>
        <input value={id} onChange={(e) => setId(e.target.value)} placeholder="Employee ID / email" required aria-label="Employee ID or email" className="w-full border rounded p-2 text-sm" />
        <input value={pw} onChange={(e) => setPw(e.target.value)} type="password" placeholder="Password" required minLength={8} aria-label="Password" className="w-full border rounded p-2 text-sm" />
        {err && <p role="alert" className="text-xs text-red-600">{err}</p>}
        <button disabled={busy} className="w-full bg-industrial text-white rounded p-2 text-sm disabled:opacity-50">{busy ? "Signing in..." : "Login"}</button>
        <a href="/register" className="text-xs text-industrial underline">Register</a>
      </form>
    </main>
  );
}
