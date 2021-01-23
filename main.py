import telegram, logging, os, re, psutil, settings
import downloader, authentication

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

downloads = []
AllowedUser = Filters.user(username=[i.replace('\n', '') for i in open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r').readlines()])

def start(update, context):
    '''
    Starting message.
    '''
    update.message.reply_text("Welcome to Davidyz's Bot!")

def add_user(update, context):
    ''
    if authentication.validate(update.message.chat_id):
        # check for admin.
        AllowedUser.add_usernames([i.replace('@', '') for i in context.args])

        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r') as fin:
            allowed = set(fin.readlines())
        allowed |= set(context.args)
        
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'w') as fin:
            for i in allowed:
                if i[-1] != '\n':
                    fin.write(i.replace('@', '') + '\n')
                else:
                    fin.write(i.replace('@', ''))
        update.message.reply_text('Added.')
    else:
        update.message.reply_text('You are unauthorized to perform this action.')

def remove_user(update, context):
    ''
    if authentication.validate(update.message.chat_id):
        # check for admin.
        AllowedUser.remove_usernames([i.replace('@', '') for i in context.args])
        
        allowed = []
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r') as fin:
            allowed = [i.replace('\n', '') for i in fin.readlines()]
        
        for i in context.args:
            if i.replace('\n', '').replace('@', '') in allowed:
                allowed.remove(i.replace('\n', '').replace('@', ''))
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'w') as fin:
            for i in allowed:
                fin.write(i + '\n')
        update.message.reply_text('Removed.')
    else:
        update.message.reply_text('You are unauthorized to perform this action.')

def list_user(update, text):
    if authentication.validate(update.message.chat_id):
        # check for admin.
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r') as fin:
            users = tuple(i.replace('\n', '') for i in fin.readlines())

        update.message.reply_text('Allowed users:\n' + '\n'.join(['@' + i for i in users]))
    else:
        update.message.reply_text('You are not authorized to perform this action.')

def help_command(update, context):
    '''
    Help message.
    '''
    message = 'Current function:\n - Download videos from Youtube at max quality by sending the url of the video;\n - /list_downloading list all videos being downloaded.'
    update.message.reply_text(message)

def Action(update, context):
    '''
    Reply the same text as the user sent.
    '''
    global downloads
    message = update.message.text
    video_check = downloader.check_type(message)
    if video_check:
        update.message.reply_text("This is a {} video. Trying to download.".format(video_check[0].upper() + video_check[1:].lower()))
        dl = downloader.Downloader(update=update, context=context)
        if dl.download(message, site=video_check):
            downloads.append(dl)
        else:
            update.message.reply_text('This video source is not supported yet.')

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
        i.check_finished()
        if i.context[0].chat_data == context.chat_data:
            result += i.get_downloading()
    if result:
        update.message.reply_text('\n'.join(result))
    else:
        update.message.reply_text('No active jobs.')
    return result

def sys_info(update, context):
    '''
    To display the system information.
    '''
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    temperature = psutil.sensors_temperatures()
    update.message.reply_text('CPU utilization: {}%\nMemory utilization: {}%\nTemperature: {}°C'.format(cpu, mem, temperature))

def main():
    updater = Updater(settings.SECRETS, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command, filters=AllowedUser))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & AllowedUser, Action))
    dispatcher.add_handler(CommandHandler('list_downloading', get_downloading, filters=AllowedUser))
    dispatcher.add_handler(CommandHandler("sys_info", sys_info, filters=AllowedUser))
    dispatcher.add_handler(CommandHandler('add_user', add_user))
    dispatcher.add_handler(CommandHandler('remove_user', remove_user))
    dispatcher.add_handler(CommandHandler('list_user', list_user))

    dispatcher.job_queue.run_repeating(checkFinished, interval=10)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
