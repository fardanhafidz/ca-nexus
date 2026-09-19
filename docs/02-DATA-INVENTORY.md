# 02 — Inventaris Data dan Batas Verifikasi

## 1. Metode pemeriksaan

- Tanggal: **18 September 2026**.
- Pemeriksaan menggunakan daftar direktori dan pencarian nama file pada workspace.
- Root sumber aktual: `supporting_data/Case 1_ Manufacturing Knowledge Hub/`.
- **TERVERIFIKASI-WORKSPACE:** keberadaan file, nama, ekstensi, dan pengelompokan direktorinya.
- **Belum diverifikasi:** isi dokumen, jumlah halaman, kualitas scan/teks, isi cell Excel, formula, isi slide, nilai engineering, akurasi judul internal, revision resmi, maupun relasi antar-tag.

Inventaris ini bukan laporan keberhasilan parsing atau ingestion.

## 2. Ringkasan jumlah file

| Jenis | Jumlah dari daftar file | Catatan |
| --- | ---: | --- |
| PDF | 88 | Setiap set memiliki 11 PDF: 7 bernama OPL dan 4 dokumen teknis lain |
| PNG | 8 | Satu gambar bernama P&ID/PID per set |
| XLSX | 1 | `Maintenance History (All Equipment).xlsx` |
| PPTX | 1 | `Data Set Explanation for Case 1 Manufacturing Knowledge Hub.pptx` |
| **Total** | **98** | 96 file di delapan set, ditambah workbook dan slide deck |

Klasifikasi OPL/datasheet/drawing/interlock/plot plan di sini berdasarkan nama file. Keberadaan informasi teknis tertentu di dalam file belum diperiksa.

## 3. Delapan set equipment

Tag dan nama equipment berikut disalin/dinormalisasi dari nama folder, bukan hasil pembacaan datasheet.

| Set | Folder relatif terhadap root sumber | Tag dari folder | Label equipment dari folder | PDF | PNG | OPL PDF |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 01 | `Set_01_GA-1201A_HEXANE_FEED_PUMP/` | `GA-1201A` | Hexane Feed Pump | 11 | 1 | 7 |
| 02 | `Set_02_YD-2301_POLYMER_FLUID_BED_DRYER/` | `YD-2301` | Polymer Fluid Bed Dryer | 11 | 1 | 7 |
| 03 | `Set_03_DC-3401A_CATALYST_REDUCTION_REACTOR/` | `DC-3401A` | Catalyst Reduction Reactor | 11 | 1 | 7 |
| 04 | `Set_04_KC-4501_RECYCLE_GAS_COMPRESSOR/` | `KC-4501` | Recycle Gas Compressor | 11 | 1 | 7 |
| 05 | `Set_05_EA-5601_SOLVENT_HEATER/` | `EA-5601` | Solvent Heater | 11 | 1 | 7 |
| 06 | `Set_06_LV-6701_SEPARATOR_LEVEL_CONTROL_VALVE/` | `LV-6701` | Separator Level Control Valve | 11 | 1 | 7 |
| 07 | `Set_07_CT-7801_COOLING_TOWER_CELL_FAN/` | `CT-7801` | Cooling Tower Cell Fan | 11 | 1 | 7 |
| 08 | `Set_08_FA-8901_REFLUX_ACCUMULATOR_DRUM/` | `FA-8901` | Reflux Accumulator Drum | 11 | 1 | 7 |

Total berdasarkan pola nama: **56 OPL PDF**, **32 PDF teknis lainnya**, dan **8 PNG P&ID**.

### 3.1 Nama file P&ID aktual

| Set | Nama file |
| --- | --- |
| 01 | `PID_Set_01.png` |
| 02 | `P&ID_Set_02.png` |
| 03 | `P&ID Set 3.png` |
| 04 | `P&ID SET 4.png` |
| 05 | `P&ID SET 5.png` |
| 06 | `P&ID SET 6.png` |
| 07 | `P&ID_Set 7.png` |
| 08 | `P&ID_Set 8.png` |

Konsekuensi: pencarian sumber perlu menangani ekstensi PNG dan variasi penamaan. Membaca seluruh PDF saja tidak mencakup gambar-gambar ini.

### 3.2 Variasi folder dan filename

- Folder OPL menggunakan beberapa bentuk: `One Point Lesson`, `One Point Lesson (OPL)`, dan `OPL (One Point Lessons)`.
- Drawing Set 03 bernama `Equipment Drawing DC-3401A.pdf`, sedangkan banyak set lain menggunakan `Equipment GA Drawing ...`.
- Spasi, underscore, tanda hubung, serta huruf besar/kecil bervariasi.
- Beberapa nama OPL Set 01 memuat suffix seperti `EDITED`, `ONE_PAGE`, atau `REFINED_TABLE`. Suffix tersebut belum membuktikan urutan revision resmi.
- Nama tag pada folder merupakan petunjuk equipment utama. File bisa membahas equipment/instrument terkait; isinya perlu diperiksa sebelum menetapkan relasi.

## 4. Workbook maintenance

Path aktual:

```text
supporting_data/Case 1_ Manufacturing Knowledge Hub/Maintenance History (All Equipment).xlsx
```

| Informasi | Status |
| --- | --- |
| File workbook tersedia | TERVERIFIKASI-WORKSPACE |
| Terdapat 211 record historis | BRIEF; belum dihitung dari workbook |
| Model maintenance terdiri dari 31 kolom | BRIEF; header dan jumlah kolom belum dibaca |
| Nama sheet yang harus diimpor | TERBUKA |
| Kolom ID record, tanggal, equipment, divisi, biaya, downtime, dan unit | TERBUKA; tidak boleh dibuat seolah-olah sudah ditemukan |
| Formula, merged cell, header bertingkat, cell kosong, duplikasi | Belum diperiksa |
| Relasi data dengan delapan set | BRIEF menyebut semua equipment; pemetaan aktual belum diperiksa |

### Pemeriksaan yang diperlukan sebelum menetapkan model

1. Daftar sheet, rentang data, lokasi header, dan baris non-data.
2. Jumlah kolom aktual, nama header asli, tipe nilai, serta kandidat identitas record.
3. Jumlah baris data menurut aturan yang disepakati; bandingkan dengan angka 211.
4. Format tanggal, timezone bila ada, satuan, nilai kosong, serta formula versus cached value.
5. Nilai equipment/divisi dan mekanisme klasifikasi akses yang bisa didukung data.
6. Duplikasi, data yang gagal dibaca, dan aturan transformasi yang mempertahankan informasi asli.
7. Definisi lineage: sumber workbook, sheet, row, dan versi import.

Nama 31 kolom SQL baru dapat ditetapkan setelah hasil profiling tersedia. Bila hasil berbeda dari brief, selisih harus dicatat dan dibahas, bukan dipaksa menjadi 211 × 31.

## 5. Slide deck penjelasan dataset

Path aktual:

```text
supporting_data/Case 1_ Manufacturing Knowledge Hub/Data Set Explanation for Case 1 Manufacturing Knowledge Hub.pptx
```

Keberadaan slide deck terverifikasi. Isinya belum dibaca. Perlu ditentukan apakah slide merupakan sumber requirement tambahan, panduan interpretasi data, sumber yang ikut diindeks, atau hanya materi konteks. Bila isinya berbeda dari brief, urutan otoritas sumber perlu disepakati melalui D-07.

## 6. Ketidaksesuaian dan informasi yang belum lengkap

| ID | Temuan | Dampak | Keputusan/task terkait |
| --- | --- | --- | --- |
| GAP-01 | P&ID berupa PNG; pipeline brief berfokus PDF | Butuh jalur ekstraksi/indexing gambar bila P&ID masuk cakupan retrieval | D-11; T2.6 |
| GAP-02 | Lokasi sumber aktual berbeda dari `scripts/data/` | Script, mount container, dan konfigurasi source root perlu konsisten | D-02; T1.1, T1.3 |
| GAP-03 | Contoh sitasi menggunakan path ringkas `/data/Set_04_KC-4501/...` | Path contoh tidak boleh dianggap sebagai alamat file aktual | D-18; T3.5, T4.9 |
| GAP-04 | Header workbook belum diketahui | Model 31 kolom, import, metrik, dan row-level access belum bisa difinalkan | D-09, D-10; T2.2, T2.3 |
| GAP-05 | Hak akses per file belum tersedia pada inventaris | Metadata `division_access` memerlukan pemetaan yang disepakati | D-06, D-07; T2.4 |
| GAP-06 | Tidak ada hasil pemeriksaan isi drawing | BOM, simbol, relasi, koordinat, dan teks mungkin memerlukan metode berbeda | D-11; T2.5, T2.6 |
| GAP-07 | Relasi `Related_Interlock`/`Instrument_Tag` belum diekstrak | Graph belum dapat dibangun hanya berdasarkan nama direktori | D-14; T4.3, T4.4 |
| GAP-08 | Status revision/otoritas dokumen belum diketahui | Retrieval harus memiliki aturan untuk sumber yang berubah/bertentangan | D-07, D-08; T2.10 |
| GAP-09 | Peran slide deck belum ditetapkan | Requirement atau metadata penting mungkin masih perlu ditinjau | D-07; T0.2 |

## 7. Manifest sumber yang diusulkan

**USULAN, bukan schema database yang disepakati.** Tujuannya menghubungkan sumber asli dengan hasil ekstraksi dan indeks.

| Kelompok | Informasi kandidat | Dasar |
| --- | --- | --- |
| Metadata retrieval | `equipment_tag`, `doc_type`, `division_access`, `doc_title`, `page_number` | Field eksplisit dalam brief |
| Identitas | ID dokumen stabil, ID revision, path sumber relatif, checksum, MIME type | Usulan untuk deduplikasi, sitasi, dan perubahan sumber |
| Provenance | Nomor halaman PDF atau identitas gambar; sheet/row untuk Excel; lokasi region bila diperlukan | Usulan agar rujukan sesuai tipe sumber |
| Ekstraksi | Metode/parser, versi konfigurasi, status per file/halaman, teks mentah dan hasil normalisasi bila dipilih | Usulan untuk menelusuri kualitas parsing |
| Pengindeksan | ID chunk, model embedding, versi indeks, status dense/lexical/graph | Usulan untuk konsistensi pipeline |
| Relasi | Tag terkait, jenis hubungan, sumber bukti, status peninjauan bila dipilih | Usulan untuk graph berbasis sumber |

`page_number` belum mempunyai arti yang disepakati untuk PNG dan record SQL. Keputusan kontraknya dibahas pada [kontrak respons](04-AI-RESPONSE-CONTRACT.md).

## 8. Kriteria selesai audit data

Audit data baru dapat dinyatakan selesai ketika ada:

- Manifest seluruh sumber yang masuk scope beserta pengecualian yang dijelaskan.
- Laporan isi workbook, hitungan baris/kolom aktual, serta pemetaan schema yang disepakati.
- Sampel representatif setiap tipe dokumen yang diperiksa beserta kebutuhan OCR/vision/tabelnya.
- Pemetaan sumber ke equipment dan divisi dengan dasar yang dapat ditelusuri.
- Keputusan cakupan PPTX, PNG, plot plan, relasi graph, dan data maintenance.
- Daftar gap yang masih terbuka tanpa membuat nilai atau isi teknis pengganti.
