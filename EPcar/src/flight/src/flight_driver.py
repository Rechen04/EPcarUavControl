#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist

from flight.srv import *
import cv2
import sys
sys.path.append('/home/tta/catkin_ws/src/flight/src/')

def flight_takeoffOrLanding(state):
    client = rospy.ServiceProxy("takeoffOrLanding",takeoffOrLanding)
    client.wait_for_service
    try:
        if state == 1:
            response = client.call(1)
            rospy.loginfo("start taking off...")
        else:
            response = client.call(2)
            rospy.logwarn("start landing...")
    except:
        rospy.logerr("flight by vel failed!")
        return 0
    return response

class Flight_node:
    def __init__(self):
        # flight_takeoffOrLanding(1)
        # Subscribe to twist topic
        self.flight_server = rospy.Service("photoFlight",photoFlight,self._photo_flight_cb)

    def _photo_flight_cb(self,request):
        com = request.command
        response = photoFlightResponse()
        if com == "photoFlight":
            dir = "/home/tta/catkin_ws/src/yolo/src/yolov5/photo_flight.jpg"
            rtsp_url = 'rtsp://192.168.0.10:8554/live'
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                rospy.logerr("Vidoe open failed!")
                response.result = False

            ret, frame = cap.read()
            try:
                if ret:
                    cv2.imwrite(dir, frame)
                    rospy.loginfo("flight photo successed!")
                    response.result = True
                else:
                    rospy.logerr("flight photo failed!")
                    response.result = False

                cap.release()
                
            except:
                rospy.logerr("Can not take a photo")
                response.result = False
        elif com == "photoCharge":
            dir = "/home/tta/catkin_ws/src/yolo/src/yolov5/photo_charge.jpg"
            rtsp_url = 'rtsp://192.168.0.10:8554/live'
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                rospy.logerr("Vidoe open failed!")
                response.result = False

            ret, frame = cap.read()
            try:
                if ret:
                    cv2.imwrite(dir, frame)
                    rospy.loginfo("flight photo successed!")
                    response.result = True
                else:
                    rospy.logerr("flight photo failed!")
                    response.result = False

                cap.release()
                
            except:
                rospy.logerr("Can not take a photo")
                response.result = False
        else:
            rospy.logerr("photo command failed")
            response.result = False
        return response
if __name__ == '__main__':
    rospy.init_node("flight_driver")
    node = Flight_node()
    rospy.loginfo("Start flight driver successed...")

    rospy.spin()