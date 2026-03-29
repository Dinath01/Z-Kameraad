active_chats: dict[str, dict] = {}
pending_requests: dict[str, str] = {}
online_peers: set[str] = set()
chat_messages: dict[str, list[dict]] = {}