from __future__ import unicode_literals
import youtube_dl


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):   
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    # else:
    #     print(d['status'])



ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'outtmpl': './temp/%(title)s.%(ext)s'
}

def download(url):

    dl_error = None
    try:
        #youtube_dl.YoutubeDL( params={'-c': '', '--no-mtime': '', 'outtmpl': './%(uploader)s/%(title)s-%(upload_date)s-%(id)s.%(ext)s'} ).download([url])        
        #youtube_dl.YoutubeDL( params={'-c': '', '--no-mtime': '', 'outtmpl': './%(title)s-%(id)s.%(ext)s'} ).download([url])        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except youtube_dl.DownloadError as de:
         dl_error = de
    
    return dl_error
