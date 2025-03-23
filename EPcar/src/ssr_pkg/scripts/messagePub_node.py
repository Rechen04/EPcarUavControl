#!/usr/bin/env python3

import rospy
from std_msgs.msg import String

if __name__ == "__main__":
    rospy.init_node("messagePub_node")
    rospy.logwarn("message")

    pub = rospy.Publisher("qun",String,queue_size=10)

    rate = rospy.Rate(2)

    while not rospy.is_shutdown():
        rospy.loginfo("message")
        msg = String()
        msg.data = "message_data"
        pub.publish(msg)
        rate.sleep()

    exit(0)