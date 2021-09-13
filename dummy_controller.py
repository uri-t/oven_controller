from queue import Queue
import time
from datetime import datetime

class Controller:
    def __init__(self):
        self.stopped = False
        
    def terminate(self):
        self.stopped = True
        
    def run_controller(self, times, set_points, \
                       read_callback=None, \
                       write_callback=None, \
                       controller_fn=None,
                       temp_queue = None):
        t = 0
        T = 0
        t_start = datetime.now()
        
        while True:
            if self.stopped:
                print("controller: stopping")
                break
            
            t += int((datetime.now() - t_start).total_seconds()*1000)
            print("controller: putting %s in queue" % str((t, T)))
            temp_queue.put((t, T))
            T = T+1
            time.sleep(2)
            
