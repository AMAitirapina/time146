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
import unidecode
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

conversation_map = {}

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f'Oi, eu sou o {BOT_NAME}, qual é o seu nome')

    return CHOOSING_NAME

def begin(update: Update, context: CallbackContext) -> int:
    if 'name' in context.user_data:
        name = context.user_data['name']
        update.message.reply_text(f'Oi {name}, bem vindo de volta, o que anda fazendo?',)
        return INTERESTS

    else:
        update.message.reply_text(f'Oi, eu sou o {BOT_NAME}, qual é o seu nome')
        return CHOOSING_NAME

def set_name(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['name'] = text
    update.message.reply_text(f'Legal {text}, do que voce gosta?')

    return INTERESTS

def regular_choice(update: Update, context: CallbackContext) -> int:
    # Formatar o texto do usuario para lower case e sem acentos
    interest = unidecode.unidecode(update.message.text.lower())
    context.user_data['interest'] = interest

    if interest in conversation_map:
        update.message.reply_text(conversation_map[interest])
    # TODO: salvar o termo novo na memoria
    else:
        update.message.reply_text(f'Não ouvi falar sobre {interest}, me conta mais!')

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

    update.message.reply_text(f"I learned these facts about you. Until next time!")

    user_data.clear()
    return ConversationHandler.END

def main() -> None:

    conversation_file = open("conversation", "r")
    conversation_lines = conversation_file.read().split('\n')

    for i in range(0, len(conversation_lines), 2):
        conversation_map[conversation_lines[i]] = conversation_lines[i+1]

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
                MessageHandler(Filters.text, regular_choice),
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

# TODO: chamar o usuario (ser ativo)
# TODO: melhorar o fluxo de conversa
# TODO: guardar os interesses do usuario
if __name__ == '__main__':
    main()
