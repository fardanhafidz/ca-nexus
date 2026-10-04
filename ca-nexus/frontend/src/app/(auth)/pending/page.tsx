"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";

export default function Pending() {
  const r = useRouter();
  const [err, setErr] = useState("");
  useEffect(() => {
    let stop = false;
    const check = async () => {
      try {
        await api("/api/v1/auth/me");  // cookie-attached; 200 means approved since
        r.push("/chat");
      } catch (e) {
        if (e instanceof ApiError && e.status === 403) return;  // still pending — keep waiting
        if (!stop) setErr(e instanceof ApiError ? e.message : "Cannot reach backend — retrying...");
      }
    };
    check();
    const t = setInterval(check, 5000);
    return () => { stop = true; clearInterval(t); };
  }, [r]);
  const logout = async () => {
    try {
      await api("/api/v1/auth/logout", { method: "POST" });
    } catch {
      // Best effort: cookie may already be expired; login page is the safe landing.
    }
    r.push("/login");
  };
  return (
    <main className="min-h-screen flex items-center justify-center bg-canvas">
      <div className="bg-white border rounded p-6 text-sm space-y-2 w-96">
        <h1 className="font-bold text-industrial">Pending Approval</h1>
        <p>Your account is waiting for admin approval. This page refreshes automatically.</p>
        {err && <p role="alert" className="text-xs text-red-600">{err}</p>}
        <div className="flex gap-2">
          <a href="/login" className="text-industrial underline text-xs">Back to login</a>
          <button onClick={logout} className="text-xs border rounded px-2 py-0.5">Log out</button>
        </div>
      </div>
    </main>
  );
}
