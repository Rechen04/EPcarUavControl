#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from ttauav_node.msg import uavdata
import math
import numpy as np

position_x = 0.0
position_y = 0.0
position_z = 0.0

velocity_x = 0.0
velocity_y = 0.0
velocity_z = 0.0

# ¹ýÂË²ÎÊý
alpha = 0.5
dt = 0.1  # ¹Ì¶¨Ê±¼ä²½³¤

latest_msg = None

def shuju_callback(msg):
    global latest_msg
    latest_msg = msg

def timer_callback(event):
    global latest_msg, position_x, position_y, position_z
    global velocity_x, velocity_y, velocity_z
    global alpha, dt

    if latest_msg is None:
        return

    msg = latest_msg

    # Ð£ÕýËÙ¶ÈÊý¾Ý
    if abs(msg.velN) < 0.03 or abs(msg.velN) > 3.0:
        msg.velN = 0
    if abs(msg.velE) < 0.03 or abs(msg.velE) > 3.0:
        msg.velE = 0
    if abs(msg.velD) < 0.03 or abs(msg.velD) > 3.0:
        msg.velD = 0

    # Ð£Õý¼ÓËÙ¶ÈÊý¾Ý
    acc_x = msg.accE
    acc_y = msg.accN
    acc_z = msg.accD

    # ¸üÐÂËÙ¶È£º½áºÏ¼ÓËÙ¶ÈºÍ²âÁ¿ËÙ¶È
    velocity_x = alpha * (velocity_x + acc_x * dt) + (1 - alpha) * msg.velE
    velocity_y = alpha * (velocity_y + acc_y * dt) + (1 - alpha) * msg.velN
    velocity_z = alpha * (velocity_z + acc_z * dt) + (1 - alpha) * msg.velD

    # ¼ÆËãÎ»ÖÃ
    position_x += velocity_x * dt
    position_y += velocity_y * dt
    position_z += velocity_z * dt

    rospy.loginfo("Position: X=%.3f, Y=%.3f, Z=%.3f" %
                  (position_x, position_y, position_z))

if __name__ == "__main__":
    rospy.init_node("shuju")

    sub = rospy.Subscriber("uavdata", uavdata, shuju_callback, queue_size=100)

    timer = rospy.Timer(rospy.Duration(dt), timer_callback)

rospy.spin()