#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

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

# Ativa logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Estados validos
CHOOSING_NAME, INTERESTS = range(2)

# Variaveis de ambiente
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
    # Salvar o nome do usuario
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

def fallback(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f"Não entendi o que voce quis dizer")
    return INTERESTS

def main() -> None:

    # Ler o arquivo de conversacao
    conversation_file = open("conversation", "r")
    conversation_lines = conversation_file.read().split('\n')

    # Processar os dados de conversacao
    for i in range(0, len(conversation_lines), 2):
        conversation_map[conversation_lines[i]] = conversation_lines[i+1]

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
        },
        fallbacks=[MessageHandler(Filters.text, fallback)],
    )

    dispatcher.add_handler(conv_handler)

    # Iniciar o Bot
    updater.start_polling()

    # O bot executa até que o processo seja terminado com Ctrl-C
    # ou receba um SIGINT, SIGTERM or SIGABRT.
    updater.idle()

# TODO: chamar o usuario (ser ativo)
# TODO: melhorar o fluxo de conversa
# TODO: guardar os interesses do usuario
if __name__ == '__main__':
    main()
