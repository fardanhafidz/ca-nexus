# T0.3 — Golden Query Set (awal, tanpa persen sukses sebelum evaluasi)

Keputusan: D-26. Validator: TERBUKA (Q-QA-02). Setiap expected answer harus menunjuk
sumber di bawah, bukan output LLM.

| ID | Query | Jalur | Sumber acuan | Peran uji |
|---|---|---|---|---|
| G-01 | VSHH-4505 high vibration trip action on KC-4501? | vector+graph | OPL-KC-4501-05 + Interlock Logic Diagram KC-4501 | Mechanical, E&I |
| G-02 | Exact tag `SEQ-4501` — what does it protect? | exact-tag+graph | maintenance `Related_Interlock=SEQ-4501` + interlock PDF | E&I |
| G-03 | Mechanical seal spare parts for GA-1201A? | vector | Equipment GA Drawing GA-1201A | Mechanical |
| G-04 | Total downtime + cost EA-5601 vs YD-2301? | sql | maintenance rows tag EA-5601/YD-2301 | HSE&Rel, Process |
| G-05 | Corrective vs Preventive count KC-4501? | sql | maintenance `Work_Type` | HSE&Rel |
| G-06 | Cross-source: interlock + OPL for LV-6701 SEQ-6701? | vector+graph | Interlock LV-6701 + OPL LV-6701-* | E&I, Process |
| G-07 | Akses-ditolak: Mechanical tanya interlock E&I-only (bila mapping E&I-only aktif) | policy | expected: ditolak/tidak-bocor | semua divisi |
| G-08 | Bukti-kurang: `MTBF CT-7801` (formula belum disepakati) | sql→insufficient | expected: `insufficient_evidence=true`, tanpa angka rekaan | HSE&Rel |
| G-09 | Konflik revisi: dua revision OPL sama → tampilkan keduanya + versi | retrieval | expected: kedua bukti + label versi | Admin |
| G-10 | Ambigu: `trip` tanpa tag → klarifikasi | router | expected: pertanyaan klarifikasi, bukan tebakan equipment | semua |

Rubric: retrieval-hit (sumber benar), citation-correct (judul/halaman/snippet/locator),
grounding (tanpa klaim tanpa bukti), divisi-tidak-bocor, JSON-valid, angka-reproduksibel.
