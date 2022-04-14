import Constants
import Content
import Firestore
from Logger import logger

import html
import json
import random
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode, ForceReply
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater

from time import sleep
import traceback

def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"""/word: replies the next word definition
/daily_word: subscribes to the word of the day
/hourly_word: subscribes to the word of the hour
/quiz: asks for the definition of a word
/daily_quiz: subscribes to the quiz of the day
/hourly_quiz: subscribes to the quiz of the hour
/unsubscribe: unsubscribes from all subscriptions
""")

def word_command(update: Update, context: CallbackContext) -> None:
    subscription = Firestore.get_subscription_and_update_count(update.effective_chat.id)
    content = Content.get(subscription.get(u'language'), subscription)
    update.message.reply_markdown_v2(content)

def quiz_command(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    subscription = Firestore.get_subscription(update.effective_chat.id)
    (quiz, reply_markup) = get_quiz(subscription.get(u'language'), subscription)
    update.message.reply_markdown_v2(quiz, reply_markup=reply_markup)

def _get_markup(buttons: list) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1])],
        [InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])],
        [InlineKeyboardButton(buttons[2][0], callback_data=buttons[2][1])],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quiz(language: str, subscription: dict) -> tuple:
    words = Content.get_quiz(language, subscription)
    correct_answer_index = random.randint(0, 2)
    correct_answer = words[correct_answer_index]
    buttons = []
    for i in range(len(words)):
        callback_data = []
        for j in range(len(words)):
            if j == correct_answer_index:
                callback_data.append(f"✔ {words[j][0]} ✔")
            elif i == j:
                callback_data.append(f"❌ {words[j][0]} ❌")
            else:
                callback_data.append(f"  {words[j][0]}  ")
        callback_data = "\n".join(callback_data)
        buttons.append((f"  {words[i][0]}  ", callback_data))
    reply_markup = _get_markup(buttons)
    quiz = f"{correct_answer[2]} \\({correct_answer[1]}\\)"
    return (quiz, reply_markup)

def answer_quiz_button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    message = "" + query.data
    if message == "done":
        return
    words = message.split("\n")
    buttons = []
    for word in words:
        buttons.append((word, "done"))
    print(buttons)
    reply_markup = _get_markup(buttons)
    print(reply_markup)
    query.edit_message_reply_markup(reply_markup)

def subscribe(update: Update, interval_s: int, is_quiz: bool) -> None:
    subscription = Firestore.subscribe(update.effective_chat.id, interval_s, is_quiz)
    if subscription == None:
        update.message.reply_text("already subscribed")
        return
    if is_quiz:
        (quiz, reply_markup) = get_quiz(subscription.get(u'language'), subscription)
        update.message.reply_markdown_v2(quiz, reply_markup=reply_markup)
        return
    content = Content.get(subscription.get(u'language'), subscription)
    update.message.reply_markdown_v2(content)

def daily_word_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, interval_s=86400, is_quiz=False)

def hourly_word_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, interval_s=3600, is_quiz=False)

def daily_quiz_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, interval_s=86400, is_quiz=True)

def hourly_quiz_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, interval_s=3600, is_quiz=True)

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
    dispatcher.add_handler(CommandHandler("quiz", quiz_command))
    dispatcher.add_handler(CommandHandler("daily_word", daily_word_command))
    dispatcher.add_handler(CommandHandler("hourly_word", hourly_word_command))
    dispatcher.add_handler(CommandHandler("daily_quiz", daily_quiz_command))
    dispatcher.add_handler(CommandHandler("hourly_quiz", hourly_quiz_command))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    # on non command i.e message - log the message
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, log))

    updater.dispatcher.add_handler(CallbackQueryHandler(answer_quiz_button))
    
    # Start the Bot
    updater.start_polling()

    return updater