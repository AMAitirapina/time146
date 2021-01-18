#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

import logging
from typing import Dict
from os import getenv
import time
from utils import parse_json_from_file, format_input, answer_user

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

# Ativa logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Estados validos
CHOOSING_NAME, NEW_CHAT, KEEP_CHATING = range(3)

# Variaveis de ambiente
TOKEN = getenv("TOKEN")
BOT_NAME = getenv("BOT_NAME")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
PORT = getenv("PORT", default=8000)
ENV = getenv("ENV")

# Pegar os dados de conversacao
conversation_json = parse_json_from_file("conversation.json")

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f'Oi, eu sou o {BOT_NAME}, qual é o seu nome')

    return CHOOSING_NAME

def begin(update: Update, context: CallbackContext) -> int:
    if 'name' in context.user_data:
        name = context.user_data['name']
        update.message.reply_text(f'Oi {name}, bem vindo de volta, o que anda fazendo?',)
        return NEW_CHAT

    else:
        update.message.reply_text(f'Oi, eu sou o {BOT_NAME}, qual é o seu nome')
        return CHOOSING_NAME

def set_name(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    # Salvar o nome do usuario
    context.user_data['name'] = text
    update.message.reply_text(f'Legal {text}, do que voce gosta?')

    return NEW_CHAT

def new_chat(update: Update, context: CallbackContext) -> int:
    interest = format_input(update.message.text)
    if interest in conversation_json:
        for answer in conversation_json[interest]['respostas']:
            answer_user(update, answer)
            time.sleep(0.8)
        if 'conversa' in conversation_json[interest]:
            context.user_data['conversation_json'] = conversation_json[interest]['conversa']
            return KEEP_CHATING
    else:
        update.message.reply_text(f'Não ouvi falar sobre {interest}, me conta mais!')

    return NEW_CHAT

def keep_chating(update: Update, context: CallbackContext) -> int:
    interest = format_input(update.message.text)

    if interest in context.user_data['conversation_json']:
        for answer in context.user_data['conversation_json'][interest]['respostas']:
            answer_user(update, answer)
        if 'conversa' in context.user_data['conversation_json'][interest]:
            context.user_data['conversation_json'] = context.user_data['conversation_json'][interest]['conversa']
            return KEEP_CHATING
    else:
        update.message.reply_text(f'Não ouvi falar sobre {interest}, me conta mais! (K)')

    return NEW_CHAT

def fallback(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f"Não entendi o que voce quis dizer")
    if update.message.sticker:
        update.message.reply_text(update.message.sticker.file_id)
    return NEW_CHAT

def main() -> None:

    # Persitencia dos dados do usuario
    pp = PicklePersistence(filename='savedata')
    # Passar o token para o bot
    updater = Updater(TOKEN,persistence=pp, use_context=True)

    dispatcher = updater.dispatcher

    # Estados de conversacao
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.text, begin),
            MessageHandler(Filters.all, fallback),
        ],
        states={
            CHOOSING_NAME: [
                MessageHandler(Filters.text, set_name),
            ],
            NEW_CHAT: [
                MessageHandler(Filters.text, new_chat),
            ],
            KEEP_CHATING: [
                MessageHandler(Filters.text, keep_chating),
            ]
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
        },
        fallbacks=[MessageHandler(Filters.all, fallback)],
    )

    dispatcher.add_handler(conv_handler)

    # Iniciar o Bot
    if (ENV == 'production'):
        updater.start_webhook(listen="0.0.0.0",port=PORT,url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
    else:
        updater.start_polling()

    # O bot executa até que o processo seja terminado com Ctrl-C
    # ou receba um SIGINT, SIGTERM or SIGABRT.
    updater.idle()

# TODO: chamar o usuario (ser ativo)
# TODO: guardar os interesses do usuario
if __name__ == '__main__':
    main()
