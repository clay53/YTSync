import time

import threading
from queue import Queue

import ytda
from ydl import ydl

q = Queue()

def threader(job, args):
    while True:
        # gets an worker from the queue
        q.get()

        # Run the example job with the avail worker in queue (thread)
        if (args != None):
            job(args)
        else:
            job()
        
        # completed with the job
        q.task_done()

def sync (args):
    syncedTracks = catchup(args['playlist_name'], args['playlist_id'], args['music'], args['workers'])
    print(syncedTracks)
    with open('playlists/' + args['playlist_name'] + "/sync.data", "w") as f:
        f.write(','.join(syncedTracks))
    while True:
        attempt = 0
        success=False
        response=None
        while success==False and attempt < 5:
            try:
                print(args['playlist_name'] + " tick attempt " + str(attempt))
                response = ytda.playlist_items_list_by_playlist_id(ytda.client,
                    part='contentDetails',
                    maxResults=args['update_length'],
                    playlistId=args['playlist_id']
                )
            except:
                print("Sync failed to get response " + args['playlist_name'] + " attempt: " + str(attempt))
                attempt+=1
                time.sleep(1)
            else:
                success=True
        for track in response.get('items'):
            id = track.get('contentDetails').get('videoId')
            with open('playlists/' + args['playlist_name'] + "/sync.data", "r+") as f:
                if id not in f.read():
                    print(id)
                    ydl({
                        'folder': 'playlists/' + args['playlist_name'],
                        'url': 'https://www.youtube.com/watch?v=' + id,
                        'music': args['music']
                    })
                    f.write(',' + id)
        time.sleep(args['update_freq'])
    
    print ("Unexpected end of thread with playlist_id of: " + args['playlist_id'] + " hanging...")


def catchup (playlist_name, playlist_id, music, workers):
    print(playlist_id + " is catching up...")
    results = []
    pageToken = None
    working = True
    workersn = 0
    while working:
        print(playlist_id)
        attempt = 0
        success=False
        response=None
        while success==False and attempt < 5:
            try:
                response = ytda.playlist_items_list_by_playlist_id(ytda.client,
                    part='contentDetails',
                    maxResults=50,
                    pageToken=pageToken,
                    playlistId=playlist_id
                )
            except:
                print("Catchup failed to get response " + playlist_name + " attempt: " + str(attempt))
                attempt+=1
                time.sleep(1)
            else:
                success=True
        if 'nextPageToken' in response:
            pageToken = response.get('nextPageToken')
        else:
            working = False
        for track in response.get('items'):
            id = track.get('contentDetails').get('videoId')
            try:
                with open('playlists/' + playlist_name + '/sync.data', 'r') as f:
                    if id not in f.read():
                        t = threading.Thread(target=threader, args=(ydl, {
                            'folder': 'playlists/' + playlist_name,
                            'url': 'https://www.youtube.com/watch?v=' + id,
                            'music': music
                        }))
                        t.daemon = False
                        t.start()
                        q.put(workersn)
                        workersn += 1
                        print(workersn)
                        print(workers)
                        if (not (workersn < workers or workers == 0)):
                            print(playlist_name + ".catchup is waiting for q...")
                            q.join()
                            workersn = 0
            except:
                t = threading.Thread(target=threader, args=(ydl, {
                    'folder': 'playlists/' + playlist_name,
                    'url': 'https://www.youtube.com/watch?v=' + id,
                    'music': music
                }))
                t.daemon = False
                t.start()
                q.put(workersn)
                workersn += 1
                print(workersn)
                print(workers)
                if (not (workersn < workers or workers == 0)):
                    print(playlist_name + ".catchup is waiting for q...")
                    q.join()
                    workersn = 0
            results.append(id)
    if workersn > 0:
        print(playlist_name + ".catchup is waiting for q...")
        q.join()
    return results