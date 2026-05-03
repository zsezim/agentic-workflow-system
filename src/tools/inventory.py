INVENTORY = {
    "oak": 8,
    "pine": 50,
    "maple": 25,
    "walnut": 12,
}


def check_inventory(material: str, quantity: int):
    available = INVENTORY.get(material.lower(), 0)
    reorder_required = available < quantity

    return {
        "material": material,
        "required_quantity": quantity,
        "available_quantity": available,
        "status": "low_inventory" if reorder_required else "available",
        "reorder_required": reorder_required,
    }