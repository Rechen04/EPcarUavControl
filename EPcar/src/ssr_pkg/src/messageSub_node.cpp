#include<ros/ros.h>
#include <std_msgs/String.h>

void message_callback(std_msgs::String msg)
{
    ROS_INFO(msg.data.c_str());
}

int main(int argc, char *argv[])
{
    ros::init(argc, argv, "messageSub_node");

    ros::NodeHandle nh;
    ros::Subscriber sub = nh.subscribe("qun",10, message_callback);

    while(ros::ok())
    {
        ros::spinOnce();
    }
    return 0;
}
