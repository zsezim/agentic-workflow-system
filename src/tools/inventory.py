INVENTORY = {
    "oak": 8,
    "pine": 50,
    "maple": 25,
    "walnut": 12,
}

def check_inventory(material: str, quantity: int):
    available = INVENTORY.get(material.lower(), 0)
    reorder_required = available < quantity

    status = "low_inventory" if reorder_required else "available"

    if reorder_required:
        reason = (
            f"Available inventory ({available}) is less than required quantity ({quantity})."
        )
    else:
        reason = (
            f"Available inventory ({available}) is sufficient for required quantity ({quantity})."
        )

    return {
        "material": material,
        "required_quantity": quantity,
        "available_quantity": available,
        "status": status,
        "reorder_required": reorder_required,
        "reason": reason,
    }