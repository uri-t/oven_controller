import serial
import time
import threading
from datetime import datetime

ser = serial.Serial('/dev/ttyACM0', timeout=7)

f = open('results/%s.txt' % datetime.isoformat(datetime.now(), timespec='minutes'), 'a')

time.sleep(0.3)
ser.reset_input_buffer()

def diff(x):
    diff_x = [0]*(len(x)-1)
    
    for i in range(len(x)-1):
        diff_x[i] = x[i+1] - x[i]

    return diff_x

def mean(x):
    return sum(x)/len(x)

measure_time = 10

while True:
    ser.write(bytes("1.0\n", 'utf-8'))
    ser.flush()

    x = threading.Thread(target=time.sleep, args=(measure_time,))
    x.start()
    
    times = []
    temps = []
    
    while x.is_alive():
        data = ser.readline().decode('utf-8').strip().split(",")
        times.append(int(data[0]))
        temps.append(float(data[1]))        
        f.write('%s, %s\n' % tuple(data))

    dts = diff(times)
    dtemps = diff(temps)
    dTdts = [x[1]/x[0] for x in zip(dts, dtemps)]
    
    print("T = %0.2f, dT = %0.2f" % (mean(temps), 1000*mean(dTdts)))
