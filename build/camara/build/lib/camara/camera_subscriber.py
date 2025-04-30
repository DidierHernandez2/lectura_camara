#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class SubscriberNodeClass(Node):

    def __init__(self):
        super().__init__("camera_subscriber_node")

        self.bridgeObject =CvBridge()
        self.topicNameFrames="topic_camera_image"
        self.queueSize= 20
        self.subscription=self.create_subscription(msg_type=Image,
                                                   topic=self.topicNameFrames,
                                                   callback=self.listener_callbackFunction,
                                                   qos_profile=self.queueSize)
        self.subscription

    def listener_callbackFunction(self,imageMessage):
        self.get_logger().info("image has reveiced")
        openCVImage=self.bridgeObject.imgmsg_to_cv2(imageMessage)
        cv2.imshow("Camera Video",openCVImage)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    SubscriberNode=SubscriberNodeClass()
    rclpy.spin(SubscriberNode)
    SubscriberNode.destroy_node()
    rclpy.shutdown()

if __name__ =="__main__":
    main()