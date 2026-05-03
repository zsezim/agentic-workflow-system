from src.tools.inventory import check_inventory
from src.tools.defect_risk import predict_defect_risk
from src.tools.machine_assignment import assign_machine
from src.tools.scheduling import schedule_order
from src.tools.notifications import notify_team


def process_order(order):
    inventory = check_inventory(order.material, order.quantity)
    defect_risk = predict_defect_risk(order)
    machine = assign_machine(order.material)
    schedule = schedule_order(order, machine, defect_risk["qc_required"])

    messages = []

    if inventory["reorder_required"]:
        messages.append(f"Low inventory for {order.material}. Reorder request created.")

    if defect_risk["qc_required"]:
        messages.append("High defect risk detected. QC inspection added.")

    messages.append(f"Order assigned to {machine['assigned_machine']}.")
    messages.append("Production team notified.")

    notifications = notify_team(order.order_id, messages)

    final_summary = (
        f"Order {order.order_id} processed. "
        f"Inventory status: {inventory['status']}. "
        f"Defect risk: {defect_risk['risk_level']}. "
        f"Machine: {machine['assigned_machine']}. "
        f"QC required: {defect_risk['qc_required']}."
    )

    return {
        "order_id": order.order_id,
        "inventory": inventory,
        "defect_risk": defect_risk,
        "machine": machine,
        "schedule": schedule,
        "notifications": notifications,
        "final_summary": final_summary,
    }