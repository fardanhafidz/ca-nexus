// T6.4 voice: Web Speech API for instant input + server Whisper via /transcribe.
// Transcript is always returned to the input box for preview/edit before send (D-22).
export function supportsWebSpeech(): boolean {
  if (typeof window === "undefined") return false;
  return !!((window as unknown as { webkitSpeechRecognition?: unknown; SpeechRecognition?: unknown }).webkitSpeechRecognition
    || (window as unknown as { SpeechRecognition?: unknown }).SpeechRecognition);
}
export function listenOnce(cb: (text: string) => void, onErr: (e: string) => void, lang = "en-US") {
  type Rec = {
    lang: string; interimResults: boolean;
    onresult: ((e: { results: { transcript: string }[][] }) => void) | null;
    onerror: ((e: { error?: string }) => void) | null;
    start: () => void;
  };
  const w = window as unknown as Record<string, (new () => Rec) | undefined>;
  const Cls = w.SpeechRecognition || w.webkitSpeechRecognition;
  if (!Cls) return onErr("Speech recognition not supported — type instead, or record audio for server transcription.");
  const rec: Rec = new Cls();
  rec.lang = lang;  // en-US default; pass id-ID for Indonesian tags/operators
  rec.interimResults = false;
  rec.onresult = (e) => cb(e.results[0][0].transcript);
  rec.onerror = (e) => onErr(e.error || "Microphone error — check permission and retry.");
  rec.start();
}

/** DEL-F4 — MediaRecorder path: returns controls; caller stops to get the Blob.
 *  No dependency; works wherever MediaRecorder + getUserMedia exist. */
export function isRecorderSupported(): boolean {
  if (typeof window === "undefined" || typeof navigator === "undefined") return false;
  return !!(window.MediaRecorder && navigator.mediaDevices?.getUserMedia);
}

export async function startRecording(onErr: (e: string) => void): Promise<{ stop: () => Promise<Blob> } | null> {
  if (!isRecorderSupported()) { onErr("Recording not supported — type instead."); return null; }
  let stream: MediaStream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch {
    onErr("Microphone permission denied.");
    return null;
  }
  const mime = window.MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "";
  const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
  const chunks: BlobPart[] = [];
  rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
  rec.start();
  return {
    stop: () =>
      new Promise((resolve, reject) => {
        rec.onstop = () => {
          stream.getTracks().forEach((t) => t.stop());
          if (!chunks.length) reject(new Error("Empty recording — record again."));
          else resolve(new Blob(chunks, { type: rec.mimeType || "audio/webm" }));
        };
        rec.onerror = () => reject(new Error("Recording failed — retry."));
        rec.stop();
      }),
  };
}
