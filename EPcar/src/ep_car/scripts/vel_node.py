#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist

if __name__ == "__main__":
    rospy.init_node("vel_node")

    vel_pub = rospy.Publisher("cmd_vel",Twist,queue_size=10)

    vel_msg = Twist()
    # run as a small circle
    vel_msg.linear.x = 0.1
    vel_msg.angular.z = 30



    rate = rospy.Rate(5)
    while not rospy.is_shutdown():
        rospy.loginfo("vel_msg data:")
        print(f"x:{vel_msg.linear.x} y:{vel_msg.linear.y} z:{vel_msg.linear.z}")
        print(f"roll:{vel_msg.angular.x} pitch:{vel_msg.angular.y} yaw:{vel_msg.angular.z}")
        vel_pub.publish(vel_msg)
        rate.sleep()

    exit(0)