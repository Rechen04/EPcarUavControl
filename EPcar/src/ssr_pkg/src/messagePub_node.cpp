#include <ros/ros.h>
#include <std_msgs/String.h>

int main(int argc, char *argv[])
{
    ros::init(argc, argv, "messagePub_node");
    printf("Hello world!");

    ros::NodeHandle nh;
    ros::Publisher pub = nh.advertise<std_msgs::String>("qun",10);
    ros::Rate loop_rate(10);

    while(ros::ok())
    {
        printf("message!!!\n");
        std_msgs::String msg;
        msg.data = "message data";
        pub.publish(msg);
        loop_rate.sleep();
    }
    return 0;
}
