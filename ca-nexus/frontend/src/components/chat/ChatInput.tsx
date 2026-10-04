"use client";
import { useState, useRef } from "react";
import { Plus, Mic, ArrowUp, Square } from "lucide-react";

export default function ChatInput({ onSend, loading, onCancel, draft, setDraft }: {
  onSend: (text: string, file?: File | null) => void; loading: boolean; onCancel?: () => void;
  draft?: string; setDraft?: (t: string) => void;
}) {
  const [inner, setInner] = useState("");
  const text = draft ?? inner;
  const setText = setDraft ?? setInner;
  const [file, setFile] = useState<File | null>(null);
  const [fileErr, setFileErr] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const pick = (f: File | null) => {
    setFileErr("");
    if (f && f.size > 5 * 1024 * 1024) { setFileErr("Image max 5 MB."); return; }
    if (f && !["image/png", "image/jpeg"].includes(f.type)) { setFileErr("Supported: PNG, JPEG."); return; }
    setFile(f);
  };

  const handleSend = () => {
    if (loading || (!text.trim() && !file)) return;
    if (text.length > 4000) return;
    onSend(text, file); setText(""); setFile(null);
  };

  return (
    <div className="bg-canvas border-t border-line/50 p-4 pb-6 flex flex-col items-center">
      <div className="w-full max-w-4xl mx-auto flex flex-col relative">
        {fileErr && <span className="text-[11px] text-red-600 mb-1 absolute -top-5">{fileErr}</span>}
        {file && (
          <div className="absolute -top-10 left-0 bg-white border border-line rounded-lg px-3 py-1.5 text-xs flex items-center gap-2 shadow-sm">
            <span className="truncate max-w-[150px] font-medium text-slate-700">{file.name}</span>
            <button type="button" onClick={() => setFile(null)} className="text-slate-400 hover:text-red-500 rounded-full bg-slate-100 p-0.5">&times;</button>
          </div>
        )}
        
        <div className="relative flex items-center bg-white border border-line rounded-full shadow-sm pr-2 pl-4 py-2 hover:border-slate-300 focus-within:border-industrial focus-within:ring-1 focus-within:ring-industrial/30 transition-all">
          <button 
            type="button" 
            onClick={() => fileInputRef.current?.click()}
            className="text-slate-400 hover:text-slate-600 p-1.5 transition-colors shrink-0"
            aria-label="Attach file"
          >
            <Plus size={20} />
          </button>
          <input 
            type="file" 
            accept="image/png,image/jpeg" 
            ref={fileInputRef}
            onChange={(e) => pick(e.target.files?.[0] || null)} 
            className="hidden" 
          />
          
          <input 
            value={text} 
            onChange={(e) => setText(e.target.value)} 
            maxLength={4000}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Ask CA Nexus..."
            className="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 text-sm px-3 text-slate-800 placeholder:text-slate-400" 
          />
          
          <div className="flex items-center gap-1 shrink-0">
            <button type="button" className="text-slate-400 hover:text-slate-600 p-2 transition-colors" title="Voice input">
              <Mic size={20} />
            </button>
            {loading && onCancel ? (
              <button 
                type="button" 
                onClick={onCancel} 
                className="bg-slate-100 text-slate-600 hover:bg-slate-200 w-9 h-9 rounded-full flex items-center justify-center transition-colors"
                title="Cancel"
              >
                <Square size={16} fill="currentColor" />
              </button>
            ) : (
              <button 
                disabled={loading || (!text.trim() && !file)} 
                onClick={handleSend}
                className="bg-industrial text-white hover:bg-industrial-light w-9 h-9 rounded-full flex items-center justify-center shadow-sm disabled:opacity-50 disabled:hover:bg-industrial transition-colors"
                title="Send message"
              >
                <ArrowUp size={18} strokeWidth={2.5} />
              </button>
            )}
          </div>
        </div>
      </div>
      <p className="text-[11px] font-medium text-slate-400 mt-3 text-center max-w-lg">
        CA Nexus synthesizes grounded factory records. Always verify critical safety SOPs with plant supervisors.
      </p>
    </div>
  );
}
