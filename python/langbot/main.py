import Constants
import Content
from Logger import logger
import Firestore.Language
import Firestore.Poll
import Firestore.Subscriber
import PubSub
import Secrets
import Storage
import Telegram

from datetime import datetime, timedelta
import os
from time import sleep
from telegram import ParseMode
from telegram.ext import Updater

def get_updater(language: str, token: str) -> Updater:
    logger.info(f"get_updater {language}")
    Storage.get_dictionary(language)
    updater = Telegram.get_updater(language, token)
    subscriptions = Firestore.Subscriber.get_pending_messages(language)
    for subscription in subscriptions:
        chat_id = subscription['chat_id']
        if subscription['is_quiz']:
            if not Firestore.Poll.has_answers(language, chat_id):
                continue
            Telegram.quiz(updater, chat_id, subscription)
            continue
        content = Content.get(language, subscription)
        updater.bot.send_message(chat_id, text=content, reply_markup=reply_markup)
    return updater

def app(event, context) -> None:
    end_time = datetime.now() + timedelta(minutes=8)
    language = Firestore.Language.get()
    if language == "":
        logger.info("no language found")
        return
    token = Secrets.access_secret_version(f"telegram-{language}-token")
    try:
        updater = get_updater(language, token)
        sleep_time = (end_time - datetime.now()).total_seconds()
        logger.info(f"will sleep for {sleep_time} seconds")
        sleep(sleep_time)

        if updater.persistence:
            # Update user_data, chat_data and bot_data before flushing
            updater.dispatcher.update_persistence()
            updater.persistence.flush()
        updater.stop()
    finally:
        Firestore.Language.release_lock(language)
    PubSub.publish(language)

if __name__ == '__main__':
    os.environ["LANGUAGE_CODE"] = "sh"
    language = Firestore.Language.get()
    if language == "":
        language = "sh"
    token = Secrets.access_secret_version(f"telegram-dev-token")
    updater = get_updater(language, token)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    PubSub.publish(language)
