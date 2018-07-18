import playlist
import threading
from queue import Queue


# Create the queue and threader 
q = Queue()

# The threader thread pulls an worker from the queue and processes it
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

t = threading.Thread(target=threader, args=(playlist.sync, {
    'playlist_name': 'ClaytonMusic',
    'playlist_id': 'PLaHvpZQLFcTphP6szbVI9ig2fH8vn5f91',
    'update_length': 5,
    'update_freq': 5,
    'workers': 61
}))
t.daemon = False
t.start()

s = threading.Thread(target=threader, args=(playlist.sync, {
    'playlist_name': 'Duuuuh',
    'playlist_id': 'PLaHvpZQLFcTphP6szbVI9ig2fH8vn5f91',
    'update_length': 5,
    'update_freq': 5
}))
s.daemon = False
s.start()

for worker in range(2):
    q.put(worker)

print("Thread1")
q.join()