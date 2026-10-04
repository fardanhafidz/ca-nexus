"""T4.10 — Versioned answer contract (D-17). Backend Pydantic source of truth.

`details` is discriminated per component_type — never a free object for the
renderer. Frontend mirrors these shapes in `src/lib/contract.ts` (T5.6).
Runtime must send exactly one enum value (never `a | b` strings).
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any, Literal

SCHEMA_VERSION = "v1"

ComponentType = Literal[
    "procedure_checklist", "interlock_logic", "bom_table",
    "root_cause_card", "text_only", "kpi_table", "clarification",
]
AlertLevel = Literal["normal", "warning", "critical"]


class ChecklistStep(BaseModel):
    step: int | None = None
    instruction: str = ""
    parameter: str | None = None
    unit: str | None = None


class ProcedureDetails(BaseModel):
    procedure: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    steps: list[ChecklistStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class InterlockCause(BaseModel):
    instrument_tag: str | None = None
    condition: str | None = None
    comparator: str | None = None
    setpoint: str | None = None  # string keeps unit + unknown distinct from 0
    unit: str | None = None
    voting: str | None = None
    delay: str | None = None
    effect: str | None = None


class InterlockDetails(BaseModel):
    interlock_id: str = ""
    causes: list[InterlockCause] = Field(default_factory=list)
    reset: str | None = None


class BomItem(BaseModel):
    item_no: str | None = None
    description: str = ""
    part_number: str | None = None
    quantity: str | None = None  # string: missing vs "0" stay distinct
    unit: str | None = None
    material: str | None = None


class BomDetails(BaseModel):
    drawing: str = ""
    revision: str | None = None
    items: list[BomItem] = Field(default_factory=list)


class RootCauseDetails(BaseModel):
    anomaly: str = ""
    recorded_cause: str | None = None
    hypothesis: str | None = None  # labeled unverified when present
    recommendation: str | None = None
    record_refs: list[str] = Field(default_factory=list)
    limitations: str | None = None


class KpiDetails(BaseModel):
    rows: list[dict[str, Any]] = Field(default_factory=list)
    query: str = ""
    unit_notes: str = "downtime_hours in hours; costs in IDR (no conversion); NULL ignored"


class ClarificationDetails(BaseModel):
    question: str = ""
    options: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    document_id: str | None = None
    document_title: str = ""
    page_number: int | None = None
    snippet: str = ""
    file_path: str = ""
    source_type: Literal["pdf", "png", "xlsx"] = "pdf"
    region: str | None = None
    bbox: list[float] | None = None  # DEL-B9: [x0,y0,x1,y1] normalized 0..1, PNG regions
    row_reference: str | None = None

    @field_validator("file_path", mode="before")
    @classmethod
    def _path_str(cls, v):
        return v if isinstance(v, str) else ""  # models emit null; registry fills the real path

    @field_validator("source_type", mode="before")
    @classmethod
    def _source_known(cls, v, info):
        if v in ("pdf", "png", "xlsx"):
            return v
        title = str((info.data or {}).get("document_title", "")).lower()
        if title.endswith(".png"):
            return "png"
        if title.endswith((".xlsx", ".xls")):
            return "xlsx"
        return "pdf"  # resolver still drops unmapped titles; this only keeps parse alive


class ComponentPayload(BaseModel):
    title: str = ""
    alert_level: AlertLevel = "normal"
    details: dict[str, Any] = Field(default_factory=dict)
    insufficient_evidence: bool = False


class ChatAnswer(BaseModel):
    schema_version: str = SCHEMA_VERSION
    summary_text: str = ""
    equipment_tag: str | None = None
    related_tags: list[str] = Field(default_factory=list)
    component_type: ComponentType = "text_only"
    component_payload: ComponentPayload = Field(default_factory=ComponentPayload)
    citations: list[Citation] = Field(default_factory=list)
    sql_query: str | None = None
    route: str | None = None  # T4.7 route trace: sql|vector|graph|combined

    @model_validator(mode="after")
    def _check_details(self) -> "ChatAnswer":
        # T4.10: details are validated per component_type at parse time —
        # never a free object. Invalid details raise (callers recover to
        # insufficient-evidence; see api/chat.py).
        model = DETAIL_MODELS.get(self.component_type)
        if model is not None:
            model(**(self.component_payload.details or {}))
        return self


class ErrorAnswer(BaseModel):
    schema_version: str = SCHEMA_VERSION
    error: str = ""
    retryable: bool = True


class ChatAsk(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=4000)
    attachment_id: str | None = None


DETAIL_MODELS = {
    "procedure_checklist": ProcedureDetails,
    "interlock_logic": InterlockDetails,
    "bom_table": BomDetails,
    "root_cause_card": RootCauseDetails,
    "kpi_table": KpiDetails,
    "clarification": ClarificationDetails,
}
