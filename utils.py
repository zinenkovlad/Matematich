class Player:
    def __init__(self, id_table, user_id, username, n_pes, n_matematich):
        self.id = id_table
        self.user_id = user_id
        self.username = username
        self.n_pes = n_pes
        self.n_matematich = n_matematich


def get_chat_name(message):
    return 'chat_' + str(abs(message.chat.id))
