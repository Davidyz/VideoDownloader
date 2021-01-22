import youtube_dl, os, subprocess, psutil

class Downloader:
    def __init__(self, update, context, defaultPath='/mnt/wd_blue/Videos/Youtube_dl/'):
        self.__ydl_opts = {
                'format': 'bestvideo+bestaudio',
                'prefer_ffmpeg': True,
                'ignoreerrors': True,
                'outtmpl': '/mnt/wd_blue/Videos/Youtube_dl/%(title)s.%(ext)s',
                'ffmpeg_location': '/usr/local/bin/ffmpeg'
                }
        self.__inProgress = {}
        self.defaultPath = defaultPath
        self.context = context,
        self.update = update
        self.finished = {}

    def download(self, url, path=None, audioOnly=False):
        '''
        Start a download.
        '''
        if path == None:
            path = self.defaultPath

        if isinstance(url, str):
            title = youtube_dl.YoutubeDL(self.__ydl_opts).extract_info(url, download=False)['title']
            process = subprocess.Popen(args=['youtube-dl', '-f', int(not audioOnly) * 'bestvideo+' + 'bestaudio', url, '-o',self.__ydl_opts['outtmpl'], '--output',os.sep.join([path, title])])
            self.__inProgress[process.pid] = title
        
        elif isinstance(url, (list, tuple)):
            for i in url:
                self.download(i[0], path, audioOnly)

    def check_finished(self):
        '''
        Return a dict of pid:videoTitle.
        '''
        finished = {}
        for i in self.__inProgress:
            try:
                # the process id still exists. either incomplete or different process with same pid.
                if psutil.Process(i).name() == 'youtube-dl' and psutil.Process(i).status() != 'zombie':
                    pass
                else:
                    finished[i] = self.__inProgress.get(i)
            except psutil.NoSuchProcess:
                # process finished.
                finished[i] = self.__inProgress.get(i)
        
        for i in finished:
            self.__inProgress.pop(i)
        
        self.finished.update(finished)

        return finished

    def all_finished(self):
        return not bool(self.__inProgress)

    def get_downloading(self):
        return [self.__inProgress[i] for i in self.__inProgress]
