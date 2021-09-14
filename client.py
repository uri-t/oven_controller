from datetime import datetime

def writer_fn(f):
    def write_temps(t, T):
        f.write('%d, %0.2f\n' % (t, T))
    return write_temps

def write_duty_cycle(on_frac):
    print("Setting duty cycle: %0.2f" % on_frac)


def controller_fn():

    dT_sum = 0
    dT_prev = False
    t_prev = datetime.now()
    
    def fn(dT):
        nonlocal dT_sum
        nonlocal dT_prev
        nonlocal t_prev
        
        k_p = 0.03
        k_i = 0.005
        k_d = 0.2
        
        dT_prev = dT_prev or dT
        t_curr = datetime.now()
        dt = (t_curr - t_prev).seconds/60
        deriv = (dT - dT_prev)/dt

        dT_sum += dT*dt

        t_prev = t_curr
        dT_prev = dT
        
        print("integral term: %0.2f" % dT_sum)
        print("deriv: %0.2f" % deriv)
        return min(0.5, max(0, k_p*dT + k_i*dT_sum + k_d*deriv))

    return fn


#run_controller([0, 115, 125, 158, 188], \
#               [25, 370, 370, 470, 470], writer_fn(f), \
#                                             write_duty_cycle,
#                                             controller_fn())
