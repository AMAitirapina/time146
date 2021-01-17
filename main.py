#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

import logging
from typing import Dict
from os import getenv

from utils import parse_json_from_file, format_input

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

conversation_map = {}

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

    if interest in conversation_map:
        for answer in conversation_map[interest].respostas:
            update.message.reply_text(answer)
        if 'conversa' in conversation_map[interest]:
            context.user_data[conversation_map] = conversation_map[interest].conversa
            return KEEP_CHATING
    else:
        update.message.reply_text(f'Não ouvi falar sobre {interest}, me conta mais!')

    return NEW_CHAT

def keep_chating(update: Update, context: CallbackContext) -> int:
    interest = format_input(update.message.text)

    if interest in context.user_data[conversation_map]:
        for answer in context.user_data[conversation_map].respostas:
            update.message.reply_text(answer)
        if 'conversa' in context.user_data[conversation_map]:
            context.user_data[conversation_map] = context.user_data[conversation_map].conversa
            return KEEP_CHATING
    else:
        update.message.reply_text(f'Não ouvi falar sobre {interest}, me conta mais!')

    return NEW_CHAT

def fallback(update: Update, context: CallbackContext) -> int:
    print(update)
    update.message.reply_text(f"Não entendi o que voce quis dizer")
    return NEW_CHAT

def main() -> None:

    # Pegar os dados de conversacao
    conversation_map = parse_json_from_file("conversation.json")

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
            NEW_CHAT: [
                MessageHandler(Filters.text, new_chat),
            ],
            KEEP_CHATING: [
                MessageHandler(Filters.text, new_chat),
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
    updater.start_polling()

    # O bot executa até que o processo seja terminado com Ctrl-C
    # ou receba um SIGINT, SIGTERM or SIGABRT.
    updater.idle()

# TODO: chamar o usuario (ser ativo)
# TODO: melhorar o fluxo de conversa
# TODO: guardar os interesses do usuario
if __name__ == '__main__':
    main()
