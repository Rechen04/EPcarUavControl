        # self._standing = True
        # self._sub = rospy.Subscriber("/cmd_vel", Twist, self._twist_cb, queue_size=3)

    # def _twist_cb(self, msg):
    #     if msg.linear.x != 0 or msg.linear.y != 0 or msg.angular.z != 0:
    #         self._standing = False
        
    #     if msg.linear.x == 0 and msg.linear.y == 0 and msg.angular.z == 0:
    #         flight_vel(0, 0, 0)
    #         self._standing = True

    #     if not self._standing:
    #         flight_vel(msg.linear.x, -msg.linear.y, -msg.angular.z/math.pi*180.0)

# def flight_vel(x,y,yaw):
#     client_vel = rospy.ServiceProxy("flightByVel",flightByVel)
#     client_vel.wait_for_service
#     try:
#         response = client_vel.call(x,-y,0,yaw,1.0)
#     except:
#         rospy.logerr("flight by vel failed!")
#         return 0
#     return response