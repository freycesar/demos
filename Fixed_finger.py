'''
Author: SUN Qingyu sunqingyu1997@gmail.com
Date: 2023-05-25 15:05:46
LastEditors: SUN Qingyu sunqingyu1997@gmail.com
LastEditTime: 2023-05-25 16:21:47
FilePath: \demos\Fixed_finger.py
'''
from pyautd3.link import SOEM, Simulator, OnLostFunc
from pyautd3.gain import Focus
from pyautd3 import Controller, Geometry, SilencerConfig, Clear, Synchronize, Stop, DEVICE_WIDTH, DEVICE_HEIGHT
from pyautd3.modulation import Static, Sine
import numpy as np
import math
import time
from pyautd3.stm import GainSTM
import ctypes
import platform
import os

# use cpp to get high precision sleep time
dll = ctypes.cdll.LoadLibrary
libc = dll(os.path.dirname(__file__) + '/cpp/' + platform.system().lower() + '/HighPrecisionTimer.so') 

W = 640
H = 480

def on_lost(msg: ctypes.c_char_p):
        print(msg.decode('utf-8'), end="")
        os._exit(-1)

def stm_gain(autd: Controller):
    config = SilencerConfig.none()
    autd.send(config)
    m = Static(1.0)
    stm = GainSTM()
    radius = 1.0
    # radius_velocity = r_v
    size = 50
    n_updatecircle = 1.
    stm.frequency = 5.
    # time_step = (n_updatecircle * 1.) / stm.frequency
    time_step = 0.2
    # step = 0.2
    # size = 50 * 2 * np.pi * radius // step
    center = autd.geometry.center + np.array([0., 0., 150.])

    for circle_number in range(50):
        for i in range(size):
            # theta = step / radius
            theta = 2 * np.pi * i / size
            p = radius * np.array([np.cos(theta), np.sin(theta), 0])
            f = Focus(center + p)
            stm.add(f)
        libc.HighPrecisionSleep(ctypes.c_float(time_step))
        # time.sleep(time_step)
        radius += 0.1
       # radius += r_v * 0.01

def run(autd: Controller):
    autd.send(Clear())
    autd.send(Synchronize())

    print('================================== Firmware information ====================================')
    firm_info_list = autd.firmware_info_list()
    for firm in firm_info_list:
        print(firm)
    print('============================================================================================')

    r_list = np.arange(5, 30.0, 0.5)
    stm_gain(autd)
    _ = input()
    print('finish.')
    autd.send(Stop())
    autd.dispose()


if __name__ == '__main__':

    W_cos = math.cos(math.pi/12) * DEVICE_WIDTH
    geometry = Geometry.Builder()\
            .add_device([W_cos - (DEVICE_WIDTH - W_cos), DEVICE_HEIGHT - 10 + 12.5, 0.], [math.pi, math.pi/12, 0.])\
            .add_device([W_cos - (DEVICE_WIDTH - W_cos), -10 - 12.5, 0.], [math.pi, math.pi/12, 0.])\
            .add_device([-W_cos + (DEVICE_WIDTH - W_cos),  12.5, 0.], [0., math.pi/12, 0.])\
            .add_device([-W_cos + (DEVICE_WIDTH - W_cos), -DEVICE_HEIGHT - 12.5, 0.], [0., math.pi/12, 0.])\
            .build()
    
    # on_lost_func = OnLostFunc(on_lost)
    link = Simulator().build()
    # link = SOEM().on_lost(on_lost_func).build()    
    autd = Controller.open(geometry, link)
    # if_use_simulator = input('If use simulator? [y: simulator] or [n: AUTD]: ')

    autd.check_trials = 50

    run(autd)