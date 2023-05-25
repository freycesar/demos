'''
Author: SUN Qingyu sunqingyu1997@gmail.com
Date: 2023-05-25 15:05:46
LastEditors: SUN Qingyu sunqingyu1997@gmail.com
LastEditTime: 2023-05-25 16:20:31
FilePath: \demos\Fixed_finger.py
'''
from pyautd3.link import SOEM
from pyautd3.link import Simulator
from pyautd3.gain import Focus
from pyautd3 import Controller, SilencerConfig, Clear, Synchronize, Stop, DEVICE_WIDTH, DEVICE_HEIGHT
from pyautd3.modulation import Static, Sine
import numpy as np
import time
import ctypes
import platform
import os
import math
from multiprocessing import Process, Pipe
import time

# use cpp to get high precision sleep time
dll = ctypes.cdll.LoadLibrary
libc = dll(os.path.dirname(__file__) + '/../cpp/' + platform.system().lower() + '/HighPrecisionTimer.so') 

W = 640
H = 480

def stm_gain(autd: Controller):
    config = SilencerConfig.none()
    autd.send(config)
    m = Static(1)
    stm = GainSTM(autd)
    radius = 1.0
    # radius_velocity = r_v
    stm.frequency = 5
    size = 200
    n_updatecircle = 1
    # step = 0.2
    # size = 50 * 2 * np.pi * radius // step
    center = autd.geometry.center + np.array([0., 0., 150.])
    for radius in range(6):
        for i in range(size):
            # theta = step / radius
            theta = 2 * np.pi * i / size
            p = radius * np.array([np.cos(theta), np.sin(theta), 0])
            f = Focus(center + p)
            stm.add(f)
        autd.send(m,stm)
        time.sleep(n_updatecircle * 1 / stm.frequency)
        radius += 0.01
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
    autd = Controller()

 # Multiple AUTD
    # The arrangement of the AUTDs:
    # 1 → 2
    #     ↓
    # 4 ← 3
    # (See from the upside)
    autd.geometry.add_device([-DEVICE_WIDTH / 2, DEVICE_HEIGHT / 2, 0.], [0., 0., 0.])
    autd.geometry.add_device([DEVICE_WIDTH / 2, DEVICE_HEIGHT / 2, 0.], [0., 0., 0.])
    autd.geometry.add_device([DEVICE_WIDTH / 2, -DEVICE_HEIGHT / 2, 0.], [0., 0., 0.])
    autd.geometry.add_device([-DEVICE_WIDTH / 2, -DEVICE_HEIGHT / 2, 0.], [0., 0., 0.])

    if_use_simulator = input('If use simulator? [y: simulator] or [n: AUTD]: ')


    link = SOEM().high_precision(True).build()

    if not autd.open(link):
        print('Failed to open Controller')
        exit()

    autd.check_trials = 50

    run(autd)