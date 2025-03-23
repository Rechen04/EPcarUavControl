#!/usr/bin/env python3

import rospy
from robomaster_driver.srv import *
from yolo.srv import *
import time

if __name__ == '__main__':
    rospy.init_node("car_detect")
    photo_client = rospy.ServiceProxy("photo",photo)
    photo_response = photo_client.call("yolo")
    if photo_response:
        rospy.sleep(1)
        photo_client.call("yolo")
        rospy.loginfo("photo successed")
    else:
        rospy.logerr("photo failed!")
    if photo_response:
        yolo_client = rospy.ServiceProxy("detectsrv",detectsrv)
        to = time.time()
        yolo_response = yolo_client.call("photo.jpg") 
        print(yolo_response)