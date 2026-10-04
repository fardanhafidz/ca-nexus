"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Network, MessageSquare, BookOpen, Settings, ShieldCheck, ChevronDown, Plus, History, Sun, Settings2, PanelLeftClose } from "lucide-react";
import { api } from "@/lib/api";

type SessionItem = { id: string; title: string };

const NAV_ITEMS = [
  { href: "/chat", icon: <MessageSquare size={18} />, label: "Chat & Synthesis", roles: ["user", "admin", "super_admin"] },
  { href: "/knowledge", icon: <BookOpen size={18} />, label: "Knowledge Base", roles: ["user", "admin", "super_admin"] },
  { href: "/admin/docs", icon: <Settings size={18} />, label: "Ingestion Pipeline", roles: ["admin", "super_admin"] },
  { href: "/admin/users", icon: <ShieldCheck size={18} />, label: "Personnel Clearance", roles: ["admin", "super_admin"] },
];

export default function AppSidebar({ activeSessionId }: { activeSessionId?: string | null }) {
  const path = usePathname();
  const router = useRouter();
  const [role, setRole] = useState("user");
  const [user, setUser] = useState<{name?: string, division?: string}>({});
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    api("/api/v1/auth/me").then((u) => {
      setRole(u.role);
      setUser(u);
    }).catch(() => setRole("user"));
    
    api("/api/v1/chat/sessions").then(setSessions).catch(() => {});
  }, []);

  const items = NAV_ITEMS.filter((i) => i.roles.includes(role));

  if (collapsed) {
    return (
      <aside className="w-16 bg-industrial text-white flex flex-col items-center py-4 shrink-0 h-screen overflow-y-auto">
        <button onClick={() => setCollapsed(false)} className="hover:bg-white/10 p-2 rounded mb-6">
          <Network size={24} />
        </button>
        {items.map((i) => {
          const active = path === i.href || path.startsWith(i.href + "/");
          return (
            <Link key={i.href} href={i.href} title={i.label} className={`p-3 rounded mb-2 hover:bg-white/10 ${active ? "bg-white/20" : ""}`}>
              {i.icon}
            </Link>
          );
        })}
      </aside>
    );
  }

  return (
    <aside className="w-[260px] bg-industrial text-white flex flex-col shrink-0 h-screen overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 pt-5">
        <div className="flex items-center gap-2 font-semibold text-lg">
          <Network size={20} className="text-white/90" />
          <span>CA Nexus</span>
        </div>
        <button onClick={() => setCollapsed(true)} className="text-white/70 hover:text-white">
          <PanelLeftClose size={18} />
        </button>
      </div>

      {/* New Chat Button */}
      <div className="px-4 mb-4">
        <button 
          onClick={() => router.push("/chat?new=true")}
          className="w-full py-2.5 px-4 bg-industrial-light hover:bg-white/20 transition-colors rounded-full flex items-center justify-center gap-2 text-sm font-medium border border-white/10"
        >
          <Plus size={16} /> New Chat
        </button>
      </div>

      {/* Main Nav */}
      <div className="px-3 flex flex-col gap-1 mb-6">
        {items.map((i) => {
          const active = path === i.href || path.startsWith(i.href + "/");
          return (
            <Link key={i.href} href={i.href} className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${active ? "bg-white/15 text-white" : "text-white/80 hover:bg-white/10 hover:text-white"}`}>
              {i.icon}
              {i.label}
            </Link>
          );
        })}
      </div>

      {/* Recent Investigations */}
      <div className="flex-1 overflow-y-auto px-3">
        <div className="flex items-center justify-between px-3 py-2 text-xs font-semibold text-white/50 tracking-wider mb-1">
          RECENT INVESTIGATIONS
          <ChevronDown size={14} />
        </div>
        <div className="flex flex-col gap-0.5">
          {sessions.length === 0 && <div className="px-3 py-2 text-xs text-white/40">No history yet.</div>}
          {sessions.map((s) => (
            <Link 
              key={s.id} 
              href={`/chat?id=${s.id}`} 
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm truncate transition-colors ${activeSessionId === s.id ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5 hover:text-white"}`}
            >
              <History size={14} className="shrink-0 opacity-60" />
              <span className="truncate">{s.title || s.id.slice(0, 8)}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* User Profile */}
      <div className="p-4 bg-industrial-dark/30 border-t border-white/10 mt-auto flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-500 flex items-center justify-center text-sm font-bold shadow-sm shrink-0 overflow-hidden">
          {/* Default avatar, in real app would use image */}
          {user.name ? user.name.charAt(0) : "U"}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{user.name || "User"}</div>
          <div className="text-xs text-white/60 truncate">{user.division || "Division"}</div>
        </div>
        <div className="flex items-center gap-1 text-white/50">
          <button className="p-1.5 hover:text-white hover:bg-white/10 rounded-md transition-colors"><Sun size={14} /></button>
          <button className="p-1.5 hover:text-white hover:bg-white/10 rounded-md transition-colors"><Settings2 size={14} /></button>
        </div>
      </div>
    </aside>
  );
}
