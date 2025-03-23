#!/usr/bin/env python3

import rospy
from flight.srv import *
from yolo.srv import *

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

if __name__ == '__main__':
    rospy.init_node("flight_charge")
    # gimbal_response = flight_gimbalControl(-90)
    gimbal_response = flight_gimbalControl(0)
    if gimbal_response:
        photo_client = rospy.ServiceProxy("photoFlight",photoFlight)
        photo_response = photo_client.call("photoCharge")
        if photo_response:
            rospy.loginfo("flight photo successed")
        else:
            rospy.logerr("flight photo failed!")
        if photo_response:
            yolo_client = rospy.ServiceProxy("detectsrv",detectsrv)
            yolo_response = yolo_client.call("photo_charge.jpg") 
            rospy.loginfo(yolo_response)