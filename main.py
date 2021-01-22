import telegram, logging, os, re

if os.path.isdir('/mnt/wd_blue/git/MyBot'):
    os.chdir('/mnt/wd_blue/git/MyBot')
import downloader

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

downloads = []

def start(update, context):
    '''
    Starting message.
    '''
    update.message.reply_text("Welcome to Davidyz's Bot!")

def help_command(update, context):
    '''
    Help message.
    '''
    message = 'Current function:\n \- *Download videos* from Youtube at max quality by sending the url of the video;\n \- /list_downloading list all videos being downloaded.'
    update.message.reply_text(message, parse_mode='MarkdownV2')

def Action(update, context):
    '''
    Reply the same text as the user sent.
    '''
    global downloads
    message = update.message.text
    if isVideoUrl(message):
        update.message.reply_text("This is a youtube video. Trying to download.")
        dl = downloader.Downloader(update=update, context=context)
        dl.download(message)
        downloads.append(dl)
    else:
        update.message.reply_text(update.message.text)

def isVideoUrl(url):
    WebPattern = "https://(www\.)*youtu(\.)*be(\.com)*.*"
    return re.match(WebPattern, url) != None

def checkFinished(context):
    global downloads
    finished = []
    empty_job = []
    for i in downloads:
        result = i.check_finished()
        if result:
            finished.append(i)

    for job in finished:
        finished_downloads = job.finished
        for i in finished_downloads:
            job.update.message.reply_text(text="<{}> downloaded.".format(finished_downloads[i]))
        if job.all_finished():
            empty_job.append(job)

    while empty_job:
        job = empty_job.pop(0)
        downloads.remove(job)
        del job

def get_downloading(update, context):
    '''
    To display the videos being downloaded.
    '''
    global downloads
    result = []
    for i in downloads:
        if i.context[0].chat_data == context.chat_data:
            result += i.get_downloading()
    if result:
        update.message.reply_text('\n'.join(result))
    else:
        update.message.reply_text('No active jobs.')
    return result

def main():
    updater = Updater("1593220412:AAGHOel6vvRY__QkfuX6wjy_GAspblBKBR8", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, Action))
    dispatcher.add_handler(CommandHandler('list_downloading', get_downloading))
    dispatcher.job_queue.run_repeating(checkFinished, interval=10)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
