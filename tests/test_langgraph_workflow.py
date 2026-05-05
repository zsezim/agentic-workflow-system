from src.models.schemas import ProductionOrder
from src.graph.langgraph_workflow import process_order_with_langgraph


def test_low_inventory_high_risk_adds_reorder_and_qc():
    order = ProductionOrder(
        order_id="ORD-1001",
        product_type="custom cabinet doors",
        material="oak",
        size="large",
        quantity=20,
        due_date="2026-05-10",
        priority="high",
    )

    result = process_order_with_langgraph(order)

    assert result["inventory"]["reorder_required"] is True
    assert result["defect_risk"]["qc_required"] is True
    assert result["schedule"]["qc_added"] is True
    assert len(result["workflow_steps"]) > 0
    assert len(result["decision_log"]) > 0


def test_sufficient_inventory_low_risk_skips_reorder_and_qc():
    order = ProductionOrder(
        order_id="ORD-1002",
        product_type="standard shelf",
        material="pine",
        size="small",
        quantity=5,
        due_date="2026-05-12",
        priority="normal",
    )

    result = process_order_with_langgraph(order)

    assert result["inventory"]["reorder_required"] is False
    assert result["defect_risk"]["qc_required"] is False
    assert result["schedule"]["qc_added"] is False

    steps = " ".join(result["workflow_steps"]).lower()
    assert "reorder" not in steps
    assert "qc inspection added" not in steps


def test_machine_assignment_returns_valid_machine():
    order = ProductionOrder(
        order_id="ORD-1003",
        product_type="cabinet frame",
        material="maple",
        size="medium",
        quantity=10,
        due_date="2026-05-15",
        priority="normal",
    )

    result = process_order_with_langgraph(order)

    assert result["machine"]["assigned_machine"] in [
        "Machine-A",
        "Machine-B",
        "Machine-C",
        "manual_review",
    ]


def test_decision_log_contains_required_fields():
    order = ProductionOrder(
        order_id="ORD-1004",
        product_type="custom cabinet doors",
        material="oak",
        size="large",
        quantity=20,
        due_date="2026-05-10",
        priority="high",
    )

    result = process_order_with_langgraph(order)

    first_decision = result["decision_log"][0]

    assert "step" in first_decision
    assert "decision" in first_decision
    assert "reason" in first_decision
    assert "inputs" in first_decision
    assert "outputs" in first_decision