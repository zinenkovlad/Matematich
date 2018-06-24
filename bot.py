import sys
import telebot
import random
import config
from SQLighter import SQLighter
from utils import get_chat_name
from time import sleep

bot = telebot.TeleBot(sys.argv[1])


@bot.message_handler(commands=['reg'])
def register_users(message):
    db_worker = SQLighter(config.database_name)
    chat = get_chat_name(message)
    registered_chats = db_worker.get_registered_chats()

    if chat in registered_chats:
        registered_users = db_worker.get_registered_users(chat)
        if message.from_user.id not in registered_users:
            db_worker.register_user(chat, message.from_user.id, message.from_user.username)
    else:
        # New chat. Create needed tables and register this user
        db_worker.create_new_chat_tables(chat, message.from_user.id, message.from_user.username)
    db_worker.close()


@bot.message_handler(commands=['game'])
def play(message):
    db_worker = SQLighter(config.database_name)
    chat = get_chat_name(message)
    registered_chats = db_worker.get_registered_chats()

    if chat in registered_chats:
        played = db_worker.is_played(chat)
        if not played:
            n_players = db_worker.count_users(chat)
            winner = db_worker.get_winner(chat, random.randint(1, n_players))
            losers = db_worker.get_losers(chat, winner.id)

            words = config.common_words.copy()
            words.insert(-1, '@' + winner.username)

            if losers:
                words.append(", ".join(['@' + loser.username for loser in losers]))
            else:
                del words[-1]
                words.append("а псов нет как бы")

            for word in words:
                bot.send_message(message.chat.id, word)
                sleep(2.0)

            db_worker.update_tables(chat, winner, losers)
        else:
            bot.send_message(message.chat.id, "Хватит одного математика на сегодня")
    else:
        bot.send_message(
            message.chat.id,
            "Чтобы начать нужен хотя бы один зарегистрированный математик. Регистрация по команде /reg"
        )
    db_worker.close()


@bot.message_handler(commands=['stats'])
def get_stats(message):
    db_worker = SQLighter(config.database_name)
    chat = 'chat_' + str(abs(message.chat.id))
    stats = db_worker.get_stats(chat)
    bot.send_message(message.chat.id, "Топ математиков:\n\n" + stats)


@bot.message_handler(commands=['more'])
def nullify(message):
    # TODO: make this command available only for admins
    db_worker = SQLighter(config.database_name)
    chat = 'chat_' + str(abs(message.chat.id))
    db_worker.nullify_is_played(chat)
    bot.send_message(message.chat.id, "Ок, можно роллить")


@bot.message_handler(content_types=["text"])
def remind_of_game(message):
    bot.send_message(message.chat.id, "Нажми один раз /reg, а затем всегда /game")


if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)
