"use client";
import { useState } from "react";
export default function ChatInput({ onSend, loading, onCancel, draft, setDraft }: {
  onSend: (text: string, file?: File | null) => void; loading: boolean; onCancel?: () => void;
  draft?: string; setDraft?: (t: string) => void;  // DEL-F4: controlled mode for transcript editing
}) {
  const [inner, setInner] = useState("");
  const text = draft ?? inner;
  const setText = setDraft ?? setInner;
  const [file, setFile] = useState<File | null>(null);
  const [fileErr, setFileErr] = useState("");
  const pick = (f: File | null) => {
    setFileErr("");
    if (f && f.size > 5 * 1024 * 1024) { setFileErr("Image max 5 MB."); return; }
    if (f && !["image/png", "image/jpeg"].includes(f.type)) { setFileErr("Supported: PNG, JPEG."); return; }
    setFile(f);
  };
  return (
    <form className="border-t border-line bg-white p-3 flex gap-2 items-end"
      onSubmit={(e) => {
        e.preventDefault();
        if (loading || (!text.trim() && !file)) return;
        if (text.length > 4000) return;
        onSend(text, file); setText(""); setFile(null);
      }}>
      <div className="flex flex-col gap-1">
        <input type="file" accept="image/png,image/jpeg" aria-label="Attach image"
          onChange={(e) => pick(e.target.files?.[0] || null)} className="text-xs max-w-[160px]" />
        {file && <button type="button" onClick={() => setFile(null)} className="text-[11px] underline text-left">Remove {file.name}</button>}
        {fileErr && <span className="text-[11px] text-red-600">{fileErr}</span>}
      </div>
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} maxLength={4000}
        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); (e.target as HTMLTextAreaElement).form?.requestSubmit(); } }}
        placeholder="Ask about equipment, OPL, interlock, BOM, downtime... (Shift+Enter for newline)"
        className="flex-1 border border-line rounded p-2 text-sm focus:outline-none focus:ring-1 focus:ring-industrial" />
      {loading && onCancel
        ? <button type="button" onClick={onCancel} className="border border-line px-4 py-2 rounded text-sm">Cancel</button>
        : <button disabled={loading} className="bg-industrial text-white px-4 py-2 rounded text-sm disabled:opacity-50">
            {loading ? "Sending..." : "Send"}
          </button>}
    </form>
  );
}
