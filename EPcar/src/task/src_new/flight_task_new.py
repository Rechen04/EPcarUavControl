#!/usr/bin/env python3

import rospy
from yolo.srv import *
from room_writer import Room_writer
from flight.srv import *
from std_msgs.msg import String

pos = [0 , 0 , 0]

def flight_takeoffOrLanding(state):
    pub_flightstate = rospy.Publisher("flight_takeoff",String,queue_size= 10)
    msg_flight = String()
    msg_flight.data = "flight ok! ep_car start"
    client = rospy.ServiceProxy("takeoffOrLanding",takeoffOrLanding)
    client.wait_for_service()
    rospy.sleep(0.5)
    try:
        if state == 1:
            rospy.loginfo("Calling service to take off...")
            response = client.call(1)
            rospy.loginfo("start taking off...")
            time_flight = rospy.Time.now()
            while rospy.Time.now() - time_flight <= rospy.Duration(3):
                rospy.loginfo("flight ok! ep_car start")
                pub_flightstate.publish(msg_flight)
            pub_flightstate.unregister()
            rospy.sleep(3)
        else:
            response = client.call(2)
            rospy.logwarn("start landing...")
    except:
        rospy.logerr("flight by vel failed!")
        return 0
    return response

# def photo_and_yolo_flight(state = "photo_flight"):
#     photo_client = rospy.ServiceProxy("photoFlight",photoFlight)
#     photo_client.wait_for_service()
#     rospy.sleep(0.5)
#     if state == "photo_flight":
#         photo_response = photo_client.call("photoFlight")
#     elif state == "photo_charge":
#         photo_response = photo_client.call("photoCharge")
#     else:
#         rospy.logerr("photo failed")

#     if photo_response:
#         yolo_client = rospy.ServiceProxy("detectsrv",detectsrv)
#         yolo_client.wait_for_service()
#         if state == "photo_flight":
#             yolo_response = yolo_client.call("photo_flight.jpg")
#             rospy.loginfo("flight photo successed")
#         elif state == "photo_charge":
#             yolo_response = yolo_client.call("photo_charge.jpg")
#             rospy.loginfo("charge photo successed")
#         else:
#             rospy.logerr("flight photo failed!")

#         rospy.loginfo(yolo_response)
#         yolo_result = yolo_response.result
#     else:
#         return [-2]
#     return yolo_result

def nav_to_goal(point):
    flight_client = rospy.ServiceProxy("flightByOffset", flightByOffset)
    rospy.loginfo("Waiting for the flight nav service...")
    flight_client.wait_for_service()
    rospy.sleep(0.5)
    global pos
    offset = [p - q for p, q in zip(point, pos)]
    targetYaw = 0.2
    yawThreshold = 1.0
    posThreshold = 0.5
    
    rospy.loginfo("Starting navigation to"+offset)
    
    try:
        # 调用服务
        flight_response = flight_client.call(offset, targetYaw, yawThreshold, posThreshold)
        
        # 等待响应
        timeout = rospy.Time.now() + rospy.Duration(10)  # 10秒超时
        while rospy.Time.now() < timeout:
            if flight_response.ack != 0:  # ack = 0 通常代表未完成
                pos = point
                rospy.loginfo("Navigation Success! Current position:"+ pos )
                return True
            rospy.sleep(0.1)  # 每 0.1 秒检查一次
        
        rospy.logerr("Navigation timeout...")
        return False
    
    except rospy.ServiceException as e:
        rospy.logerr(f"Service call failed: {e}")
        return False


def flight_gimbalControl(pitch):
    rospy.loginfo("start contorl gimbal")
    rospy.wait_for_service("gimbalControl")
    client = rospy.ServiceProxy("gimbalControl",gimbalControl)
    try:
        response = client.call(pitch,0,0)
        rospy.loginfo("gimbal control succeed!")
    except:
        rospy.logerr("gimbal control failed!")
        return 0
    return response

nav_point = [
    #I区域
    [0.1,-0.3,1],      #1-1 (x,y,z)
    [0.75,0.3,1],       #1-2 
    [2,0.3,1],          #1-3 
    [3,0.3,1],          #1-4 
    [-0.75,0.3,1.5],    #2-1 
    [0.75,0.3,1.5],     #2-2 
    [2,0.3,1.5],        #2-3 
    [3,0.3,1.5]         #2-4

    #II区域
    [-0.75,-2,1],      #1-1 (x,y,z)
    [0.75,-2,1],       #1-2 
    [2,-2,1],          #1-3 
    [3,-2,1],          #1-4 
    [-0.75,-2,1.5],    #2-1 
    [0.75,-2,1.5],     #2-2 
    [2,-2,1.5],        #2-3 
    [3,-2,1.5]         #2-4 
]

if __name__ == '__main__':
    rospy.init_node("ep_flight_task")
    flight_takeoffOrLanding(1)
    point = nav_point[0]
    nav_to_goal(point)
    # flight_takeoffOrLanding(2)
    photo_client = rospy.ServiceProxy("photoFlight",photoFlight)
    photo_client.wait_for_service()
    rospy.sleep(0.5)
    photo_response = photo_client.call("photoFlight")
