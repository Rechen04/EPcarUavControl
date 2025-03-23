#!/usr/bin/env python3

import rospy
from std_msgs.msg import String

def message_callback(msg):
    rospy.loginfo(msg)

if __name__ == "__main__":
    rospy.init_node("messageSub_node")
    rospy.logwarn("SUB!!")

    sub = rospy.Subscriber("qun",String,message_callback,queue_size=10)
    
    rospy.spin()
        
    exit(0)