from __future__ import unicode_literals
import youtube_dl

def ydl (args):
    ydl_opts = {}
    if not args['music']:
        ydl_opts = {
            'outtmpl': args['folder'] + '/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio',
            # 'postprocessors': [{
            #     'key': 'FFmpegVideoConvertor',
            #     'preferedformat': 'mkv'
            # }]
        }
    else:
        ydl_opts = {
            'outtmpl': args['folder']+'/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'vorbis',
                'preferredquality': '192',
            }],
        }
    attempt = 0
    success = False
    while (attempt < 5 and success == False):
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([args['url']])
            success = True
        except:
            print ("Error occured while downloading video: " + args['url'] + " attempt: " + str(attempt))
            attempt = attempt + 1