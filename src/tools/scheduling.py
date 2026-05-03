def schedule_order(order, machine_decision, qc_required: bool):
    return {
        "scheduled_start": "2026-05-04 09:00",
        "scheduled_end": "2026-05-04 15:00" if not qc_required else "2026-05-04 17:00",
        "qc_added": qc_required,
    }