def notify_team(order_id: str, messages: list[str]):
    return [f"Notification for {order_id}: {message}" for message in messages]