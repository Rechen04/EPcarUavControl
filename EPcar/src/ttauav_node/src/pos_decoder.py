#!/usr/bin/env python
import rospy
from ttauav_node.msg import uavdata
from time import time

class Pos_decoder:
    def __init__(self):
        self.uavsub = rospy.Subscriber("uavdata",uavdata,self.uav_cb,queue_size=100)
        self.tl = 0
        self.velN=0
        self.velE=0
        self.velD=0
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0
        
    def uav_cb(self,msg):
        # if self.tl == 0:
        #     self.tl = time()
        #     return
        if abs(msg.velN) < 0.01 or abs(msg.velN) > 2.0:
            msg.velN = 0
        if abs(msg.velE) < 0.01 or abs(msg.velE) > 2.0:
            msg.velE = 0
        if abs(msg.velD) < 0.01 or abs(msg.velD) > 2.0:
            msg.velD = 0
        if abs(msg.accN) < 0.02 or abs(msg.accN) > 4.0:
            msg.accN = 0
        if abs(msg.accE) < 0.02 or abs(msg.accE) > 4.0:
            msg.accE = 0
        if abs(msg.accD) < 0.02 or abs(msg.accD) > 4.0:
            msg.accD = 0

        dt = 0.1
        # t0 = time()
        # vel_x = -(msg.velE + msg.accE * (t0-self.tl))
        # vel_y = -(msg.velN + msg.accN * (t0-self.tl))
        # vel_z = msg.velD + msg.accD * (t0-self.tl)

        # self.pos_x = vel_x * (t0-self.tl)
        # self.pos_y = vel_y * (t0-self.tl)
        # self.pos_z = vel_z * (t0-self.tl)

        self.velN += msg.accN * dt
        self.velE += msg.accE * dt
        self.velD += msg.accD * dt

        self.pos_x += self.velN * dt + 0.5 * msg.accN * (dt ** 2)
        self.pos_y += self.velE * dt + 0.5 * msg.accE * (dt ** 2)
        self.pos_z += self.velD * dt + 0.5 * msg.accD * (dt ** 2)
        rospy.loginfo(f"pos_x:{self.pos_x}pos_y:{self.pos_y}pos_z:{self.pos_z}")
        # self.tl = time()


if __name__ == "__main__":
    rospy.init_node("pos_decoder")
    pos_decoder = Pos_decoder()

    rospy.spin()

