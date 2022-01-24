import youtube_dl, os, subprocess, psutil, re, biget, multiprocessing, settings, requests
from typing import List

def check_type(url):
    y2b_Pattern = "https://(www\.)*youtu(\.)*be(\.com)*.*"
    bili_pattern = 'av.*|BV.*|(https://(www\.)*bilibili.com/video/((BV.*)|(av.*)))|(https://b23.tv/[^/]*)'
    bv = 'BV.*'
    if re.match(y2b_Pattern, url) != None:
        return 'youtube'
    if re.match(bili_pattern, url) != None:
        return 'bilibili'
    return False

def recurse_list(path):
    stack = [path]
    complete = False
    while not complete:
        complete = True
        new = []
        removed = []
        for i in stack:
            if os.path.isdir(i):
                removed.append(i)
                complete = False
                for j in os.listdir(i):
                    new.append(os.sep.join([i, j]))
        
        for i in removed:
            stack.remove(i)

        stack += new
    return stack

def get_bv(url):
    if 'bilibili.com' in url:
        return url.split('/')[-1]
    elif url[:2] == 'BV' and len(url) == 12:
        return url
    text = requests.get(url).text.strip()
    for i in range(len(text)):
        if text[i:i + 2] == 'BV':
            return text[i:i + 12]

class Downloader:
    def __init__(self, update, context, defaultPath=settings.DEFAULT_PATH):
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
        self.supported_site = ('youtube', 'bilibili')
        self.downloading = {}
        self.transcoding = []

    def download(self, url, path=None, audioOnly=False, site=None):
        '''
        Start a download.
        '''

        if path == None:
            path = self.defaultPath

        if isinstance(url, str):
            if not (site in self.supported_site):
                site = check_type(url)
                if not site:
                    return False
            
            title = str()
            if site == 'youtube':
                try:
                    title = youtube_dl.YoutubeDL(self.__ydl_opts).extract_info(url, download=False)['title']
                except youtube_dl.DownloadError as d:
                    return False
                command: List[str] = ['yt-dlp', '-f', int(not audioOnly) * 'bestvideo+' + 'bestaudio', url, '-o',self.__ydl_opts['outtmpl']]
                if settings.PROXY != '' and settings.PROXY.split("://")[0] in ('http', 'socks5'):
                    # passes socks5 or http proxy to the command line.
                    command.insert(1, '--proxy')
                    command.insert(2, settings.PROXY)

                process = subprocess.Popen(args=command)
                self.__inProgress[process.pid] = title
                self.downloading[process.pid] = psutil.Process(process.pid).name()
                return process.pid

            elif site == 'bilibili':
                # support bv only. working on URLs.
                video = biget.Video(bv=get_bv(url))
                video.access()
                title = video.data['title']
                proc = multiprocessing.Process(target=biget.Video.download, args=(video, ), 
                                               kwargs={'pages': range(video.page_num),
                                                       'path': self.defaultPath,
                                                       'keep': False})
                proc.start()
                self.__inProgress[proc.pid] = title
                self.downloading[proc.pid] = psutil.Process(proc.pid).name()
                return proc.pid

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
                if psutil.Process(i).name() == self.downloading[i] and psutil.Process(i).status() != 'zombie':
                    pass
                else:
                    finished[i] = self.__inProgress.get(i)
            except psutil.NoSuchProcess:
                # process finished.
                finished[i] = self.__inProgress.get(i)

        for i in self.transcoding:
            try:
                if psutil.Process(i).name() == 'ffmpeg' and psutil.Process(i).status() != 'zombie':
                    pass
                else:
                    finished[i] = self.transcoding.get(i)
            except psutil.NoSuchProcess:
                finished[i] = self.transcoding.get(i)

        for i in finished:
            self.__inProgress.pop(i)
            self.downloading.pop(i)
            self.transcoding.pop(i)
            if os.path.isdir(os.sep.join([self.defaultPath, finished[i]])):
                root = os.sep.join([self.defaultPath, finished[i]])
                files = recurse_list(root)
                for j in files:
                    os.system('mv "{}" "{}"'.format(j, root))
                for j in os.listdir(root):
                    if os.path.isdir(os.sep.join([root, j])):
                        os.system('rm -r "{}"'.format(os.sep.join([root, j])))
                
        self.finished.update(finished)

        return finished

    def transcode(self, path, title=None):
        if os.path.isdir(path):
            files = recurse_list(path)
        elif os.path.isfile(path):
            files = [path]

        for i in files:
            original_format = i.split('.')[-1]
            new_filename = i.replace(original_format, '.h265.' + original_format)
            command = 'ffmpeg -v 0 -i "{source}" -c:v libx265 -c:a copy -q 0 -y "{target}"'.format(source=i, target=new_filename)
            process = subprocess.Popen(command.split(' '))
            self.transcoding[process.pid] = title

    def all_finished(self):
        return not bool(self.__inProgress)
    
    def get_pid(self):
        return self.__inProgress

    def get_downloading(self):
        return [self.__inProgress[i] for i in self.__inProgress]
