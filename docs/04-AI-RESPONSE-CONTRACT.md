# 04 — Kontrak Respons AI

## 1. Status dan tujuan

**BRIEF:** LLM menghasilkan JSON murni sehingga frontend dapat merender komponen secara dinamis.

**TERBUKA:** schema terperinci, cardinality komponen/equipment, status hasil, sumber non-PDF, serta transport streaming. Dokumen ini mempertahankan contoh pengguna dan mencatat hal yang harus dilengkapi. Belum ada schema pengganti yang disepakati.

Keputusan utama: D-17, dengan dependensi D-10, D-15, D-18, D-19, D-20, dan D-23.

## 2. Contoh asli dari brief

```json
{
  "summary_text": "Deskripsi singkat hasil analisa teknis terhadap kueri yang diajukan.",
  "equipment_tag": "KC-4501",
  "component_type": "procedure_checklist | interlock_logic | bom_table | root_cause_card",
  "component_payload": {
    "title": "Judul Komponen",
    "alert_level": "normal | warning | critical",
    "details": {}
  },
  "citations": [
    {
      "document_title": "OPL-KC-4501-05 Crosshead_Vibration_Monitoring_VSHH_4505.pdf",
      "page_number": 1,
      "snippet": "Kutipan kalimat rujukan eksak dari dokumen sumber...",
      "file_path": "/data/Set_04_KC-4501/OPL-KC-4501-05.pdf"
    }
  ]
}
```

Catatan pembacaan:

- Teks dengan pemisah `|` menyatakan pilihan pada brief. Payload runtime harus memilih satu nilai enum, bukan mengirim seluruh string daftar pilihan.
- `details: {}` belum mendefinisikan struktur data yang dapat divalidasi atau dirender secara konsisten.
- `KC-4501`, judul, nomor halaman, dan path di atas berasal dari contoh brief. Kutipan tersebut merupakan placeholder, bukan hasil ekstraksi dokumen.
- File dengan judul OPL tersebut ditemukan dalam dataset, tetapi isi dan nomor halaman kutipannya belum diperiksa.
- `file_path` pada contoh berbeda dari lokasi sumber aktual. Contoh ini belum merupakan URL viewer yang dapat digunakan.

## 3. Field yang sudah disebutkan

| Field | Makna dari brief | Detail yang perlu diputuskan |
| --- | --- | --- |
| `summary_text` | Narasi ringkas jawaban | Bahasa, format teks/Markdown, panjang, perilaku saat tidak ada bukti |
| `equipment_tag` | Equipment yang dibahas | Wajib atau nullable; satu atau banyak; pertanyaan tanpa equipment; normalisasi tag |
| `component_type` | Salah satu dari empat komponen | Apakah boleh tanpa komponen, beberapa komponen, atau tipe baru untuk hasil SQL/spesifikasi |
| `component_payload.title` | Judul komponen | Batas panjang dan hubungan dengan equipment/sumber |
| `component_payload.alert_level` | `normal`, `warning`, atau `critical` | Dasar penentuan, apakah wajib, dan cara menyatakan tidak diketahui/tidak relevan |
| `component_payload.details` | Isi spesifik komponen | Schema berbeda untuk setiap jenis komponen |
| `citations` | Daftar rujukan | Wajib per klaim/komponen atau per pesan; cardinality; deduplikasi |
| `citations[].document_title` | Judul sumber | Judul file atau judul resmi; revision; escaping/normalisasi |
| `citations[].page_number` | Halaman sumber | Index 1-based; printed page versus PDF page; representasi PNG/SQL |
| `citations[].snippet` | Kutipan eksak | Kutipan terhadap teks visual/raw extraction/normalisasi; OCR; region diagram tanpa kalimat |
| `citations[].file_path` | Lokasi file | Path relatif, identitas dokumen, atau URL terotorisasi yang diselesaikan backend |

## 4. Kasus yang belum terwakili

| Kasus | Kekurangan kontrak sekarang | Keputusan |
| --- | --- | --- |
| Pertanyaan umum atau definisi singkat | Empat tipe komponen wajib tidak selalu cocok | Q-JSON-01 |
| Spesifikasi datasheet | Belum ada komponen spesifikasi umum | Q-JSON-01 |
| Hitungan maintenance | Belum ada representasi tabel/angka/agregat SQL dan provenance tabular | Q-JSON-01, Q-CIT-03 |
| Beberapa equipment | Hanya satu `equipment_tag` | Q-JSON-02 |
| Checklist dan interlock dalam satu jawaban | Hanya satu komponen | Q-JSON-02 |
| Sumber tidak ditemukan | Tidak ada status insufficient-evidence atau bentuk hasil kosong | Q-JSON-03, Q-RAG-02 |
| Pertanyaan perlu klarifikasi | Tidak ada struktur pertanyaan klarifikasi | Q-JSON-03 |
| Sumber bertentangan/revision berbeda | Tidak ada cara menyatakan perbedaan bukti | Q-RAG-03, Q-JSON-03 |
| Gambar P&ID | `page_number` dan kutipan kalimat belum tentu sesuai | Q-CIT-03 |
| Citation terkait satu langkah atau satu row | Sitasi hanya pada tingkat pesan | Q-CIT-02 |
| Generation invalid/provider error | Error envelope belum ditentukan | Q-STR-03 |
| Streaming | Fragmen output belum tentu JSON utuh | Q-STR-01, Q-STR-02 |
| Riwayat setelah schema berubah | Belum ada versioning payload | Q-JSON-04 |

## 5. Rancangan payload yang perlu didiskusikan

Seluruh field kandidat di bagian ini berstatus **USULAN**. Daftar ini membantu menentukan kebutuhan komponen; nama field, requiredness, enum, dan schema akhirnya belum ditetapkan. Tidak ada nilai engineering yang diisi sebagai contoh faktual.

### 5.1 ProcedureChecklist

Tujuan dari brief: menyajikan langkah SOP/OPL sebagai checklist.

Informasi yang perlu dipertimbangkan:

- Identitas prosedur, equipment, dokumen/revision sumber.
- Prasyarat dan kondisi awal **jika tersedia dalam sumber**.
- Daftar langkah berurutan: identitas langkah, instruksi, parameter/satuan yang bersumber, dan rujukan.
- Catatan/peringatan yang benar-benar ada dalam sumber.
- Pemisahan data prosedur dari state interaksi pengguna seperti checked/unchecked.

Keputusan interaksi:

- Apakah checklist sekadar bantuan membaca atau catatan pekerjaan yang disimpan?
- Apakah state berlaku per pesan, session, user, atau pekerjaan tertentu?
- Apakah perubahan state membutuhkan backend atau hanya state UI?
- Bagaimana menampilkan langkah yang tidak lengkap atau saling berbeda antar-revision?

### 5.2 InterlockLogicCard

Tujuan dari brief: menampilkan tabel Cause & Effect sensor-trip.

Informasi yang perlu dipertimbangkan, hanya jika sumber mendukung:

- Equipment dan identitas interlock.
- Cause: instrument tag, kondisi, operator pembanding, setpoint, dan unit.
- Kombinasi/voting logic serta delay bila tercantum.
- Effect: aksi, target equipment/output, dan kondisi trip yang dijelaskan dokumen.
- Reset, permissive, atau catatan lain jika masuk scope dan ditemukan.
- Rujukan per cause/effect atau per hubungan.

Nilai kosong tidak boleh otomatis menjadi `0`, `false`, atau status normal. Hubungan instrument-trip tidak dapat ditetapkan hanya karena dua tag muncul pada chunk yang sama.

### 5.3 SparePartBOMTable

Tujuan dari brief: menyajikan BOM/suku cadang dari GA drawing.

Informasi yang perlu dipertimbangkan:

- Equipment, drawing, revision, dan halaman/region sumber.
- Row item: nomor item, nama/deskripsi, part number, quantity, unit, material/specification jika ada.
- Rujukan per row atau per tabel.
- Penanda field yang tidak tersedia versus nilai yang benar-benar nol.

Belum diketahui apakah semua GA drawing memiliki BOM. Part number, jumlah, dan material tidak boleh dilengkapi berdasarkan pengetahuan umum ketika sumber tidak mencantumkannya.

### 5.4 RootCauseCard

Tujuan dari brief: menyajikan investigasi kegagalan dan konteks RCA/maintenance.

Informasi yang perlu dipertimbangkan:

- Equipment dan kejadian/record maintenance terkait.
- Gejala dan observasi yang dinyatakan sumber.
- Root cause yang telah dicatat dalam sumber, bila memang ada.
- Hipotesis analisis, jika pengguna mengizinkan, ditandai terpisah dari fakta tercatat.
- Tindakan yang dicatat pada histori dan rekomendasi baru, jika termasuk scope, dibedakan asalnya.
- Bukti, keterbatasan data, serta provenance dokumen/record.

Frekuensi kerusakan atau korelasi waktu tidak dengan sendirinya membuktikan root cause. Confidence score atau status terkonfirmasi memerlukan definisi dan bukti, bukan angka dari model tanpa kalibrasi.

## 6. Pertanyaan tentang alert level

Baseline enum adalah `normal | warning | critical`. Hal-hal berikut masih perlu dijawab:

1. Apakah level berasal dari klasifikasi sumber, aturan produk yang disepakati, atau penilaian model?
2. Apakah severity suatu kejadian, tingkat perhatian UI, dan kondisi equipment merupakan konsep yang sama?
3. Apa hasilnya ketika sumber tidak memberi tingkat severity?
4. Apakah semua komponen memerlukan alert, termasuk BOM atau definisi umum?

Sampai disepakati, tidak ada mapping otomatis dari kata tertentu, divisi, jenis dokumen, atau nilai yang belum diverifikasi ke level alert.

## 7. Sitasi dan provenance

### 7.1 Baseline

Sitasi menampilkan judul, halaman, snippet eksak, dan lokasi file. Klik chip membuka Inspector yang menampilkan sumber asli.

### 7.2 Usulan penguatan kontrak

- Backend menautkan rujukan ke sumber yang benar-benar diambil dan masih boleh diakses.
- Gunakan identitas sumber/revision yang stabil; alamat storage diselesaikan backend sesuai kontrak final.
- Bedakan locator PDF, gambar, dan workbook/row SQL.
- Definisikan index halaman; jangan menyamakan angka halaman tercetak dengan nomor halaman file tanpa aturan.
- Definisikan kutipan eksak terhadap representasi sumber yang dipilih. Teks normalisasi retrieval dan teks untuk kutipan dapat perlu disimpan terpisah.
- Untuk diagram tanpa kalimat, rujukan region/label sumber dapat lebih sesuai daripada membuat snippet naratif yang diklaim sebagai kutipan.
- Untuk agregasi maintenance, tampilkan lineage dataset, filter/periode, formula yang dipilih, dan referensi row/query sesuai kebutuhan audit yang disepakati.
- Tentukan cara menangani dokumen yang diganti, dihapus, atau hak aksesnya berubah setelah jawaban disimpan.

Field baru seperti `document_id`, `revision_id`, `source_type`, `citation_id`, `row_reference`, atau `bounding_box` adalah kandidat, bukan schema yang telah disetujui.

## 8. Structured output dan streaming

Tiga lapisan perlu dipisahkan dalam keputusan kontrak:

1. **Output model:** bagaimana provider menghasilkan data sesuai schema.
2. **Payload aplikasi:** objek akhir yang divalidasi backend dan disimpan sebagai jawaban.
3. **Transport:** cara server mengirim progres, teks, hasil akhir, dan error ke browser.

Pilihan pembahasan, semuanya **TERBUKA**:

| Opsi | Bentuk | Konsekuensi |
| --- | --- | --- |
| JSON final non-streaming | Satu response JSON setelah validasi | Lebih sederhana; pengguna menunggu hasil final |
| Event stream dengan final JSON | Event progres/teks terpisah, kemudian objek final tervalidasi | Perlu event schema, status UI, aturan penyimpanan, dan error/cancel |
| Streaming structured delta | Field/delta dirakit secara bertahap | Perlu assembler dan state parsial; komponen belum boleh diperlakukan final sebelum validasi |

SSE, WebSocket, atau transport lain belum dipilih. Kontrak harus menjelaskan kapan pesan selesai, apa yang disimpan saat terputus, bagaimana retry bekerja, dan apakah komponen parsial ditampilkan.

## 9. Validasi yang diusulkan

### Backend

- Validasi request, kepemilikan session, akses, dan input multimodal sebelum retrieval.
- Validasi response menggunakan schema per jenis komponen, bukan menerima `details` arbitrer.
- Periksa citation reference terhadap sumber yang diambil dan scope pengguna.
- Hindari angka/tag/part number/relasi tanpa sumber yang sesuai dengan kebijakan grounding yang disepakati.
- Gunakan hasil SQL sebagai data perhitungan, bukan meminta model menghitung ulang secara bebas.
- Tetapkan batas retry untuk output invalid; kegagalan memiliki respons yang dapat dirender.
- Simpan final payload beserta versioning/provenance yang dipilih.

### Frontend

- Renderer menangani discriminant komponen dan versi schema yang didukung.
- State loading, partial, complete, insufficient-evidence, clarification, dan error mengikuti kontrak final; nama enum belum ditentukan.
- Tipe tak dikenal/payload invalid ditangani tanpa merender data teknis rekaan.
- Isi teks dirender melalui mekanisme yang sesuai format terpilih; konten sumber tidak menjadi kode atau URL storage bebas.
- Klik sitasi meminta file melalui jalur otorisasi aplikasi.

## 10. Skenario acceptance kontrak

**USULAN skenario pengujian, bukan hasil test:**

1. Masing-masing empat komponen memiliki payload valid yang dapat dirender dan payload invalid yang ditolak.
2. Pertanyaan umum tanpa equipment mempunyai bentuk respons yang disepakati.
3. Pertanyaan multi-equipment/multi-komponen mengikuti keputusan cardinality.
4. Bukti tidak cukup menghasilkan respons yang jujur, tanpa kutipan atau nilai buatan.
5. Dokumen yang berbeda menyatakan nilai berbeda; respons mempertahankan asal dan perbedaan bukti.
6. Citation PDF membuka file/revision/halaman yang benar.
7. Citation PNG membuka gambar/region sesuai keputusan locator.
8. Analitik maintenance memiliki angka, formula, unit, filter, dan rujukan sumber yang dapat direproduksi.
9. Pengguna tanpa akses tidak memperoleh sumber melalui citation endpoint langsung.
10. Provider mengembalikan JSON invalid, enum salah, refusal, timeout, atau respons tidak lengkap; API dan UI menangani sesuai kontrak error.
11. Stream terputus/retry/cancel tidak menghasilkan dua pesan final atau payload rusak yang dianggap selesai.
12. Riwayat yang dibuat dengan versi schema sebelumnya memiliki perilaku kompatibilitas yang telah ditentukan.

Nilai contoh untuk fixture engineering baru diambil setelah sumber diperiksa; data uji sintetis, bila digunakan, harus diberi label jelas.
