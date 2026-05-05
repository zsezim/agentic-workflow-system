def notify_team(order_id: str, messages: list[str]):
    return {
        "notifications": [
            f"Notification for {order_id}: {message}" for message in messages
        ],
        "reason": "Notifications were sent to relevant teams based on workflow decisions.",
    }