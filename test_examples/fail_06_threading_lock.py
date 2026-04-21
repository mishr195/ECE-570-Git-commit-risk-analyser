import threading
lock = threading.Lock()
def danger(self):
    lock.acquire()
    # TODO: might deadlock
