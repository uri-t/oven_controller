from datetime import datetime
from controller import run_controller

def writer_fn(f):
    def write_temps(t, T):
        f.write('%d, %0.2f\n' % (t, T))
    return write_temps

def write_duty_cycle(on_frac):
    print("Setting duty cycle: %0.2f" % on_frac)


def controller_fn():

    dT_sum = 0
    def fn(dT):
        nonlocal dT_sum
        
        k_p = 0.02
        k_i = 0.001
        dT_sum += dT
        
        print("integral term: %0.2f" % dT_sum)
        return min(0.5, max(0, k_p*dT + k_i*dT_sum))

    return fn


f = open('results/%s.txt' % datetime.isoformat(datetime.now(), \
                                                   timespec='minutes'), 'a')


run_controller([0, 60, 120], [25, 180, 180], writer_fn(f), \
                                             write_duty_cycle,
                                             controller_fn())
