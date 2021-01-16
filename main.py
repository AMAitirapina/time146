#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import Dict
from os import getenv

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    PicklePersistence
)

from dotenv import load_dotenv
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING_NAME, INTERESTS = range(2)

TOKEN = getenv("TOKEN")
BOT_NAME = getenv("BOT_NAME")

# reply_keyboard = [
#     ['Age', 'Favourite colour'],
#     ['Number of siblings', 'Something else...'],
#     ['Done'],
# ]
# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        f'Oi, eu sou o {BOT_NAME}, qual é o seu nome',
    )

    return CHOOSING_NAME

def begin(update: Update, context: CallbackContext) -> int:

    if 'name' in context.user_data:
        name = context.user_data['name']
        update.message.reply_text(f'Oi {name}, bem vindo de volta',)
        return INTERESTS

    else:
        update.message.reply_text(
            f'Oi, como voce se chama?',
        )
        return CHOOSING_NAME

def set_name(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['name'] = text
    update.message.reply_text(f'Legal {text}, do que voce gosta?')

    return INTERESTS

def regular_choice(update: Update, context: CallbackContext) -> int:
    interest = update.message.text
    context.user_data['interest'] = interest

    if interest == "futebol":
        update.message.reply_text(
            'Sabia que voce pode fazer uma parabola chutando uma bola?')
    elif interest == "culinaria":
        update.message.reply_text(
            'Sabia que voce pode aprender quimica cozinhando?')

    return INTERESTS


def custom_choice(update: Update, context: CallbackContext) -> int:
    interest = update.message.text
    update.message.reply_text(
        f'Não ouvi falar sobre {interest}, me conta mais!'
    )
    # TODO: estado do me conta mais
    return INTERESTS

# def received_information(update: Update, context: CallbackContext) -> int:
#     user_data = context.user_data
#     text = update.message.text
#     category = user_data['choice']
#     user_data[category] = text
#     del user_data['choice']

#     update.message.reply_text(
#         "Neat! Just so you know, this is what you already told me:"
#         f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
#         " on something.",
#         reply_markup=markup,
#     )

#     return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"I learned these facts about you. Until next time!"
    )

    user_data.clear()
    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    pp = PicklePersistence(filename='savedata')
    updater = Updater(TOKEN,persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.text, begin),
        ],
        states={
            CHOOSING_NAME: [
                MessageHandler(Filters.text, set_name),
            ],
            INTERESTS: [
                MessageHandler(
                    Filters.regex(
                        '^(futebol|culinaria)$'), regular_choice
                ),
                MessageHandler(Filters.text, custom_choice),
            ],
            # CHOOSING: [
            #     MessageHandler(
            #         Filters.regex('^(Age|Favourite colour|Number of siblings)$'), regular_choice
            #     ),
            #     MessageHandler(Filters.regex('^Something else...$'), custom_choice),
            # ],
            # TYPING_CHOICE: [
            #     MessageHandler(
            #         Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
            #     )
            # ],
            # TYPING_REPLY: [
            #     MessageHandler(
            #         Filters.text & ~(Filters.command | Filters.regex('^Done$')),
            #         received_information,
            #     )
            # ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
