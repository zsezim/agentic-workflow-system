MACHINES = [
    {"id": "Machine-A", "status": "busy", "materials": ["oak", "pine"]},
    {"id": "Machine-B", "status": "available", "materials": ["oak", "maple", "walnut"]},
    {"id": "Machine-C", "status": "available", "materials": ["pine", "maple"]},
]

def assign_machine(material: str):
    for machine in MACHINES:
        if material.lower() in machine["materials"]:
            if machine["status"] == "available":
                return {
                    "assigned_machine": machine["id"],
                    "reason": (
                        f"{machine['id']} selected because it supports {material} "
                        f"and is currently available."
                    ),
                }

    return {
        "assigned_machine": "manual_review",
        "reason": (
            f"No available machines support {material}, "
            "so manual intervention is required."
        ),
    }









