import youtube_dl, os, subprocess, psutil, re, biget, multiprocessing, settings

def check_type(url):
    y2b_Pattern = "https://(www\.)*youtu(\.)*be(\.com)*.*"
    bili_pattern = 'av.*|BV.*|(https://(www\.)*bilibili.com/video/((BV.*)|(av.*)))|(https://b23.tv/[^/]*)'
    bv = 'BV.*'
    if re.match(y2b_Pattern, url) != None:
        return 'youtube'
    if re.match(bv, url) != None:
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
        self.process_name = {}

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

            if site == 'youtube':
                title = youtube_dl.YoutubeDL(self.__ydl_opts).extract_info(url, download=False)['title']
                process = subprocess.Popen(args=['youtube-dl', '-f', int(not audioOnly) * 'bestvideo+' + 'bestaudio', url, '-o',self.__ydl_opts['outtmpl'], '--output',os.sep.join([path, title])])
                self.__inProgress[process.pid] = title
                self.process_name[process.pid] = psutil.Process(process.pid).name()
                return process.pid

            elif site == 'bilibili':
                # support bv only. working on URLs.
                video = biget.Video(bv=url)
                video.access()
                title = video.data['title']
                proc = multiprocessing.Process(target=biget.Video.download, args=(video, ), 
                                               kwargs={'pages': range(video.page_num),
                                                       'path': self.defaultPath,
                                                       'keep': False})
                proc.start()
                self.__inProgress[proc.pid] = title
                self.process_name[proc.pid] = psutil.Process(proc.pid).name()
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
                if psutil.Process(i).name() == self.process_name[i] and psutil.Process(i).status() != 'zombie':
                    pass
                else:
                    finished[i] = self.__inProgress.get(i)
            except psutil.NoSuchProcess:
                # process finished.
                finished[i] = self.__inProgress.get(i)

        for i in finished:
            self.__inProgress.pop(i)
            self.process_name.pop(i)
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

    def all_finished(self):
        return not bool(self.__inProgress)
    
    def get_pid(self):
        return self.__inProgress

    def get_downloading(self):
        return [self.__inProgress[i] for i in self.__inProgress]
