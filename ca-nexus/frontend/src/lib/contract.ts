/** T4.10/T5.6 — Frontend mirror of backend schemas/chat.py. Keep in sync manually. */
export const SCHEMA_VERSION = "v1";
export type ComponentType =
  | "procedure_checklist" | "interlock_logic" | "bom_table"
  | "root_cause_card" | "text_only" | "kpi_table" | "clarification";
export type AlertLevel = "normal" | "warning" | "critical";
export type Citation = {
  document_id?: string | null; document_title: string; page_number?: number | null;
  snippet: string; file_path: string; source_type: "pdf" | "png" | "xlsx";
  region?: string | null; bbox?: number[] | null; row_reference?: string | null;
};
export type Answer = {
  schema_version?: string; summary_text: string; equipment_tag?: string | null;
  related_tags?: string[]; component_type: ComponentType;
  component_payload: { title: string; alert_level: AlertLevel; details: Record<string, unknown>; insufficient_evidence?: boolean };
  citations: Citation[]; sql_query?: string | null; route?: string | null;
};
export const KNOWN_COMPONENTS: ComponentType[] = [
  "procedure_checklist", "interlock_logic", "bom_table",
  "root_cause_card", "text_only", "kpi_table", "clarification",
];
