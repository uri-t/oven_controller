from queue import Queue
import serial
import time
import threading
from datetime import datetime
import glob

# takes in an array of times (in minutes) and setpoints (in deg. C)
# and writes the appropriate duty cycle to follow this heating trajectory.

# The read_callback function is called on every temperature read in from the
# Arduino and takes two arguments: the board time (in millis), and current
# temperature (in deg. C).

# The write_callback function is called when a duty cycle is sent to the Arduino
# It takes one argument: the new duty cycle

# The controller function takes in the difference between the current setpoint
# and temperature and outputs a duty cycle

class Controller:
    def __init__(self):
        self.stopped = False

    def terminate(self):
        self.stopped = True

    def run_controller(self, times, set_points, \
                       read_callback=None, \
                       write_callback=None, \
                       controller_fn=None,
                       temp_queue = None,
                       stopped = False):

        # log program
        f = open('programs/%s.txt' % datetime.isoformat(datetime.now(), \
                                                   timespec='minutes'), 'w')

        for i in range(len(times)):
            f.write("%0.2f, %0.2f\n" % (times[i], set_points[i]))
            
        f.close()

    
        ser = self.serial_connection()
    
        t_start = datetime.now()
        t_prev = times[0]
        sp_prev = set_points[0]

        time.sleep(1)
        ser.reset_input_buffer()
        
        measure_time = 10
        
        controller_fn = controller_fn or self.default_controller
        
        while True:
            if self.stopped:
                print("stopping controller")
                ser.write(bytes("0.0\n", 'utf-8'))
                break
            
            if len(times) == 0:
                ser.write(bytes("0.0\n", 'utf-8'))
                return

            t_curr = (datetime.now() - t_start).seconds/60
        
            while t_curr > times[0]:
                t_prev = times.pop(0)
                sp_prev = set_points.pop(0)
                if len(times) == 0:
                    ser.write(bytes("0.0\n", 'utf-8'))
                    return


            a = (t_curr - t_prev)/(times[0] - t_prev)
            sp_curr = (1-a)*sp_prev + a*set_points[0]
            
            print("the current time is %0.1f mins;  current setpoint is %0.1f C" \
                  % (t_curr, sp_curr))
            
            x = threading.Thread(target=time.sleep, args=(measure_time,))
            x.start()
            
            temps = []

            while x.is_alive():
                try:
                    curr_line = ser.readline().decode('utf-8')
                    data = curr_line.strip().split(",")
                    t = int(data[0])
                    T = float(data[1])
                    temps.append(T)
                    if read_callback:
                        read_callback(t, T)

                    if temp_queue:
                        temp_queue.put((t, T))

                except serial.serialutil.SerialException as e:
                    ser = self.serial_connection(ser)
                    ser.write(0)
                    print("========================")
                    print("caught error")
                    print(e)
                    print("========================")

                except ValueError as e:
                    print(data)
                    print(curr_line)
                    ser.reset_input_buffer()
                    print("========================")
                    print("value error, retrying")
                    print(e)
                    print("========================")
                

            try:
                on_frac = controller_fn(sp_curr - sum(temps)/len(temps))

            except:
                print("========================")
                print("measurement failed, defaulting to duty cycle of 0")
                print("========================")
                on_frac = 0
                
            if write_callback:
                write_callback(on_frac)
                
            ser.write(bytes("%0.1f\n" % on_frac, 'utf-8'))
            ser.flush()
        
    def default_controller(self, dT):
        k = 0.02
        return min(0.5, max(0, k*dT))
        

    def serial_connection(self, ser = None):

        if ser:
            ser.close()
            
        fnames = []
        
        while len(fnames) == 0:
            time.sleep(1)
            fnames = glob.glob('/dev/ttyACM*')
            print("device names: %s " % fnames)
            
        return serial.Serial(fnames[0], timeout=7)
