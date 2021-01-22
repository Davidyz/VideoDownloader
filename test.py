import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def start(update, context):
    '''
    Starting message.
    '''
    update.message.reply_text("Welcome to Davidyz's Bot!")

def help_command(update, context):
    '''
    Help message.
    '''
    update.message.reply_text("Help text")

def echo(update, context):
    '''
    Reply the same text as the user sent.
    '''
    update.message.reply_text(update.message.text)

def main():
    updater = Updater("1593220412:AAGHOel6vvRY__QkfuX6wjy_GAspblBKBR8", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
