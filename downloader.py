import youtube_dl, os, subprocess, psutil

class Downloader:
    def __init__(self, defaultPath='/mnt/wd_blue/Videos/Youtube_dl/'):
        self.__ydl_opts = {
                'format': 'bestvideo+bestaudio',
                'prefer_ffmpeg': True,
                'ignoreerrors': True,
                'outtmpl': '/mnt/wd_blue/Videos/Youtube_dl/%(title)s.%(ext)s',
                'ffmpeg_location': '/usr/local/bin/ffmpeg'
                }
        self.__inProgress = {}
        self.defaultPath = path

    def download(self, url, path=None, audioOnly=False):
        '''
        Start a download.
        '''
        if path == None:
            path = self.defaultPath

        if isinstance(url, str):
            process = subprocess.Popen(args=['Youtube-dl', '-f', int(not audioOnly) * 'bestvideo+' + 'bestaudio', url, '-o', __ydl_opts['outtmpl'], '--output', path])
            self.__inProgress[process.pid] = youtube_dl.YoutubeDL(self.__ydl_opts).extract_info(url, download=False)
        
        elif isinstance(url, (list, tuple)):
            for i in url:
                DownloadAltern(i)[0]

    def check_finished(self):
        '''
        Return a dict of pid:videoTitle.
        '''
        finished = {}
        for i in self.__inProgress:
            try:
                # the process id still exists. either incomplete or different process with same pid.
                if psutil.Process(i).name() == 'youtube-dl':
                    pass
                else:
                    finished[i] = self.__inProgress.pop(i)
            except psutil.NoSuchProcess:
                # process finished.
                finished[i] = self.__inProgress.pop(i)
        return finished
