import telegram, logging, os, re

if os.path.isdir('/mnt/wd_blue/git/MyBot'):
    os.chdir('/mnt/wd_blue/git/MyBot')
import downloader

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
    message = 'Current function:\n - Download videos from Youtube at max quality.'
    update.message.reply_text(message)

def Action(update, context):
    '''
    Reply the same text as the user sent.
    '''
    message = update.message.text
    if isVideoUrl(message):
        update.message.reply_text("This is a youtube video. Trying to download.")
        downloader.Download(message)
    else:
        update.message.reply_text(update.message.text)

def isVideoUrl(url):
    WebPattern = "https://(www\.)*youtu(\.)*be(\.com)*.*"
    return re.match(WebPattern, url) != None

def main():
    updater = Updater("1593220412:AAGHOel6vvRY__QkfuX6wjy_GAspblBKBR8", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, Action))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
