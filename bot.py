#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
from pprint import pprint

import yaml
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from config import *
from wienerLinien import WienerLinien
from save import PersistentData

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

wl = WienerLinien("stationen/cache/current.json")
save = PersistentData()

SELECT, TEST = range(2)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hallo!')
    save.user(update.message.chat_id)


def help_message(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hilfetext')


def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def image(bot, update):
    bot.sendMessage(update.message.chat_id, text="Bild")


def getstations(bot, update, args):
    if not args:
        bot.sendMessage(update.message.chat_id, text="Verwendung:\n/add [Stationenname]")
        return ConversationHandler.END
    userinput = " ".join(args)
    print(userinput)
    choice = wl.fuzzy_stationname(userinput)

    save.save_choice(update.message.chat_id, choice)
    pprint(choice)
    message = "Es wurden mehrere Stationen gefunden.\nBitte gib die Nummer der gewünschten Station an:\n"
    prev_percentage = choice[0][1]
    i = 1
    keyboard = []
    for name, percentage, stationId in choice:
        if prev_percentage - percentage >= 10 or percentage <= 50:
            break
        message += str(i) + ": " + name + "\n"
        keyboard.append([InlineKeyboardButton(name, callback_data=str(i))])
        i += 1
        prev_percentage = percentage
    print(message)
    if message and i > 2:
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(update.message.chat_id, text=message, reply_markup=reply_markup)
    elif i == 2:
        bot.sendMessage(update.message.chat_id, text=message)
        return ConversationHandler.END
    else:
        bot.sendMessage(update.message.chat_id, text="Keine Station gefunden")
        return ConversationHandler.END
    return SELECT


def select(bot, update):
    query = update.callback_query
    if query.data.isdigit():
        selected_station = save.get_choice(query.message.chat_id)[int(query.data) - 1]
        pprint(selected_station)
        save.add_station(query.message.chat_id, {"name": selected_station[0], "id": selected_station[2]})
        bot.editMessageText(text="Station '{station}' hinzugefügt".format(station=selected_station[0]),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        return ConversationHandler.END

    else:
        bot.sendMessage(update.message.chat_id, text="Ungültige Eingabe")
        return SELECT


def cancel(bot, update):
    bot.sendMessage(update.message.chat_id, text="Aktion abgebrochen")
    save.delete_choice(update.message.chat_id)
    return ConversationHandler.END


def list_stations(bot, update):
    stations = save.get_stations(update.message.chat_id)
    if stations:
        message = ""
        for station in stations:
            message += station["name"] + "\n"
        bot.sendMessage(update.message.chat_id, text=message)
    else:
        bot.sendMessage(update.message.chat_id,
                        text="Du hast noch keine Stationen hinzugefügt\n"
                             "mit /add kannst du eine neue Station hinzufügen")


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_message))
    # dp.add_handler(CommandHandler("station", getstations))
    dp.add_handler(CommandHandler("list", list_stations))
    updater.dispatcher.add_handler(CallbackQueryHandler(select))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', getstations, pass_args=True)],

        states={
            #
            #     PHOTO: [MessageHandler([Filters.photo], photo),
            #             CommandHandler('skip', skip_photo)],
            #
            #     LOCATION: [MessageHandler([Filters.location], location),
            #                CommandHandler('skip', skip_location)],

            SELECT: [MessageHandler([Filters.text], select)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], echo))
    dp.add_handler(MessageHandler([Filters.photo], image))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    print("------------------------------------------------------------------------")  #
    save.export()


if __name__ == '__main__':
    main()
