# T0.2 — Audit Sumber (terverifikasi 19 Sep 2026 via openpyxl + PyMuPDF)

Keputusan: D-07. Status klaim 211×31: **TERVERIFIKASI** (menggantikan label BRIEF di docs/02).

## Workbook
- Path: `supporting_data/Case 1_ Manufacturing Knowledge Hub/Maintenance History (All Equipment).xlsx`
- Sheets: `Maintenance History (All Equipm` (nama terpotong limit 31 char Excel), `Explanation`
- Header baris 1, 31 kolom sesuai `docs/DATA-DICTIONARY.md`; 212 baris total = 211 data + 1 header
- `WO_Number`: 211 unik, 0 null, 0 duplikat
- Distribusi tag: KC-4501:27, LV-6701:26, YD-2301:28, CT-7801:27, EA-5601:25, FA-8901:25, DC-3401A:27, GA-1201A:26
- Tipe: 3 kolom tanggal (datetime), 5 numerik (downtime/labor/material/total), sisanya teks
- Formula/merged-cell: tidak terdeteksi via `data_only=True` pada sampel (perlu cek `data_only=False` bila formula dicurigai — TERBUKA)
- `Related_Interlock`: terisi pola `SEQ-xxxx`; baris tanpa interlock memakai `-`/kosong → edge graph hanya dibuat bila nilai valid

## PDF sampel (Set_04, PyMuPDF `get_text`)
| File | Halaman | Karakter p0 | Jenis |
|---|---|---|---|
| Equipment Datasheet - KC-4501.pdf | 1 | 1650 | native text |
| Equipment GA Drawing KC-4501.pdf | 1 | 1670 | native text |
| Interlock Logic Diagram KC-4501.pdf | 1 | 1835 | native text |
| Plot Plan KC-4501.pdf | 1 | 1552 | native text |
| OPL-KC-4501-05 Crosshead_Vibration_Monitoring_VSHH_4505.pdf | 1 | 3289 | native text |
Semua sampel = teks digital asli (bukan scan). Deteksi scan tetap diimplementasikan untuk file lain
(halaman < 50 char → flag `needs_ocr`, bukan sukses penuh).

## PNG P&ID
8 file, penamaan tidak konsisten (`PID_Set_01.png` … `P&ID_Set 8.png`). Tidak ada teks
yang dapat diekstrak tanpa OCR/vision — pipeline memperlakukan PNG sebagai citra + deskripsi
vision berprovenance, BUKAN konektivitas penuh.

## PPTX
`Data Set Explanation for Case 1 Manufacturing Knowledge Hub.pptx` = konteks arsitektur,
TIDAK diindeks sebagai sumber jawaban (D-07).

## Variasi path (T1.1)
Folder OPL: `One Point Lesson`, `One Point Lesson (OPL)`, `OPL (One Point Lessons)`;
`&` (`P&ID_Set_02.png`), spasi/underscore/case bervariasi → resolve via `pathlib`,
quoting di shell, jangan hard-code contoh `/data/Set_04...` (GAP-03).
