context = {}

def clear_user_context(user_id):
    if user_id in context:
        del context[user_id]
