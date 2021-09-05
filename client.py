from datetime import datetime
from controller import run_controller

def writer_fn(f):
    def write_temps(t, T):
        f.write('%d, %0.2f\n' % (t, T))
    return write_temps

def write_duty_cycle(on_frac):
    print("Setting duty cycle: %0.2f" % on_frac)


f = open('results/%s.txt' % datetime.isoformat(datetime.now(), \
                                                   timespec='minutes'), 'a')


run_controller([0, 60, 120], [25, 180, 180], writer_fn(f), write_duty_cycle)
