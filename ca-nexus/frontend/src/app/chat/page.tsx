"use client";
import { useEffect, useState } from "react";
import AppSidebar from "@/components/layout/AppSidebar";
import ChatInput from "@/components/chat/ChatInput";
import MessageItem from "@/components/chat/MessageItem";
import Inspector from "@/components/chat/Inspector";
import { useSearchParams } from "next/navigation";
import { api, askStream, API, ApiError } from "@/lib/api";
import type { Answer, Citation } from "@/lib/contract";
import { listenOnce, startRecording, isRecorderSupported } from "@/lib/audio";

type Msg = { key: string; role: string; text: string; answer?: Answer | null };
let keySeq = 0;
const nextKey = () => `m${Date.now()}-${keySeq++}`;

export default function ChatPage() {
  const searchParams = useSearchParams();
  const urlId = searchParams?.get("id");
  const isNew = searchParams?.get("new");
  
  const [sid, setSid] = useState<string | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamStage, setStreamStage] = useState("");
  const [err, setErr] = useState("");
  const [cite, setCite] = useState<Citation | null>(null);
  const [aborter, setAborter] = useState<AbortController | null>(null);
  const [draft, setDraft] = useState("");  // DEL-F4: composer text (transcript lands here for edit)
  const [recorder, setRecorder] = useState<{ stop: () => Promise<Blob> } | null>(null);
  const [recErr, setRecErr] = useState("");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);

  useEffect(() => {
    if (isNew) {
      setSid(null);
      setMsgs([]);
      setErr("");
      return;
    }
    if (urlId && urlId !== sid) {
      open(urlId);
    }
  }, [urlId, isNew]);

  const open = async (id: string) => {
    setErr("");
    try {
      setSid(id);
      const j = await api(`/api/v1/chat/sessions/${id}`);
      setMsgs(j.messages.map((m: { role: string; text: string; payload?: Answer | null }) => ({
        key: nextKey(), role: m.role, text: m.text, answer: m.payload || null,
      })));
    } catch (e) { setErr(e instanceof ApiError ? e.message : "Failed to open session."); }
  };
  const uploadImage = async (file: File): Promise<string | undefined> => {
    const fd = new FormData();
    fd.append("file", file);
    const r = await fetch(`${API}/api/v1/chat/attachments`, { method: "POST", credentials: "include", body: fd });
    if (!r.ok) throw new ApiError(r.status, "Image upload failed.");
    const j = await r.json();
    if (j.needs_confirmation) {
      setErr(`Vision detected ${j.detected_tags?.join(", ") || "no tags"} — confirm the equipment tag in your message.`);
    }
    return j.attachment_id as string;
  };
  // DEL-F4: record → preview → transcribe → edit in composer → send (ID/EN selectable)
  const [recLang, setRecLang] = useState("en-US");
  const toggleRecord = async () => {
    setRecErr("");
    if (recorder) {
      try {
        const blob = await recorder.stop();
        setRecorder(null);
        setAudioUrl(URL.createObjectURL(blob));
        const fd = new FormData();
        fd.append("file", blob, "recording.webm");
        const r = await fetch(`${API}/api/v1/chat/transcribe`, { method: "POST", credentials: "include", body: fd });
        if (!r.ok) throw new ApiError(r.status, await r.text());
        const j = await r.json();
        setTranscript(j.text || "");
        if (j.hint) setRecErr(j.hint);
      } catch (e) { setRecErr(e instanceof ApiError ? e.message : "Recording/transcription failed."); setRecorder(null); }
      return;
    }
    const ctl = await startRecording((e) => setRecErr(e));
    if (ctl) setRecorder(ctl);
  };
  const send = async (text: string, file?: File | null) => {
    if (loading) return;
    setLoading(true); setErr(""); setStreamStage("Starting...");
    setDraft("");
    setMsgs((m) => [...m, { key: nextKey(), role: "user", text }]);
    try {
      const attachment_id = file ? await uploadImage(file) : undefined;
      const ac = new AbortController();
      setAborter(ac);
      const final = await askStream(
        { session_id: sid, message: text, attachment_id },
        (type) => { if (type === "progress") setStreamStage("Retrieving evidence..."); },
        ac.signal,
      );
      if (final) {
        if (!sid && final.session_id) {
          // Instead of loadSessions(), we could force a refresh or AppSidebar will handle it on next load
          // For PoC, maybe just let it be or refresh page
          setSid(final.session_id);
          window.history.replaceState(null, "", `/chat?id=${final.session_id}`);
        }
        setMsgs((m) => [...m, { key: nextKey(), role: "assistant", text: final.summary_text, answer: final }]);
      }
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Send failed — retry without duplicating the message.");
    }
    setLoading(false); setStreamStage(""); setAborter(null);
  };
  return (
    <div className="flex h-screen w-full bg-canvas">
      <AppSidebar activeSessionId={sid} />
      <div className="flex-1 flex flex-col bg-canvas min-w-0">
        <header className="bg-white border-b border-line p-3 flex justify-between items-center gap-2">
          <h1 className="font-semibold text-industrial text-sm">Chat Workspace</h1>
          <div className="flex gap-1 items-center">
            <select value={recLang} onChange={(e) => setRecLang(e.target.value)} aria-label="Speech language"
              className="text-xs border rounded px-1 py-1">
              <option value="en-US">EN</option>
              <option value="id-ID">ID</option>
            </select>
            <button onClick={() => listenOnce((t) => send(t), (e) => setErr(e), recLang)}
              className="text-xs border border-industrial text-industrial rounded px-2 py-1">Voice input</button>
            {isRecorderSupported() && (
              <button onClick={toggleRecord}
                className={`text-xs border rounded px-2 py-1 ${recorder ? "border-red-500 text-red-600" : "border-industrial text-industrial"}`}>
                {recorder ? "Stop ●" : "Record"}
              </button>
            )}
          </div>
        </header>
        {recErr && <div role="alert" className="bg-amber-50 border border-amber-200 text-amber-700 text-xs p-2 m-2 rounded">{recErr}</div>}
        {audioUrl && (
          <div className="bg-white border-b border-line p-2">
            {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
            <audio src={audioUrl} controls className="w-full h-8" />
          </div>
        )}
        {transcript !== null && (
          <div className="bg-white border-b border-line p-2 space-y-1">
            <p className="text-xs font-semibold">Transcript — edit before sending:</p>
            <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} rows={2}
              aria-label="Edit transcript" className="w-full border rounded p-1.5 text-sm" />
            <div className="flex gap-1">
              <button onClick={() => { setDraft(transcript); setTranscript(null); }}
                className="text-xs bg-industrial text-white rounded px-2 py-1">Edit in composer</button>
              <button onClick={() => { send(transcript); setTranscript(null); }}
                className="text-xs border rounded px-2 py-1">Send now</button>
              <button onClick={() => setTranscript(null)} className="text-xs underline">Discard</button>
            </div>
          </div>
        )}
        {err && <div role="alert" className="bg-red-50 border border-red-200 text-red-700 text-xs p-2 m-2 rounded">{err}</div>}
        <div className="flex-1 overflow-auto p-3 space-y-2">
          {msgs.length === 0 && <p className="text-sm text-slate-500">Ask e.g. VSHH-4505 vibration interlock on KC-4501; BOM for GA-1201A seal; total downtime EA-5601.</p>}
          {msgs.map((m) => <MessageItem key={m.key} role={m.role} text={m.text} answer={m.answer} onCite={setCite} />)}
          {loading && <p className="text-xs text-slate-500" aria-live="polite">{streamStage || "Generating grounded answer..."}</p>}
        </div>
        <ChatInput onSend={send} loading={loading} onCancel={() => aborter?.abort()} draft={draft} setDraft={setDraft} />
      </div>
      <Inspector citation={cite} onClose={() => setCite(null)} />
    </div>
  );
}
