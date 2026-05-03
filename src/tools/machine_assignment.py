MACHINES = [
    {"id": "Machine-A", "status": "busy", "materials": ["oak", "pine"]},
    {"id": "Machine-B", "status": "available", "materials": ["oak", "maple", "walnut"]},
    {"id": "Machine-C", "status": "available", "materials": ["pine", "maple"]},
]


def assign_machine(material: str):
    for machine in MACHINES:
        if machine["status"] == "available" and material.lower() in machine["materials"]:
            return {
                "assigned_machine": machine["id"],
                "reason": f"{machine['id']} is available and supports {material}.",
            }

    return {
        "assigned_machine": "manual_review",
        "reason": "No available compatible machine found.",
    }