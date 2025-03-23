#!/usr/bin/env python3

import rospy
from robomaster_driver.srv import *
from flight.srv import *
from yolo.srv import *
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import math
from room_writer import Room_writer
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from time import time

def euler_to_quaternion(yaw, pitch, roll):
    qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
    qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
    qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    return [qx, qy, qz, qw]

def photo_and_yolo():
    photo_client = rospy.ServiceProxy("photo",photo)
    photo_response = photo_client.call("yolo")
    if photo_response:
        rospy.sleep(1)
        photo_client.call("yolo")
        rospy.loginfo("photo successed")
    else:
        rospy.logerr("photo failed!")
        return [-2]
    if photo_response:
        yolo_client = rospy.ServiceProxy("detectsrv",detectsrv)
        yolo_response = yolo_client.call("photo.jpg") 
        print(yolo_response)
        yolo_result = yolo_response.result
    else:
        return [-2]
    return yolo_result

def nav_to_goal(point):
    x, y, yaw=point
    ac = actionlib.SimpleActionClient('move_base',MoveBaseAction)
    rospy.loginfo("wait for the movebase server.....")
    ac.wait_for_server()
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id="map"
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.position.z = 0.0
    qx, qy, qz, qw = euler_to_quaternion(yaw,0,0)
    goal.target_pose.pose.orientation.x = 0.0
    goal.target_pose.pose.orientation.y = 0.0
    goal.target_pose.pose.orientation.z = qz
    goal.target_pose.pose.orientation.w = qw

    ac.send_goal(goal)
    rospy.loginfo("strating navigation...")
    ac.wait_for_result()
    if ac.get_state() == actionlib.GoalStatus.SUCCEEDED:
        rospy.loginfo("Navigation Success!")
        return True
    else:
        rospy.logerr("Navigation False...")
        return False

def callback_flight(msg):
    rospy.loginfo("%s", msg.data)
    # if msg.data == "flight ok! ep_car start":
    #     rospy.sleep(5)
    #     rospy.loginfo("ep_car start")

# nav_point = [
#     # [0,0,0],
#     [2.15,0.4,1.571],[3.65,0.35,1.571],[4.9,0.48,1.571],[5.93,0.52,1.571],
#     [7.45,0.5,1.571],[7.45,2.45,1.571], #1.76
#     [5.9,2.98,1.571],[4.9,2.95,1.571],[3.68,2.81,1.571],[2.15,2.85,1.571],
#     [0,0,1.571]
#         ]
nav_point = [
    # [0,0,0],
    # [2.18,0.4,1.571],[3.65,0.35,1.571],[4.9,0.48,1.571],[5.93,0.52,1.571],
    # [7.45,0.5,1.571],[7.45,2.50,1.571], #1.76
    # [5.9,2.96,1.571],[4.92,2.93,1.571],[3.7,2.81,1.571],[2.15,2.85,1.571],
    # [0,0,1.571]
    #     ]
    [2.15,0.4,1.571],[3.65,0.35,1.571],[4.9,0.48,1.571],[5.93,0.52,1.571],
    [7.45,0.5,1.571],[7.45,2.50,1.571], #1.76
    [5.95,2.92,1.571],[4.92,2.91,1.571],[3.7,2.79,1.571],[2.15,2.83,1.571],
    [0,0,1.571]
        ]
if __name__ == '__main__':
    rospy.init_node("ep_task")
    rw = Room_writer()
    rw.write_header()
    rw.data_save("/home/tta/list_of_goods_2")
    task_result = []
    task_result_end = []
    goods = 0
    bads = 0
    msg = String()
    standing_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
    standing_msg = Twist()
    standing_msg.linear.x = 0
    standing_msg.linear.y = 0
    standing_msg.angular.z = 0
    rospy.Subscriber("flight_takeoff", String, callback_flight)
    rospy.wait_for_message("flight_takeoff", String)
    rospy.sleep(5)
    for point in nav_point:
        nav_state = nav_to_goal(point)
        if nav_state:
            rospy.sleep(1)
            if point[0] > 1 and point[0] < 6:
                detect_state = photo_and_yolo()
                if detect_state[0] >= -1:
                    task_result.append(detect_state)
            elif point[0]>6 and point[1]>2:
                t0 = time()
                while rospy.wait_for_message("flight_takeoff", String) is None:
                    # nav_to_goal(point)
                    standing_pub.publish(standing_msg)
                    if time() - t0 > 120:
                        break
                    rospy.Rate(1)
                standing_pub.unregister()
                rospy.sleep(8)
            else:
                pass
        else:
            pass
    rospy.loginfo(f"\nTask result: {task_result}")
    
    for array in task_result:
        goods=0
        bads=0
        for element in array:
            if element ==1:
                goods+=1
            elif element == 0:
                bads+=1
            else:
                pass
        task_result_end.append([goods,bads])
    # task_result_end = [[1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2]]
    rw.write_car_data("/home/tta/list_of_goods_2.xls",task_result_end)
    rw.data_save("/home/tta/list_of_goods_2")
    rospy.loginfo(f"xl written.")
    while not rospy.is_shutdown:
        standing_pub.publish(standing_msg)