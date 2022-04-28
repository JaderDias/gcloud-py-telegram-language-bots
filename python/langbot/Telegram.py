import Constants
import Content
import Firestore.Poll
import Firestore.Subscriber
from Logger import logger

import html
import json
import random
import re
from telegram import\
    ForceReply,\
    Message,\
    ParseMode,\
    Poll,\
    Update
from telegram.ext import\
    CallbackContext,\
    CommandHandler,\
    Filters,\
    MessageHandler,\
    PollHandler,\
    Updater

from time import sleep
import traceback

"""
word - Shows the definition of a word
daily_word - Subscribes to the word of the day
hourly_word - Subscribes to the word of the hour
quiz - Tests your knowledge about the meaning of a word
daily_quiz - Subscribes to the quiz of the day
hourly_quiz - Subscribes to the quiz of the hour
unsubscribe - Unsubscribes from all subscriptions
"""

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
    subscription = Firestore.Subscriber.get_subscription_and_update_count(language, update.effective_chat.id)
    content = Content.get(subscription.get(u'language'), subscription)
    update.message.reply_text(content)

def _get_quiz(chat_id: int, publication_count: int) -> tuple:
    words = Content.get_quiz(language, chat_id, publication_count)
    correct_option_id = random.randint(1, len(words)) - 1
    logger.info(f"words {words} correct_option_id {correct_option_id}")
    correct_answer = words[correct_option_id]
    question = f"{correct_answer[2]} ({correct_answer[1]})"
    options = []
    for word in words:
        options.append(word[0])
    return (question, options, correct_option_id, correct_answer[3])

def quiz(updater: Updater, chat_id: int, subscription: dict) -> None:
    if not subscription:
        subscription = Firestore.Subscriber.get_subscription(language, chat_id)
    (question, options, correct_option_id, term_index) = _get_quiz(subscription["chat_id"], subscription["publication_count"])
    message = updater.bot.send_poll(
        chat_id,
        question,
        options,
        type=Poll.QUIZ,
        correct_option_id=correct_option_id,
    )
    Firestore.Poll.create(
        language,
        chat_id,
        message.poll.id,
        correct_option_id,
        options[correct_option_id],
        term_index
    )

def quiz_command(update: Update, context: CallbackContext) -> None:
    quiz(updater, update.effective_chat.id, None)

def receive_quiz_answer(update: Update, context: CallbackContext) -> None:
    print(update)
    poll = Firestore.Poll.get_and_increment_answer_count(update.poll.id, update.poll.options)
    if poll["total_answers"] == 0:
        quiz(updater, poll["chat_id"], None)

def subscribe(update: Update, context: CallbackContext, interval_s: int, is_quiz: bool) -> None:
    subscription = Firestore.Subscriber.subscribe(language, update.effective_chat.id, interval_s, is_quiz)
    if subscription == None:
        update.message.reply_text("already subscribed")
        return
    if is_quiz:
        quiz(updater, update.effective_chat.id, subscription)
        return
    content = Content.get(subscription.get(u'language'), subscription)
    update.message.reply_text(content)

def daily_word_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, context, interval_s=86400, is_quiz=False)

def hourly_word_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, context, interval_s=3600, is_quiz=False)

def daily_quiz_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, context, interval_s=86400, is_quiz=True)

def hourly_quiz_command(update: Update, context: CallbackContext) -> None:
    subscribe(update, context, interval_s=3600, is_quiz=True)

def unsubscribe_command(update: Update, context: CallbackContext) -> None:
    reply = "already unsubscribed"
    if Firestore.Subscriber.unsubscribe(language, update.effective_chat.id):
        reply = "unsubscription successful"
    update.message.reply_text(reply)

def log(update: Update, context: CallbackContext) -> None:
    """Log the user message."""
    user = update.effective_user
    logger.info(f"User {user.mention_markdown_v2()} chat_id {update.effective_chat.id} says {update.message.text}")

def get_updater(_language:str, token: str) -> Updater:
    # Create the Updater and pass it your bot's token.
    global language
    language = _language
    global updater
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", start_command))
    dispatcher.add_handler(CommandHandler("word", word_command))
    dispatcher.add_handler(CommandHandler("quiz", quiz_command))
    dispatcher.add_handler(PollHandler(receive_quiz_answer))
    dispatcher.add_handler(CommandHandler("daily_word", daily_word_command))
    dispatcher.add_handler(CommandHandler("hourly_word", hourly_word_command))
    dispatcher.add_handler(CommandHandler("daily_quiz", daily_quiz_command))
    dispatcher.add_handler(CommandHandler("hourly_quiz", hourly_quiz_command))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    # on non command i.e message - log the message
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, log))

    # Start the Bot
    updater.start_polling()

    return updater