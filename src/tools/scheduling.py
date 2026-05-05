def schedule_order(order, machine_decision, qc_required: bool):
    start = "2026-05-04 09:00"
    end = "2026-05-04 15:00" if not qc_required else "2026-05-04 17:00"

    if qc_required:
        reason = "QC inspection required, so additional buffer time was added."
    else:
        reason = "No QC required, standard scheduling applied."

    return {
        "scheduled_start": start,
        "scheduled_end": end,
        "qc_added": qc_required,
        "reason": reason,
    }