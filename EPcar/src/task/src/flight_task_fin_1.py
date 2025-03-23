#!/usr/bin/env python3

import rospy
from yolo.srv import *
from room_writer import Room_writer
from flight.srv import *
from std_msgs.msg import String

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

def photo_and_yolo_flight(state = "photo_flight"):
    photo_client = rospy.ServiceProxy("photoFlight",photoFlight)
    photo_client.wait_for_service()
    rospy.sleep(0.5)
    if state == "photo_flight":
        photo_response = photo_client.call("photoFlight")
    elif state == "photo_charge":
        photo_response = photo_client.call("photoCharge")
    else:
        rospy.logerr("photo failed")

    if photo_response:
        yolo_client = rospy.ServiceProxy("detectsrv",detectsrv)
        yolo_client.wait_for_service()
        if state == "photo_flight":
            yolo_response = yolo_client.call("photo_flight.jpg")
            rospy.loginfo("flight photo successed")
        elif state == "photo_charge":
            yolo_response = yolo_client.call("photo_charge.jpg")
            rospy.loginfo("charge photo successed")
        else:
            rospy.logerr("flight photo failed!")

        rospy.loginfo(yolo_response)
        yolo_result = yolo_response.result
    else:
        return [-2]
    return yolo_result

def nav_to_goal(point , flight_time = 4.0):
    flight_client = rospy.ServiceProxy("flightByVel",flightByVel)
    rospy.loginfo("wait for the flight nav.....")
    flight_client.wait_for_service()
    rospy.sleep(0.5)
    
    vel_n,vel_e,vel_d,target_yaw,fly_time,yolo_state=point
    flight_response =flight_client.call(vel_n,vel_e,vel_d,target_yaw,fly_time)
    rospy.loginfo("strating navigation...")
    rospy.sleep(flight_time)
    if flight_response:
        rospy.loginfo("Navigation Success!")
        return True
    else:
        rospy.logerr("Navigation False...")
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
    [0.01,0.48,-0.05,0.5,4000,1],[0.01,0.37,-0.01,0,4000,1],[0.04,0.30,0,0.5,4000,1],[0.01,0.25,-0.01,0,4000,1],
    [0,0.33,0,0,4000,0],[0.57,0,0,0,4000,2],
    # [0,0,0,0,0,2],
    [0.05,-0.28,-0.01,0,4000,1],[0.01,-0.25,-0.01,0,4000,1],[-0.03,-0.28,0,0.5,4000,1],[0,-0.34,-0.01,0,4000,1],
    [0,-0.48,0.04,0,4000,0],[-0.32,0,0,0,7500,2]
        ]

if __name__ == '__main__':
    rospy.init_node("ep_flight_task")
    rw = Room_writer()
    flight_takeoffOrLanding(1)
    rospy.sleep(8)
    task_result = []
    task_result_end = []
    goods = 0
    bads = 0
    goods_second = 0
    bads_second = 0
    landing_state = 0
    nav_uint_x = [0,-0.1,0,0,1000,2]
    nav_uint__x = [0,0.1,0,0,1000,2]
    nav_uint_y = [0.08,0,0,0,1000,2]
    nav_uint__y = [-0.08,0,0,0,1000,2]
    nav_uint_x_y = [0.08,-0.1,0,0,1000,2]
    nav_uint_x__y = [-0.08,-0.1,0,0,1000,2]
    nav_uint__x_y = [0.08,0.1,0,0,1000,2]
    nav_uint__x__y = [-0.08,0.1,0,0,1000,2]

    nav_uint_x_min = [0,-0.1,0,0,500,2]
    nav_uint__x_min = [0,0.1,0,0,500,2]
    nav_uint_y_min = [0.08,0,0,0,500,2]
    nav_uint__y_min = [-0.08,0,0,0,500,2]
    nav_uint_x_y_min = [0.08,-0.1,0,0,500,2]
    nav_uint_x__y_min = [-0.08,-0.1,0,0,500,2]
    nav_uint__x_y_min = [0.08,0.1,0,0,500,2]
    nav_uint__x__y_min = [-0.08,0.1,0,0,500,2]

    Final = True

    for point in nav_point:
        nav_state = nav_to_goal(point)
        if nav_state and point[5]==1:
            rospy.sleep(3)
            detect_state = photo_and_yolo_flight()
            if detect_state[0] >= -1:
                task_result.append(detect_state)
                rospy.sleep(3)
            else:
                pass
        elif nav_state and point[5]==2:
            landing_state +=1
            if landing_state ==2:
                rospy.loginfo(f"\nTask result: {task_result}")
                
                for array in task_result:
                    goods=0
                    bads=0
                    goods_second=0
                    bads_second=0
                    for element in array:
                        if element == 0:
                            bads+=1
                        elif element == 1:
                            goods+=1
                        elif element == 2:
                            bads_second+=1
                        elif element == 3:
                            goods_second+=1
                        else:
                            pass
                    task_result_end.append([goods,bads,goods_second,bads_second])
                # task_result_end = [[1, 0, 0, 0], [1, 1, 0, 3], [0, 1, 1, 2], [2, 3, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [2, 1, 1, 1]]
                rospy.loginfo(f"\nTask result_end: {task_result_end}")
                rw.write_air_data("/home/tta/list_of_goods_1.xls",task_result_end,cls="fin")
                rw.data_save("/home/tta/list_of_goods_1")
                rospy.loginfo(f"xl written.")
            
            flight_gimbalControl(-90)
            rospy.sleep(2)
            detect_state = photo_and_yolo_flight("photo_charge")
            location_x,location_y = detect_state
            while location_x ==0 and location_y ==0:
                rospy.sleep(5)
                detect_state = photo_and_yolo_flight("photo_charge")
                location_x,location_y = detect_state
            
            rospy.sleep(5)

            while location_x < 446 or location_x > 526 or location_y < 460 or location_y > 540:
                if location_x < 446 and location_y < 460:
                    nav_to_goal(nav_uint_x_y,1)
                elif location_x < 446 and location_y > 540:
                    nav_to_goal(nav_uint_x__y,1)
                elif location_x > 526 and location_y < 460:
                    nav_to_goal(nav_uint__x_y,1)
                elif location_x > 526 and location_y > 540:
                    nav_to_goal(nav_uint__x__y,1)
                elif location_x < 446 and location_y < 540 and location_y > 460:
                    nav_to_goal(nav_uint_x,1)
                elif location_x > 526 and location_y < 540 and location_y > 460:
                    nav_to_goal(nav_uint__x,1)
                elif location_y < 460 and location_x < 526 and location_x > 446:
                    nav_to_goal(nav_uint_y,1)
                elif location_y > 540 and location_x < 526 and location_x > 446:
                    nav_to_goal(nav_uint__y,1)
                else:
                    pass
                detect_state = photo_and_yolo_flight("photo_charge")
                location_x,location_y = detect_state

            nav_to_goal([0,0,-0.08,0,4000,2])
            detect_state = photo_and_yolo_flight("photo_charge")
            location_x,location_y = detect_state
            
            while location_x < 456 or location_x > 516 or location_y < 470 or location_y > 530:
                if location_x < 456 and location_y < 470:
                    nav_to_goal(nav_uint_x_y_min,0.5)
                elif location_x < 456 and location_y > 530:
                    nav_to_goal(nav_uint_x__y_min,0.5)
                elif location_x > 516 and location_y < 470:
                    nav_to_goal(nav_uint__x_y_min,0.5)
                elif location_x > 516 and location_y > 530:
                    nav_to_goal(nav_uint__x__y_min,0.5)
                elif location_x < 456 and location_y < 530 and location_y > 470:
                    nav_to_goal(nav_uint_x_min,0.5)
                elif location_x > 516 and location_y < 530 and location_y > 470:
                    nav_to_goal(nav_uint__x_min,0.5)
                elif location_y < 470 and location_x < 516 and location_x > 456:
                    nav_to_goal(nav_uint_y_min,0.5)
                elif location_y > 530 and location_x < 516 and location_x > 456:
                    nav_to_goal(nav_uint__y_min,0.5)
                else:
                    pass
                detect_state = photo_and_yolo_flight("photo_charge")
                location_x,location_y = detect_state

            rospy.sleep(0.5)
            flight_takeoffOrLanding(2)
            rospy.sleep(10)
            
            if landing_state == 1:
                flight_takeoffOrLanding(1)
                flight_gimbalControl(90)
                rospy.sleep(5)
            else:
                pass
        else:
            pass
            
    rospy.sleep(1)
    flight_gimbalControl(90)