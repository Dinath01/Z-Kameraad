def match_peer(burnout_level: int):

    if burnout_level == 2:
        return {
            "peer_type": "experienced",
            "message": "Connecting you with a supportive peer who can help you through this."
        }

    elif burnout_level == 1:
        return {
            "peer_type": "similar",
            "message": "Connecting you with someone going through a similar experience."
        }

    else:
        return {
            "peer_type": "casual",
            "message": "Connecting you with a friendly peer to chat."
        }