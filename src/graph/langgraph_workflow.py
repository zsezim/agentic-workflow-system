from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END

from src.models.schemas import ProductionOrder
from src.tools.inventory import check_inventory
from src.tools.defect_risk import predict_defect_risk
from src.tools.machine_assignment import assign_machine
from src.tools.scheduling import schedule_order
from src.tools.notifications import notify_team


class ManufacturingState(TypedDict, total=False):
    order: ProductionOrder
    inventory: Dict[str, Any]
    defect_risk: Dict[str, Any]
    machine: Dict[str, Any]
    schedule: Dict[str, Any]
    notifications: List[str]
    workflow_steps: List[str]
    decision_log: List[Dict[str, Any]]
    final_summary: str

def add_step(state, message: str):
    return state.get("workflow_steps", []) + [message]

def add_decision(
    state: ManufacturingState,
    step: str,
    decision: str,
    reason: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return state.get("decision_log", []) + [
        {
            "step": step,
            "decision": decision,
            "reason": reason,
            "inputs": inputs,
            "outputs": outputs,
        }
    ]

def inventory_node(state: ManufacturingState) -> ManufacturingState:
    order = state["order"]
    inventory = check_inventory(order.material, order.quantity)

    return {
        "inventory": inventory,
        "workflow_steps": add_step(
            state,
            f"Checked inventory → {inventory['reason']}"
        ),
        "decision_log": add_decision(
            state,
            step="inventory_check",
            decision="reorder_required" if inventory["reorder_required"] else "inventory_available",
            reason=inventory["reason"],
            inputs={
                "material": order.material,
                "required_quantity": order.quantity,
            },
            outputs=inventory,
        ),
    }

def reorder_node(state: ManufacturingState) -> ManufacturingState:
    order = state["order"]
    inventory = state["inventory"]

    message = (
        f"Low inventory for {order.material}. "
        f"Required: {inventory['required_quantity']}, "
        f"Available: {inventory['available_quantity']}. "
        "Reorder request created."
    )

    return {
        "notifications": state.get("notifications", []) + [message],
        "workflow_steps": add_step(
            state,
            f"Reorder request created → {inventory['reason']}"
        ),
        "decision_log": add_decision(
            state,
            step="reorder_request",
            decision="created_reorder_request",
            reason=inventory["reason"],
            inputs={
                "material": order.material,
                "required_quantity": inventory["required_quantity"],
                "available_quantity": inventory["available_quantity"],
            },
            outputs={
                "reorder_created": True,
                "message": message,
            },
        ),
    }


def defect_risk_node(state: ManufacturingState) -> ManufacturingState:
    order = state["order"]
    defect_risk = predict_defect_risk(order)

    return {
        "defect_risk": defect_risk,
        "workflow_steps": add_step(
            state,
            f"Defect risk evaluated → {defect_risk['reason']}"
        ),
        "decision_log": add_decision(
            state,
            step="defect_risk_evaluation",
            decision="qc_required" if defect_risk["qc_required"] else "qc_not_required",
            reason=defect_risk["reason"],
            inputs={
                "material": order.material,
                "size": order.size,
                "priority": order.priority,
                "quantity": order.quantity,
            },
            outputs=defect_risk,
        ),
    }

def qc_node(state: ManufacturingState) -> ManufacturingState:
    defect_risk = state["defect_risk"]

    message = (
        f"High defect risk detected. "
        f"Risk score: {defect_risk['risk_score']}. "
        "QC inspection added."
    )

    return {
        "notifications": state.get("notifications", []) + [message],
        "workflow_steps": add_step(
            state,
            "QC inspection added because defect risk was high."
        ),
        "decision_log": add_decision(
            state,
            step="quality_control",
            decision="added_qc_inspection",
            reason=defect_risk["reason"],
            inputs={
                "risk_score": defect_risk["risk_score"],
                "risk_level": defect_risk["risk_level"],
            },
            outputs={
                "qc_added": True,
                "message": message,
            },
        ),
    }

def machine_assignment_node(state: ManufacturingState) -> ManufacturingState:
    order = state["order"]
    machine = assign_machine(order.material)

    return {
        "machine": machine,
        "workflow_steps": add_step(
            state,
            f"Machine assigned → {machine['reason']}"
        ),
        "decision_log": add_decision(
            state,
            step="machine_assignment",
            decision=machine["assigned_machine"],
            reason=machine["reason"],
            inputs={
                "material": order.material,
                "product_type": order.product_type,
            },
            outputs=machine,
        ),
    }

def manual_review_node(state: ManufacturingState) -> ManufacturingState:
    machine = state["machine"]

    message = f"Manual review required. Reason: {machine['reason']}"

    return {
        "notifications": state.get("notifications", []) + [message],
        "workflow_steps": add_step(
            state,
            "Manual review required because no compatible available machine was found."
        ),
        "decision_log": add_decision(
            state,
            step="manual_review",
            decision="routed_to_manual_review",
            reason=machine["reason"],
            inputs=machine,
            outputs={
                "manual_review_required": True,
                "message": message,
            },
        ),
    }

def scheduling_node(state: ManufacturingState) -> ManufacturingState:
    order = state["order"]
    machine = state["machine"]
    defect_risk = state["defect_risk"]

    schedule = schedule_order(
        order=order,
        machine_decision=machine,
        qc_required=defect_risk["qc_required"],
    )

    return {
        "schedule": schedule,
        "workflow_steps": add_step(
            state,
            f"Production scheduled → {schedule['reason']}"
        ),
        "decision_log": add_decision(
            state,
            step="scheduling",
            decision="scheduled_order",
            reason=schedule["reason"],
            inputs={
                "order_id": order.order_id,
                "machine": machine["assigned_machine"],
                "qc_required": defect_risk["qc_required"],
                "due_date": order.due_date,
            },
            outputs=schedule,
        ),
    }

def notification_node(state: ManufacturingState) -> ManufacturingState:
    order = state["order"]
    messages = state.get("notifications", [])

    messages.append(
        f"Order {order.order_id} assigned to "
        f"{state['machine']['assigned_machine']}."
    )
    messages.append("Production team notified.")

    notification_result = notify_team(order.order_id, messages)

    return {
        "notifications": notification_result["notifications"],
        "workflow_steps": add_step(
            state,
            f"Notifications sent → {notification_result['reason']}"
        ),
        "decision_log": add_decision(
            state,
            step="notifications",
            decision="sent_notifications",
            reason=notification_result["reason"],
            inputs={
                "order_id": order.order_id,
                "message_count": len(messages),
            },
            outputs=notification_result,
        ),
    }

def finalizer_node(state: ManufacturingState) -> ManufacturingState:
    order = state["order"]
    inventory = state["inventory"]
    defect_risk = state["defect_risk"]
    machine = state["machine"]
    schedule = state.get("schedule", {})

    final_summary = (
        f"Order {order.order_id} processed successfully. "
        f"Inventory status: {inventory['status']}. "
        f"Defect risk: {defect_risk['risk_level']} "
        f"with score {defect_risk['risk_score']}. "
        f"Machine assigned: {machine['assigned_machine']}. "
        f"QC required: {defect_risk['qc_required']}. "
        f"Scheduled from {schedule.get('scheduled_start')} "
        f"to {schedule.get('scheduled_end')}."
    )

    return {
        "final_summary": final_summary,
        "workflow_steps": add_step(
            state,
            "Final workflow summary generated."
        ),   
        
    }


def route_after_inventory(state: ManufacturingState) -> str:
    if state["inventory"]["reorder_required"]:
        return "reorder"
    return "defect_risk"


def route_after_defect_risk(state: ManufacturingState) -> str:
    if state["defect_risk"]["qc_required"]:
        return "qc"
    return "machine_assignment"


def route_after_machine_assignment(state: ManufacturingState) -> str:
    if state["machine"]["assigned_machine"] == "manual_review":
        return "manual_review"
    return "scheduling"


def build_manufacturing_graph():
    graph = StateGraph(ManufacturingState)

    graph.add_node("inventory", inventory_node)
    graph.add_node("reorder", reorder_node)
    graph.add_node("defect_risk", defect_risk_node)
    graph.add_node("qc", qc_node)
    graph.add_node("machine_assignment", machine_assignment_node)
    graph.add_node("manual_review", manual_review_node)
    graph.add_node("scheduling", scheduling_node)
    graph.add_node("notification", notification_node)
    graph.add_node("finalizer", finalizer_node)

    graph.add_edge(START, "inventory")

    graph.add_conditional_edges(
        "inventory",
        route_after_inventory,
        {
            "reorder": "reorder",
            "defect_risk": "defect_risk",
        },
    )

    graph.add_edge("reorder", "defect_risk")

    graph.add_conditional_edges(
        "defect_risk",
        route_after_defect_risk,
        {
            "qc": "qc",
            "machine_assignment": "machine_assignment",
        },
    )

    graph.add_edge("qc", "machine_assignment")

    graph.add_conditional_edges(
        "machine_assignment",
        route_after_machine_assignment,
        {
            "manual_review": "manual_review",
            "scheduling": "scheduling",
        },
    )

    graph.add_edge("manual_review", "notification")
    graph.add_edge("scheduling", "notification")
    graph.add_edge("notification", "finalizer")
    graph.add_edge("finalizer", END)

    return graph.compile()


def process_order_with_langgraph(order: ProductionOrder):
    app = build_manufacturing_graph()

    result = app.invoke(
    {
        "order": order,
        "notifications": [],
        "workflow_steps": [],
        "decision_log": [],
    }
)
    
    return {
    "order_id": order.order_id,
    "inventory": result.get("inventory"),
    "defect_risk": result.get("defect_risk"),
    "machine": result.get("machine"),
    "schedule": result.get("schedule"),
    "notifications": result.get("notifications"),
    "workflow_steps": result.get("workflow_steps"),
    "decision_log": result.get("decision_log"),
    "final_summary": result.get("final_summary"),
}
    
    
    
    
    
    
    
    
    








