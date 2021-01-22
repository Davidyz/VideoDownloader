import youtube_dl

__ydl_opts = {
        'format': 'bestvideo+bestaudio',
        'prefer_ffmpeg': True,
        'ignoreerrors': True,
        'outtmpl': '/mnt/wd_blue/Videos/Youtube_dl/%(title)s.%(ext)s',
        'ffmpeg_location': '/usr/local/bin/ffmpeg'
        }

def Download(url):
    if isinstance(url, str):
        url = [url]
    __ydl = youtube_dl.YoutubeDL(__ydl_opts)
    __ydl.download(url)
