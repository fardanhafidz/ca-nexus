"use client";
import { useMemo } from "react";

/** DEL-F1 — dependency-free safe Markdown subset. Source/evidence text is DATA:
 *  HTML is escaped first, so model or document content can never inject markup. */
function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inline(s: string): string {
  let out = escapeHtml(s);
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  return out;
}

export function renderMarkdown(src: string): string {
  const lines = src.split("\n");
  let html = "", inList = "", inCode = false, codeBuf: string[] = [];
  const closeList = () => { if (inList) { html += inList === "ul" ? "</ul>" : "</ol>"; inList = ""; } };
  for (const line of lines) {
    if (line.trim().startsWith("```")) {
      if (inCode) { html += `<pre>${escapeHtml(codeBuf.join("\n"))}</pre>`; codeBuf = []; inCode = false; }
      else { closeList(); inCode = true; }
      continue;
    }
    if (inCode) { codeBuf.push(line); continue; }
    const mUl = line.match(/^\s*[-*]\s+(.*)/);
    const mOl = line.match(/^\s*\d+[.)]\s+(.*)/);
    const mH = line.match(/^(#{1,3})\s+(.*)/);
    if (mUl) {
      if (inList !== "ul") { closeList(); html += "<ul>"; inList = "ul"; }
      html += `<li>${inline(mUl[1])}</li>`;
    } else if (mOl) {
      if (inList !== "ol") { closeList(); html += "<ol>"; inList = "ol"; }
      html += `<li>${inline(mOl[1])}</li>`;
    } else if (mH) {
      closeList();
      html += `<p><strong>${inline(mH[2])}</strong></p>`;
    } else if (line.trim() === "") {
      closeList();
    } else {
      closeList();
      html += `<p>${inline(line)}</p>`;
    }
  }
  if (inCode) html += `<pre>${escapeHtml(codeBuf.join("\n"))}</pre>`;
  closeList();
  return html;
}

export default function Markdown({ text }: { text: string }) {
  const html = useMemo(() => renderMarkdown(text), [text]);
  return <div className="markdown-body space-y-1" dangerouslySetInnerHTML={{ __html: html }} />;
}
