"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { API } from "@/lib/api";
const DIVS = ["Mechanical", "Electrical & Instrumentation", "Process / Operations", "HSE & Reliability"];
type RegForm = { full_name: string; employee_id: string; email: string; password: string; division_requested: string };
const TEXT_FIELDS = ["full_name", "employee_id", "email", "password"] as const;
export default function Register() {
  const r = useRouter();
  const [f, setF] = useState<RegForm>({ full_name: "", employee_id: "", email: "", password: "", division_requested: DIVS[0] });
  const [msg, setMsg] = useState("");
  const set = (k: keyof RegForm, v: string) => setF({ ...f, [k]: v });
  return (
    <main className="min-h-screen flex items-center justify-center bg-canvas p-4">
      <form className="bg-white border rounded p-6 w-96 space-y-2"
        onSubmit={async (e) => {
          e.preventDefault();
          const res = await fetch(`${API}/api/v1/auth/register`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(f),
          });
          if (!res.ok) return setMsg(await res.text());
          r.push("/pending");
        }}>
        <h1 className="font-bold text-industrial">Register</h1>
        {(TEXT_FIELDS).map((k) => (
          <input key={k} type={k === "password" ? "password" : "text"} placeholder={k}
            value={f[k]} onChange={(e) => set(k, e.target.value)}
            className="w-full border rounded p-2 text-sm" />
        ))}
        <select value={f.division_requested} onChange={(e) => set("division_requested", e.target.value)} className="w-full border rounded p-2 text-sm">
          {DIVS.map((d) => <option key={d}>{d}</option>)}
        </select>
        {msg && <p className="text-xs text-red-600">{msg}</p>}
        <button className="w-full bg-industrial text-white rounded p-2 text-sm">Submit</button>
      </form>
    </main>
  );
}
