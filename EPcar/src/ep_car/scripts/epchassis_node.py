#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from robomaster import robot
from robomaster import led
import math
def run_callback(twist):
    rospy.loginfo("run as:")
    print(f"x:{twist.linear.x} y:{twist.linear.y} z:{twist.linear.z}")
    print(f"roll:{twist.angular.x} pitch:{twist.angular.y} yaw:{twist.angular.z}")
    ep_chassis.drive_speed(x=twist.linear.x, y=0, z=twist.angular.z, timeout=10)
    ep_led.set_led(comp=led.COMP_ALL, r=0, g=255, b=0, effect=led.EFFECT_ON)

def imu_callback(imu_info):
    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = imu_info

def pos_callback(pos_info):
    global pos_pub
    x, y, z = pos_info
    pos_msg = Twist()
    pos_msg.linear.x = x
    pos_msg.linear.y = y
    pos_msg.angular.z = -z/180*math.pi
    pos_pub.publish(pos_msg)
    # rospy.loginfo(f"{x}    {y}    {z}")

def atti(att_info):
    y ,r ,p = att_info
    rospy.logerr(f"{y}    {r}    {p}")

if __name__ == "__main__":
    rospy.init_node("epchassis")
    # EP Init
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="rndis")
    # get chassis object
    ep_chassis = ep_robot.chassis
    ep_led = ep_robot.led
    rospy.loginfo("EP init successed!")
    pos_pub = rospy.Publisher("position",Twist,queue_size=3)
    # sub chassis data
    ep_chassis.sub_position(cs=0, freq=5,callback=pos_callback)
    ep_chassis.sub_attitude(freq=5, callback=atti)

    rospy.spin()
    ep_chassis.drive_speed(x=0, y=0, z=0, timeout=1)

    # close ep
    ep_chassis.unsub_position()
    ep_robot.close()
    exit(0)


