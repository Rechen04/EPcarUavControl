#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from robomaster import robot
from robomaster import led
count = 0
def runbylidar_callback(msg):
    global vel_pub
    global count
    rospy.loginfo("run as:")
    if count > 0:
        count -= 1
        return
    vel_msg = Twist()
    for i in range(0,80):
        distl = msg.ranges[573+i]
        distr = msg.ranges[573-i]
        if distr < 0.6 or distl < 0.6:
            count = 10
            if distl < distr:
                vel_msg.linear.x = 0.3
                vel_msg.angular.z = 80 - 0.5 * i
                if distl < 0.4:
                    vel_msg.linear.x = 0.2
                    vel_msg.angular.z = 100 - 0.5 * i
            else:
                vel_msg.linear.x = 0.3
                vel_msg.angular.z = -80 + 0.5 * i
                if distr < 0.4:
                    vel_msg.linear.x = 0.2
                    vel_msg.angular.z = -100 + 0.5 * i
            break
        else:
            vel_msg.linear.x = 0.5
            vel_msg.angular.z = 0
    vel_pub.publish(vel_msg)
    rospy.loginfo("front dist: %f m",)

if __name__ == "__main__":

    rospy.init_node("runbylidar")
    lidar_sub = rospy.Subscriber("/scan",LaserScan,runbylidar_callback,queue_size=10)
    rospy.loginfo("Wait for cmd_vel......")
    vel_pub = rospy.Publisher("/cmd_vel",Twist,queue_size=10)
    rospy.spin()
    exit(0)


