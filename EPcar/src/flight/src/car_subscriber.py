# car_subscriber.py
import rospy
from std_msgs.msg import String
import subprocess

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + " I heard %s", data.data)
    if data.data == "Start":
        subprocess.call(["python", "/path/to/your_script.py"])

def subscriber():
    rospy.init_node('car_subscriber', anonymous=True)
    rospy.Subscriber('drone_signal', String, callback)
    rospy.spin()

if __name__ == '__main__':
    subscriber()
