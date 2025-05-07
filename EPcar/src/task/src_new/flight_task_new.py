#!/usr/bin/env python3

import rospy
from yolo.srv import *
from room_writer import Room_writer
from flight.srv import *
from std_msgs.msg import String

pos = [0 , 0 , 0]

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

# def photo_and_yolo_flight(state = "photo_flight"):
#     photo_client = rospy.ServiceProxy("photoFlight",photoFlight)
#     photo_client.wait_for_service()
#     rospy.sleep(0.5)
#     if state == "photo_flight":
#         photo_response = photo_client.call("photoFlight")
#     elif state == "photo_charge":
#         photo_response = photo_client.call("photoCharge")
#     else:
#         rospy.logerr("photo failed")

#     if photo_response:
#         yolo_client = rospy.ServiceProxy("detectsrv",detectsrv)
#         yolo_client.wait_for_service()
#         if state == "photo_flight":
#             yolo_response = yolo_client.call("photo_flight.jpg")
#             rospy.loginfo("flight photo successed")
#         elif state == "photo_charge":
#             yolo_response = yolo_client.call("photo_charge.jpg")
#             rospy.loginfo("charge photo successed")
#         else:
#             rospy.logerr("flight photo failed!")

#         rospy.loginfo(yolo_response)
#         yolo_result = yolo_response.result
#     else:
#         return [-2]
#     return yolo_result

def nav_to_goal(point):
    flight_client = rospy.ServiceProxy("flightByOffset", flightByOffset)
    rospy.loginfo("Waiting for the flight nav service...")
    flight_client.wait_for_service()
    rospy.sleep(0.5)
    global pos
    offset = [p - q for p, q in zip(point, pos)]
    targetYaw = 0.2
    yawThreshold = 1.0
    posThreshold = 0.5
    
    rospy.loginfo("Starting navigation to"+offset)
    
    try:
        # 调用服务
        flight_response = flight_client.call(offset, targetYaw, yawThreshold, posThreshold)
        
        # 等待响应
        timeout = rospy.Time.now() + rospy.Duration(10)  # 10秒超时
        while rospy.Time.now() < timeout:
            if flight_response.ack != 0:  # ack = 0 通常代表未完成
                pos = point
                rospy.loginfo("Navigation Success! Current position:"+ pos )
                return True
            rospy.sleep(0.1)  # 每 0.1 秒检查一次
        
        rospy.logerr("Navigation timeout...")
        return False
    
    except rospy.ServiceException as e:
        rospy.logerr(f"Service call failed: {e}")
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
    #I区域
    [0.1,-0.3,1],      #1-1 (x,y,z)
    [0.75,0.3,1],       #1-2 
    [2,0.3,1],          #1-3 
    [3,0.3,1],          #1-4 
    [-0.75,0.3,1.5],    #2-1 
    [0.75,0.3,1.5],     #2-2 
    [2,0.3,1.5],        #2-3 
    [3,0.3,1.5]         #2-4

    #II区域
    [-0.75,-2,1],      #1-1 (x,y,z)
    [0.75,-2,1],       #1-2 
    [2,-2,1],          #1-3 
    [3,-2,1],          #1-4 
    [-0.75,-2,1.5],    #2-1 
    [0.75,-2,1.5],     #2-2 
    [2,-2,1.5],        #2-3 
    [3,-2,1.5]         #2-4 
]

def take_photo(image_path):
    """
    调用 ROS 服务拍照并保存图像
    """
    try:
        rospy.wait_for_service("photoFlight", timeout=5.0)
        photo_client = rospy.ServiceProxy("photoFlight", photoFlight)
        response = photo_client.call("photoCharge")
        rospy.sleep(0.5)  # 等待图像写入磁盘
        if not response.result:
            rospy.logwarn("Photo service responded with failure.")
            return False
        return True
    except (rospy.ServiceException, rospy.ROSException) as e:
        rospy.logerr(f"Photo service call failed: {e}")
        return False

def get_offset_from_image(image_path, height_m, fov_deg=78.8):
    """
    从拍到的图像中分析红十字相对中心的偏移（单位：米）
    """
    img = cv2.imread(image_path)
    if img is None:
        rospy.logerr("Failed to load image.")
        return None

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    img_h, img_w = img.shape[:2]
    center_x = img_w // 2
    center_y = img_h // 2

    offset_x_px = cx - center_x
    offset_y_px = cy - center_y

    # 粗略换算：像素 → 米
    fov_rad = np.deg2rad(fov_deg)
    meters_per_pixel = (2 * height_m * np.tan(fov_rad / 2)) / img_w

    dx = offset_x_px * meters_per_pixel  # +右，-左
    dy = offset_y_px * meters_per_pixel  # +前，-后（根据机头方向校正）

    return dx, dy

def align_to_red_cross(height_m, tolerance=0.05, max_iter=10):
    """
    自动调整无人机位置直到对准红十字
    """
    img_path = "/home/tta/catkin_ws/src/yolo/src/yolov5/photo_charge.jpg"

    for i in range(max_iter):
        rospy.loginfo(f"[视觉校准] 第 {i+1} 次拍照并校正")

        if not take_photo(img_path):
            rospy.logwarn("拍照失败，跳过本次循环")
            continue

        offset = get_offset_from_image(img_path, height_m)
        if offset is None:
            rospy.logwarn("未检测到红十字")
            continue

        dx, dy = offset
        rospy.loginfo(f"红十字偏移量: dx = {dx:.2f}m, dy = {dy:.2f}m")

        if abs(dx) < tolerance and abs(dy) < tolerance:
            rospy.loginfo("无人机已对准红十字 ✅")
            return True

        nav_to_relative_offset(dx, dy)
        rospy.sleep(1.0)  # 等待无人机移动完成

    rospy.logwarn("未能在规定次数内对准红十字 ❌")
    return False

if __name__ == '__main__':
    rospy.init_node("ep_flight_task")
    flight_takeoffOrLanding(1)
    point = nav_point[0]
    nav_to_goal(point)
    # flight_takeoffOrLanding(2)
    photo_client = rospy.ServiceProxy("photoFlight",photoFlight)
    photo_client.wait_for_service()
    rospy.sleep(0.5)
    photo_response = photo_client.call("photoFlight")
