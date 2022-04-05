import Constants
import Content
import Firestore
from Logger import logger

import html
import json
from telegram import Update, ParseMode, ForceReply
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from time import sleep
import traceback

def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"""/word: replies the next word definition
/subscribe_daily: subscribes to the word of the day
/subscribe_hourly: subscribes to the word of the hour
/unsubscribe: unsubscribes to the word of the day
""")

def word_command(update: Update, context: CallbackContext) -> None:
    subscription = Firestore.next(update.effective_chat.id)
    if subscribe == None:
        update.message.reply_text("not subscribed yet")
        return
    content = Content.get(subscription.get(u'language'), subscription)
    update.message.reply_text(content)

def subscribe(update: Update, interval_s: int) -> None:
    subscription = Firestore.subscribe(update.effective_chat.id, interval_s)
    if subscription == None:
        update.message.reply_text("already subscribed")
        return
    content = Content.get(subscription.get(u'language'), subscription)
    update.message.reply_text(content)

def subscribe_daily_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, interval_s=86400)

def subscribe_hourly_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, interval_s=3600)

def unsubscribe_command(update: Update, context: CallbackContext) -> None:
    reply = "already unsubscribed"
    if Firestore.unsubscribe(update.effective_chat.id):
        reply = "unsubscription successful"
    update.message.reply_text(reply)

def log(update: Update, context: CallbackContext) -> None:
    """Log the user message."""
    user = update.effective_user
    logger.info(f"User {user.mention_markdown_v2()} chat_id {update.effective_chat.id} says {update.message.text}")

def get_updater(token: str) -> Updater:
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", start_command))
    dispatcher.add_handler(CommandHandler("word", word_command))
    dispatcher.add_handler(CommandHandler("subscribe_daily", subscribe_daily_command))
    dispatcher.add_handler(CommandHandler("subscribe_hourly", subscribe_hourly_command))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    # on non command i.e message - log the message
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, log))
    
    # Start the Bot
    updater.start_polling()

    return updater