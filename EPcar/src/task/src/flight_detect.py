#!/usr/bin/env python3

import rospy
from flight.srv import *
from yolo.srv import *

if __name__ == '__main__':
    rospy.init_node("flight_detect")
    photo_client = rospy.ServiceProxy("photoFlight",photoFlight)
    photo_response = photo_client.call("photoFlight")
    if photo_response:
        rospy.loginfo("flight photo successed")
    else:
        rospy.logerr("flight photo failed!")
    if photo_response:
        yolo_client = rospy.ServiceProxy("detectsrv",detectsrv)
        yolo_response = yolo_client.call("photo_flight.jpg") 
        rospy.loginfo(yolo_response)