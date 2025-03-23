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

nav_point = [
    [0,0,0],
    [2.5,0.5,0],#area 1
    [5,-1.3,0],#area 2
    [7,0,0]#area C
        ]

if __name__ == '__main__':
    rospy.init_node("ep_task")
    msg = String()
    standing_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
    standing_msg = Twist()
    standing_msg.linear.x = 0
    standing_msg.linear.y = 0
    standing_msg.angular.z = 0
    rospy.Subscriber("flight_takeoff", String, callback_flight)
    nav_to_goal(nav_point[1])
    rospy.wait_for_message("flight_takeoff", String)
    rospy.sleep(5)
    nav_to_goal(nav_point[2])
    rospy.Subscriber("flight_landed", String, callback_flight)
    rospy.wait_for_message("flight_landed", String)
    rospy.sleep(5)
    nav_to_goal(nav_point[3])
    rospy.sleep(5)
    nav_to_goal(nav_point[0])
    while not rospy.is_shutdown:
        standing_pub.publish(standing_msg)