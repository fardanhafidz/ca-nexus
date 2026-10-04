# T2.2 — Data Dictionary Maintenance (sumber: header workbook aktual)

Sheet: `Maintenance History (All Equipm` (potongan 31-char). PK: `wo_number`.
Lineage: workbook/sheet/row + versi import (disimpan di `import_batches` — lihat T2.3).

| # | Header asli | Kolom SQL | Tipe | Null | Catatan |
|---|---|---|---|---|---|
| 1 | WO_Number | wo_number | TEXT PK | NO | unik, 211/211 terisi |
| 2 | Notification_No | notification_no | TEXT | YES | |
| 3 | Report_Date | report_date | TIMESTAMPTZ | YES | YYYY-MM-DD dinormalisasi |
| 4 | Start_Date | start_date | TIMESTAMPTZ | YES | |
| 5 | Completion_Date | completion_date | TIMESTAMPTZ | YES | |
| 6 | Status | status | TEXT | YES | Completed/In Progress/Planned |
| 7 | Equipment_Tag | equipment_tag | TEXT idx | YES | 8 tag; JOIN key dokumen |
| 8 | Equipment_Name | equipment_name | TEXT | YES | |
| 9 | Functional_Location | functional_location | TEXT | YES | |
| 10 | Area_Code | area_code | TEXT | YES | angka disimpan sebagai teks (menjaga `4500` vs `4500.0`) |
| 11 | Area_Name | area_name | TEXT | YES | |
| 12 | Plant | plant | TEXT | YES | LLDPE unit |
| 13 | Work_Type | work_type | TEXT idx | YES | Corrective/Preventive/Predictive/Inspection/Calibration/Overhaul |
| 14 | Discipline | discipline | TEXT idx | YES | Mechanical/Instrument/Electrical/Process → dipakai scope divisi T3.4 |
| 15 | Priority | priority | TEXT | YES | Emergency/High/Medium/Low |
| 16 | Criticality | criticality | TEXT | YES | |
| 17 | Problem_Description | problem_description | TEXT | YES | |
| 18 | Root_Cause | root_cause | TEXT | YES | sumber RCA (D-07) |
| 19 | Corrective_Action | corrective_action | TEXT | YES | |
| 20 | Spare_Parts_Used | spare_parts_used | TEXT | YES | `-` = tidak ada (bukan NULL) |
| 21 | Breakdown | breakdown | TEXT | YES | Yes/No |
| 22 | Downtime_Hours | downtime_hours | DOUBLE | YES | jam; kosong → NULL (bukan 0) |
| 23 | Labor_Hours | labor_hours | DOUBLE | YES | |
| 24 | Labor_Cost_IDR | labor_cost_idr | DOUBLE | YES | IDR |
| 25 | Material_Cost_IDR | material_cost_idr | DOUBLE | YES | IDR |
| 26 | Total_Cost_IDR | total_cost_idr | DOUBLE | YES | IDR |
| 27 | Reported_By | reported_by | TEXT | YES | |
| 28 | Executed_By | executed_by | TEXT | YES | |
| 29 | Approved_By | approved_by | TEXT | YES | |
| 30 | Related_Interlock | related_interlock | TEXT idx | YES | `SEQ-xxxx`; `-`/kosong = tanpa relasi |
| 31 | Remarks | remarks | TEXT | YES | |

Selisih vs brief: tidak ada — 211 baris × 31 kolom TERKONFIRMASI (menggantikan BRIEF).
Disiplin→divisi (T3.4, usulan eksplisit): Mechanical→Mechanical,
Instrument/Electrical→Electrical & Instrumentation, Process→Process / Operations,
selain itu → terlihat semua divisi (agregat lintas-divisi hanya untuk Admin).
