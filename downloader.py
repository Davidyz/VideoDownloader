import youdube_dl

__ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'aac',
            'preferredquality': '320'
            }],
        'prefer_ffmpeg': True,
        'outtmpl': '/mnt/wd_blue/Videos/Youtube_dl/%(title)s.%(ext)s'
        }

__ydl = youdube_dl.YoutubeDL(ydl_opts)

def Download(url):
    if isinstance(url, str):
        url = [url]
    __ydl.download(url)
