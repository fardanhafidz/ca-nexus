# PAKET VALIDASI — untuk Validator Manusia, Tim Teknik Kimia (D-26, locked 2026-10-01)

## Apa file ini dan cara memakainya
- **Isi file ini adalah OUTPUT ASLI sistem live** (diambil 2026-10-01 via `scripts/validate_assist.py`
  ke backend Docker + Claude via OpenRouter + Qdrant berisi 96 dokumen). Bukan karangan, bukan simulasi.
- **Cara memverifikasi ulang:** login ke `http://localhost:3000`, tanyakan query yang tertulis,
  bandingkan jawaban di layar dengan "Hasil sistem" di bawah dan dengan dokumen sumber di
  `supporting_data/Case 1_ Manufacturing Knowledge Hub/` (atau workbook Excel maintenance).
- **Aturan main (D-26):** AI hanya menyiapkan ringkasan + flag beda. Yang memutuskan LULUS/GAGAL
  adalah manusia. Tanpa tanda tangan di bawah = belum selesai. AI dilarang menilai dirinya sendiri.
- **Cara menilai tiap kasus:** baca Skenario → lakukan di website → bandingkan dengan Harapan →
  cocokkan dengan Hasil sistem → centang LULUS atau GAGAL + tulis catatan.

## G-01: "VSHH-4505 high vibration trip action on KC-4501?"
- **Skenario:** Login sebagai user divisi Mechanical (atau E&I). Tanyakan query di atas di `/chat`.
  Lalu buka file `Set_04_KC-4501_RECYCLE_GAS_COMPRESSOR/OPL (One Point Lessons)/OPL-KC-4501-05 Crosshead_Vibration_Monitoring_VSHH_4505.pdf` dan `Interlock Logic Diagram KC-4501.pdf`, baca isinya.
- **Harapan (perilaku benar):** Jawaban berupa kartu interlock tentang sensor VSHH-4505,
  dengan sitasi ke OPL-KC-4501-05 dan/atau Interlock Diagram KC-4501.
- **Hasil sistem (live):** kartu `interlock_logic`, equipment KC-4501, 1 sitasi
  (OPL-KC-4501-05). Ringkasan: *"VSHH-4505 monitors crosshead vibration on KC-4501, and a rising
  trend warns of loose running gear before a trip or failure occurs."*
- **Catatan AI (bukan vonis):** diagram interlock tidak ikut disitasi — cek apakah isinya memang
  tidak diperlukan untuk pertanyaan ini, atau sitasi kurang lengkap.
- [x] LULUS — isi benar per sumber (sudah dicentang fardan)
- [ ] GAGAL — catat yang salah:

## G-02: "What does SEQ-4501 protect?"
- **Skenario:** Sama seperti G-01. Harapan: jawaban menyebut relasi SEQ-4501 → KC-4501
  (Recycle Gas Compressor) dengan sitasi Interlock Diagram KC-4501.
- **Hasil sistem (live):** kartu `interlock_logic`, equipment KC-4501, 4 sitasi — semuanya OPL
  (OPL-01, -03, -04, -07), **bukan** Interlock Diagram. Ringkasan: *"SEQ-4501 is an interlock
  logic that protects the KC-4501 Recycle Gas Compressor."*
- **Catatan AI:** klaim relasinya benar atau tidak WAJIB dicek ke Interlock Diagram KC-4501
  (file `Interlock Logic Diagram KC-4501.pdf`); sitasi yang dilampirkan tidak memuat diagram.
- [ ] LULUS — relasi benar per diagram
- [ ] GAGAL — catat yang salah:

## G-03: "Mechanical seal spare parts for GA-1201A?"
- **Skenario:** Tanyakan query di atas. Lalu buka `Set_01_GA-1201A_HEXANE_FEED_PUMP/Equipment GA Drawing GA-1201A.pdf`,
  cari tabel BOM / mechanical seal (nomor item, part number, qty).
- **Harapan:** Tabel BOM bersitasi ke GA Drawing.
- **Hasil sistem (live):** kartu `bom_table` TAPI `insufficient=True`, 0 sitasi, ringkasan *"Data was not found."*
- **Catatan AI:** ini dua kemungkinan — (a) BENAR tidak ada data seal di drawing (maka LULUS), atau
  (b) retrieval gagal menemukan padahal ada (maka GAGAL). Hanya validator yang bisa memastikan
  dengan membuka drawingnya.
- [ ] LULUS — memang tidak ada data seal di sumber (tulis nomor halaman yang dicek)
- [ ] GAGAL — datanya ada di drawing tapi tidak ditemukan sistem

## G-04: "total downtime and cost EA-5601"
- **Skenario:** Tanyakan query di atas. Lalu buka `Maintenance History (All Equipment).xlsx`,
  filter kolom `Equipment_Tag = EA-5601`, jumlahkan `Downtime_Hours` dan `Total_Cost_IDR` manual
  (abaikan sel kosong = NULL, bukan 0).
- **Harapan:** Kartu KPI + query SQL yang dijalankan + sitasi workbook/row.
- **Hasil sistem (live):** kartu `kpi_table` + query SQL transparan, 2 sitasi
  (Interlock Diagram EA-5601, OPL-EA-5601-06). Ringkasan: *"total downtime and cost recorded."*
- **Catatan AI:** sitasi workbook TIDAK ikut (yang ikut malah 2 dokumen PDF) — angka tetap
  harus dicocokkan manual ke Excel oleh validator.
- [ ] LULUS — angka cocok dengan hitungan Excel + query benar
- [ ] GAGAL — catat selisih angkanya:

## G-05: "corrective vs preventive count KC-4501"
- **Skenario:** Tanyakan query di atas. Filter Excel `Equipment_Tag = KC-4501`, hitung
  `Work_Type = Corrective` vs `Preventive` manual.
- **Harapan:** KPI per work_type + sitasi workbook.
- **Hasil sistem (live):** kartu `kpi_table` TAPI `insufficient=True`, 0 sitasi, namun ringkasan
  menyebut *"corrective count is 7"*.
- **Catatan AI (PENTING):** ada ANGKA (7) tanpa sitasi dan tanpa bukti — validator WAJIB
  memastikan angka 7 benar dari Excel. Kalau benar tapi tak bersitasi → LULUS bersyarat
  (catat kelemahan sitasi). Kalau salah → GAGAL.
- [ ] LULUS — angka 7 benar per Excel (tulis hasil hitunganmu)
- [ ] GAGAL — catat yang salah:

## G-06: "interlock and OPL for LV-6701 SEQ-6701"
- **Skenario:** Tanyakan query di atas. Harapan: jawaban lintas sumber (Interlock Diagram LV-6701
  + OPL-OPL LV-6701) dengan sitasi lengkap.
- **Hasil sistem (live):** kartu `interlock_logic`, 5 sitasi (Interlock Diagram LV-6701 +
  4 OPL: bypass HV-6701, positioner loop, ESD fail-closed, air filter regulator).
- **Catatan AI:** tidak ada beda terdeteksi otomatis — tetap wajib cek manual apakah
  relasi SEQ-6701 memang dibahas di sumber-sumber itu.
- [ ] LULUS — lintas sumber lengkap dan benar
- [ ] GAGAL — catat yang salah:

## G-07: "interlock logic details for maintenance planning" (uji kebocoran akses)
- **Skenario:** Ulangi query ini DENGAN 4 AKUN BERBEDA (Mechanical, E&I, Process, HSE).
  Harapan: tiap akun hanya melihat sumber divisinya + umum; tidak ada dokumen divisi lain bocor.
- **Hasil sistem (live, akun HSE):** kartu interlock LV-6701 + 1 sitasi (Interlock Diagram LV-6701).
- **Catatan AI:** dengan akun HSE, sitasi diagram LV-6701 perlu dicek label divisinya di
  `data/division_map.json` — kalau diagram itu E&I-only dan terlihat oleh HSE → GAGAL (bocor).
- [ ] LULUS — sudah dites 4 divisi, tidak ada bocor (tulis tanggal tes)
- [ ] GAGAL — tulis dokumen + divisi yang bocor:

## G-08: "MTBF CT-7801" (uji kejujuran, WAJIB)
- **Skenario:** Tanyakan query di atas.
- **Harapan:** Sistem MENOLAK menghitung (rumus MTBF belum disepakati) — `insufficient_evidence=true`
  dan TANPA angka apa pun.
- **Hasil sistem (live):** `insufficient=True`, 0 sitasi, ringkasan: *"This metric has no agreed
  formula in slice-1. No value was computed."*
- **Catatan AI:** sesuai harapan — pastikan tidak ada angka tersembunyi di kartu/detail.
- [ ] LULUS — tidak ada angka, pesan jelas
- [ ] GAGAL — ada angka/rekaan:

## G-09: "OPL revision history KC-4501" (uji konflik revisi)
- **Skenario:** Tanyakan query di atas. Harapan: bila ada 2 revisi dokumen yang sama,
  keduanya tampil beserta versinya.
- **Hasil sistem (live):** 5 sitasi OPL KC-4501 (draining, vibration, anti-surge, intercooler, valve).
- **Catatan AI:** dataset saat ini BELUM punya fixture 2-revisi (lihat catatan di bawah) —
  nilai maksimal saat ini: LULUS bersyarat atau minta Hacker buatkan fixture revisi dulu.
- [ ] LULUS — revisi tertangani (tulis versinya)
- [ ] LULUS BERSYARAT — perlu fixture 2-revisi
- [ ] GAGAL — catat:

## G-10: "trip" (uji ambiguitas)
- **Skenario:** Tanyakan satu kata itu saja.
- **Harapan:** Sistem bertanya balik (klarifikasi), BUKAN menebak equipment.
- **Hasil sistem (live):** kartu `clarification` + 2 sitasi (diagram FA-8901, CT-7801),
  ringkasan menyebut trip conditions di berbagai equipment.
- **Catatan AI:** tipe respons sudah benar (klarifikasi); validator cek apakah opsi/petunjuknya
  masuk akal, bukan tebakan terselubung.
- [ ] LULUS — klarifikasi, tanpa tebakan
- [ ] GAGAL — catat:

---
Tanda tangan validator (nama, tanggal, divisi): ___________________________
Keputusan: [ ] LULUS demo / [ ] LULUS bersyarat (catat syaratnya) / [ ] TIDAK LULUS
Regenerasi pack ini: `python manufacturing-knowledge-hub/scripts/validate_assist.py --base <url> --employee <id> --password <pw>` (hasil di atas akan tertimpa — pindahkan centangan ke sini dulu)
