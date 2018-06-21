def get_chat_name(message):
    return 'chat_' + str(abs(message.chat.id))