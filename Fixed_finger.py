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
    # n_updatecircle = 1.
    # stm.frequency = 5.
    # time_step = n_updatecircle / stm.frequency
    time_step = 0.2
    center = autd.geometry.center + np.array([0., 0., 150.])

#       共九种刺激
#       半径range：0-4 mm, 0-8 mm, 0-12 mm
#       速度变化：2 mm/s, 5 mm/s, 8 mm/s
#       每种刺激对应一个总时长，因为固定STM频率不变，所以(1)圈数确定，为总时长/频率向上取正
#       (2) 当圈数确定后，每圈半径增大的量也可以确定

    while True:
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
        for circle_number in range(50):
            for i in range(size):
                # theta = step / radius
                theta = 2 * np.pi * i / size
                p = radius * np.array([np.cos(theta), np.sin(theta), 0])
                f = Focus(center + p)
                stm.add(f)
            libc.HighPrecisionSleep(ctypes.c_float(time_step))
            # time.sleep(time_step)
            radius -= 0.1

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

# 实验一（本次不做）：先测力回归声压和stm频率的关系，然后分别测单位时间里手指按不同材料的力-时间曲线
#                 因为力和高度变化量成正比，则半径和速度的1/3次方成比例
#                 分析则通过混淆矩阵，来判断渲染是否成功
# 实验二：分别控制接触面积变化速率和半径范围不变，给三个level的刺激共3 * 3 = 9 种，共 9 * 3 = 27 次随机present，参加者回答rank1-5（）
#        不控制总时长，控制STM频率为5Hz，其中半径range：0-4 mm, 0-8 mm, 0-12 mm
#                                   速度变化：2 mm/s, 5 mm/s, 8 mm/s
#                                   因此所用时间为：2s, 4s, 6s / 0.8s, 1.6s, 2.4s / 0.5s, 1s, 1.5s
#                                   因为STM频率为 0.2s，  
#        首先算3by3的混淆矩阵，来评价渲染是否成功
#        然后9个之间做t test检验比较，得出两个factor哪个影响大

if __name__ == '__main__':
 
    W_cos = math.cos(math.pi/12) * DEVICE_WIDTH
    geometry = Geometry.Builder()\
            .add_device([W_cos - (DEVICE_WIDTH - W_cos), DEVICE_HEIGHT - 10 + 12.5, 0.], [math.pi, math.pi/12, 0.])\
            .add_device([W_cos - (DEVICE_WIDTH - W_cos), -10 - 12.5, 0.], [math.pi, math.pi/12, 0.])\
            .add_device([-W_cos + (DEVICE_WIDTH - W_cos),  12.5, 0.], [0., math.pi/12, 0.])\
            .add_device([-W_cos + (DEVICE_WIDTH - W_cos), -DEVICE_HEIGHT - 12.5, 0.], [0., math.pi/12, 0.])\
            .build()
    
    on_lost_func = OnLostFunc(on_lost)
    # link = Simulator().build()
    link = SOEM().on_lost(on_lost_func).build()    
    autd = Controller.open(geometry, link)
    # if_use_simulator = input('If use simulator? [y: simulator] or [n: AUTD]: ')

    autd.check_trials = 50

    run(autd)