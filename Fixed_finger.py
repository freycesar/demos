'''
Author: SUN Qingyu sunqingyu1997@gmail.com
Date: 2023-05-25 15:05:46
LastEditors: SUN Qingyu sunqingyu1997@gmail.com
LastEditTime: 2023-05-25 15:38:33
FilePath: \demos\Fixed_finger.py
'''
from pyautd3.link import SOEM
from pyautd3.link import Simulator
from pyautd3.gain import Focus
from pyautd3 import Controller, SilencerConfig, Clear, Synchronize, Stop, DEVICE_WIDTH, DEVICE_HEIGHT
from pyautd3.modulation import Static, Sine
import numpy as np
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
    stm = GainSTM(autd)
    radius = 1.0
    # step = 0.2
    # size = 50 * 2 * np.pi * radius // step

    center = autd.geometry.center + np.array([0., 0., 150.])
    for i in range(1000):
        radius += 0.005
        # theta = step / radius
        theta = 50 * 2 * np.pi * i / 1000
        p = radius * np.array([np.cos(theta), np.sin(theta), 0])
        f = Focus(center + p)
        stm.add(f)

    m = Static(1)
    stm.frequency = 0.4
    autd.send(m, stm)

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

    # if if_use_simulator == 'y':
    #     print('Use simulator')
    #     link = Simulator().build()
    # elif if_use_simulator == 'n':
    #     print('Use AUTD device')
    #     link = SOEM().high_precision(True).build()
    # else:
    #     exit()

    link = SOEM().high_precision(True).build()

    if not autd.open(link):
        print('Failed to open Controller')
        exit()

    autd.check_trials = 50

    run(autd)