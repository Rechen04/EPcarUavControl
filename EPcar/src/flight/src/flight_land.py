#!/usr/bin/env python3
import rospy
from flight.srv import *

def flight_gimbalControl(pitch):
    rospy.loginfo("start contorl gimbal")
    rospy.wait_for_service("gimbalControl")
    client = rospy.ServiceProxy("gimbalControl",gimbalControl)
    try:
            response = client.call(pitch,0,0)
    except:
        rospy.logerr("gimbal control failed!")
        return 0
    return response

def flight_takeoffOrLanding(state):
    if state == 1:
        rospy.logwarn("start taking off...")
    else:
        rospy.logwarn("start landing...")
    rospy.wait_for_service("takeoffOrLanding")
    client = rospy.ServiceProxy("takeoffOrLanding",takeoffOrLanding)
    try:
        if state == 1:
            response = client.call(1)
        else:
            response = client.call(2)
    except:
        rospy.logerr("flight by vel failed!")
        return 0
    return response

if __name__ == "__main__":
    rospy.init_node("flight_land")
    # flight_takeoffOrLanding(2)
    flight_gimbalControl(-45)