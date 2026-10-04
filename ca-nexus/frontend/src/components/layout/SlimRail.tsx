"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Factory, MessageSquare, BookOpen, Users, FileUp } from "lucide-react";
import { api } from "@/lib/api";

const ALL_ITEMS = [
  { href: "/chat", icon: <MessageSquare size={20} />, label: "Chat", roles: ["user", "admin", "super_admin"] },
  { href: "/knowledge", icon: <BookOpen size={20} />, label: "Knowledge", roles: ["user", "admin", "super_admin"] },
  { href: "/admin/users", icon: <Users size={20} />, label: "Users", roles: ["admin", "super_admin"] },
  { href: "/admin/docs", icon: <FileUp size={20} />, label: "Docs", roles: ["admin", "super_admin"] },
];

export default function SlimRail() {
  const path = usePathname();
  const [role, setRole] = useState("user");
  useEffect(() => {
    // Role fetch is best-effort: failure keeps the safe default (user-only nav).
    api("/api/v1/auth/me").then((u) => setRole(u.role)).catch(() => setRole("user"));
  }, []);
  const items = ALL_ITEMS.filter((i) => i.roles.includes(role));
  return (
    <nav aria-label="Primary" className="w-14 bg-industrial text-white hidden sm:flex flex-col items-center py-3 gap-2 shrink-0">
      <Factory size={22} className="mb-2" />
      {items.map((i) => {
        const active = path === i.href || path.startsWith(i.href + "/");
        return (
          <Link key={i.href} href={i.href} title={i.label} aria-label={i.label} aria-current={active ? "page" : undefined}
            className={`p-2 rounded hover:bg-white/20 ${active ? "bg-white/25 ring-1 ring-white/60" : ""}`}>
            {i.icon}
          </Link>
        );
      })}
    </nav>
  );
}
