import Constants
import Content
from Logger import logger
import Firestore
import Secrets
import Storage
import Telegram

from datetime import datetime, timedelta
from time import sleep
from telegram.ext import Updater

def get_updater(language: str, token: str) -> Updater:
    Storage.get_dictionary(language)
    updater = Telegram.get_updater(token)
    subscriptions = Firestore.read()
    for subscription in subscriptions:
        content = Content.get(language, subscription)
        updater.bot.send_message(chat_id=subscription['chat_id'], text=content)
    return updater

def app(event, context) -> None:
    end_time = datetime.now() + timedelta(minutes=8)
    language = Firestore.get_language()
    if language == "":
        logger.info("no language found")
        return
    token = Secrets.access_secret_version(f"telegram-{language}-token")
    try:
        updater = get_updater(language, token)
        sleep((end_time - datetime.now()).total_seconds())

        if updater.persistence:
            # Update user_data, chat_data and bot_data before flushing
            updater.dispatcher.update_persistence()
            updater.persistence.flush()
        updater.stop()
    finally:
        Firestore.release_lock()

if __name__ == '__main__':
    language = Firestore.get_language()
    if language == "":
        logger.info("no language found")
        exit()
    token = Secrets.access_secret_version(f"telegram-dev-token")
    try:
        updater = get_updater(language, token)

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
    finally:
        Firestore.release_lock()