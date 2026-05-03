from pydantic import BaseModel
from typing import Optional, List


class ProductionOrder(BaseModel):
    order_id: str
    product_type: str
    material: str
    size: str
    quantity: int
    due_date: str
    priority: str


class InventoryDecision(BaseModel):
    material: str
    required_quantity: int
    available_quantity: int
    status: str
    reorder_required: bool


class DefectRiskDecision(BaseModel):
    risk_score: float
    risk_level: str
    qc_required: bool


class MachineDecision(BaseModel):
    assigned_machine: str
    reason: str


class ScheduleDecision(BaseModel):
    scheduled_start: str
    scheduled_end: str
    qc_added: bool


class WorkflowResult(BaseModel):
    order_id: str
    inventory: InventoryDecision
    defect_risk: DefectRiskDecision
    machine: MachineDecision
    schedule: ScheduleDecision
    notifications: List[str]
    final_summary: str