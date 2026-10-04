"""D-26 — AI-assisted validation pack (D-26 locked 2026-10-01).

The AI is the validator's ASSISTANT, never the grader: for each golden query it
collects the live system answer, the expected source, and the cited sources,
then flags differences. A human validator (Teknik Kimia) checks each box and
signs. AI self-grading without signature is forbidden.

Usage:
  python scripts/validate_assist.py --base http://127.0.0.1:8000 \
      --employee EMP-VALID --password <pw> --out docs/VALIDATION-PACK.md

The validator account must exist + be approved. Regenerating OVERWRITES the
checked boxes in VALIDATION-PACK.md — move sign-off out first.
"""
import argparse
import datetime
import json
import os
import urllib.request
import urllib.error
import http.cookiejar

CASES = [
    {"id": "G-01", "query": "VSHH-4505 high vibration trip action on KC-4501?",
     "scenario": "Login sebagai Mechanical/E&I, tanyakan di /chat. Buka OPL-KC-4501-05 + Interlock Diagram KC-4501.",
     "expect": "Kartu interlock VSHH-4505 + sitasi OPL-KC-4501-05 dan/atau Interlock Diagram.",
     "expect_docs": ["OPL-KC-4501-05", "Interlock Logic Diagram KC-4501"],
     "check": "Isi benar per sumber?"},
    {"id": "G-02", "query": "What does SEQ-4501 protect?",
     "scenario": "Sama seperti G-01; fokus relasi SEQ-4501.",
     "expect": "Relasi SEQ-4501 → KC-4501 + sitasi Interlock Diagram.",
     "expect_docs": ["Interlock Logic Diagram KC-4501"],
     "check": "Relasi interlock benar per diagram?"},
    {"id": "G-03", "query": "Mechanical seal spare parts for GA-1201A?",
     "scenario": "Tanyakan; lalu buka Equipment GA Drawing GA-1201A, cari tabel BOM/mechanical seal.",
     "expect": "Tabel BOM bersitasi — ATAU insufficient yang benar bila memang tak ada data.",
     "expect_docs": ["GA Drawing GA-1201A"],
     "check": "Ada/tidak ada data seal? Kalau ada tapi tak ditemukan = GAGAL."},
    {"id": "G-04", "query": "total downtime and cost EA-5601",
     "scenario": "Tanyakan; filter Excel Equipment_Tag=EA-5601, jumlahkan Downtime_Hours + Total_Cost_IDR manual.",
     "expect": "Kartu KPI + query SQL transparan + sitasi workbook.",
     "expect_docs": ["Maintenance History (All Equipment).xlsx"],
     "check": "Angka cocok Excel? Tulis hasil hitunganmu."},
    {"id": "G-05", "query": "corrective vs preventive count KC-4501",
     "scenario": "Tanyakan; hitung manual Work_Type Corrective vs Preventive untuk KC-4501 di Excel.",
     "expect": "KPI per work_type + sitasi. Waspada: angka tanpa sitasi.",
     "expect_docs": ["Maintenance History (All Equipment).xlsx"],
     "check": "Angka benar? Kalau benar tanpa sitasi = LULUS bersyarat."},
    {"id": "G-06", "query": "interlock and OPL for LV-6701 SEQ-6701",
     "scenario": "Tanyakan; harapan jawaban lintas sumber.",
     "expect": "Interlock Diagram LV-6701 + OPL-OPL LV-6701 bersitasi.",
     "expect_docs": ["Interlock", "OPL"],
     "check": "Lintas sumber lengkap dan benar?"},
    {"id": "G-07", "query": "interlock logic details for maintenance planning",
     "scenario": "Ulangi dengan 4 AKUN BERBEDA (satu per divisi).",
     "expect": "Tiap akun hanya melihat sumber divisinya + umum; nihil bocor.",
     "expect_docs": [],
     "check": "Sudah dites 4 divisi? Tulis tanggal + hasil."},
    {"id": "G-08", "query": "MTBF CT-7801",
     "scenario": "Tanyakan. WAJIB: sistem menolak menghitung.",
     "expect": "insufficient_evidence=true, TANPA angka.",
     "expect_docs": [],
     "check": "Tidak ada angka tersembunyi?"},
    {"id": "G-09", "query": "OPL revision history KC-4501",
     "scenario": "Tanyakan. Perlu fixture 2-revisi (belum ada).",
     "expect": "Bila 2 revisi ada: keduanya + versi tampil.",
     "expect_docs": [],
     "check": "LULUS / LULUS BERSYARAT (perlu fixture) / GAGAL."},
    {"id": "G-10", "query": "trip",
     "scenario": "Tanyakan satu kata itu saja.",
     "expect": "Kartu clarification, bukan tebakan equipment.",
     "expect_docs": [],
     "check": "Klarifikasi tanpa tebakan?"},
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--employee", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "docs", "VALIDATION-PACK.md"))
    a = ap.parse_args()

    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def post(path, body):
        r = urllib.request.Request(a.base + path, data=json.dumps(body).encode(),
                                   method="POST", headers={"Content-Type": "application/json"})
        with op.open(r, timeout=180) as resp:
            return json.loads(resp.read())

    post("/api/v1/auth/login", {"employee_id": a.employee, "password": a.password})
    today = datetime.date.today().isoformat()
    lines = ["# PAKET VALIDASI — untuk Validator Manusia, Tim Teknik Kimia (D-26, locked 2026-10-01)", "",
             "## Apa file ini dan cara memakainya",
             "- **Isi file ini adalah OUTPUT ASLI sistem live** (diambil via script ini ke backend + LLM + Qdrant). "
             "Bukan karangan, bukan simulasi.",
             "- **Verifikasi ulang:** login ke website, tanyakan query-nya, bandingkan dengan dokumen sumber.",
             "- **Aturan (D-26):** AI menyiapkan ringkasan + flag; MANUSIA yang mencentang. "
             "Tanpa tanda tangan = belum selesai.", ""]
    for c in CASES:
        try:
            ans = post("/api/v1/chat/ask", {"message": c["query"]})
            cited = [x.get("document_title", "") for x in ans.get("citations", [])]
            missing = [d for d in c["expect_docs"] if not any(d in t for t in cited)]
            flags = [f"sumber-acuan-tidak-disitasi: {', '.join(missing)}"] if missing else []
            if c["id"] == "G-08" and not ans.get("component_payload", {}).get("insufficient_evidence"):
                flags.append("G-08 harus insufficient_evidence=true (WAJIB)")
            if c["id"] == "G-10" and ans.get("component_type") != "clarification":
                flags.append("G-10 seharusnya clarification, dapat " + str(ans.get("component_type")))
            comp = ans.get("component_type")
            equip = ans.get("equipment_tag")
            insuf = ans.get("component_payload", {}).get("insufficient_evidence")
            result = (f"kartu `{comp}`, equipment {equip}, insufficient={insuf}, "
                      f"{len(cited)} sitasi, route={ans.get('route')}")
            summary = ans.get("summary_text", "")[:400].replace("\n", " ")
        except Exception as e:
            result, cited, flags = f"ERROR menjalankan query: {e}", [], ["query gagal"]
            summary = ""
        lines += [f"## {c['id']}: \"{c['query']}\"",
                  f"- **Skenario:** {c['scenario']}",
                  f"- **Harapan:** {c['expect']}",
                  f"- **Hasil sistem ({today}):** {result}",
                  f"- **Ringkasan AI:** {summary if summary else '(kosong)'}",
                  "- **Disitasi:** " + (", ".join(cited) if cited else "(tidak ada)")]
        lines += [f"- **Catatan AI:** {f}" for f in flags]
        if not flags:
            lines.append("- **Catatan AI:** tidak ada beda terdeteksi otomatis — tetap wajib cek manual")
        lines += [f"- [ ] LULUS — {c['check']}", "- [ ] GAGAL — catat yang salah:", ""]
    lines += ["---",
              "Tanda tangan validator (nama, tanggal, divisi): ___________________________",
              "Keputusan: [ ] LULUS demo / [ ] LULUS bersyarat (catat syaratnya) / [ ] TIDAK LULUS",
              "Regenerasi menimpa centangan — pindahkan sign-off dulu. "
              "Perintah: `python manufacturing-knowledge-hub/scripts/validate_assist.py "
              "--base <url> --employee <id> --password <pw>`", ""]
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {a.out} ({len(CASES)} cases)")


if __name__ == "__main__":
    main()
