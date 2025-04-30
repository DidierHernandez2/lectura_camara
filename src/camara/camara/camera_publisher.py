#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
# to use sensor data
from sensor_msgs.msg import Image #https://index.ros.org/p/sensor_msgs/#jazzy-assets
import cv2
# To convert ROS2 Image message and OpenCV Images
from cv_bridge import CvBridge #https://index.ros.org/p/cv_bridge/


class PublisherNodeClass(Node):

    def __init__(self):
        super().__init__("camera_publisher_node")

        self.cameraDeviceNumber=0 # select camera
        self.camera=cv2.VideoCapture(self.cameraDeviceNumber)

        self.bridgeObject=CvBridge()
        self.topicNameFrames="topic_camera_image"
        self.queueSize = 20
        self.publisher=self.create_publisher(msg_type=Image,
                                             topic=self.topicNameFrames,
                                             qos_profile=self.queueSize)
        self.periodCommunication=0.02
        self.timer= self.create_timer(timer_period_sec=self.periodCommunication,
                                      callback=self.timer_callbackFunction)

        self.i =0
    
    def timer_callbackFunction(self):
        success, frame = self.camera.read()
        frame=cv2.resize(frame,(820,640),interpolation=cv2.INTER_CUBIC)

        if success==True:
            ROS2ImageMessage=self.bridgeObject.cv2_to_imgmsg(frame)
            self.publisher.publish(ROS2ImageMessage)
        
        self.get_logger().info("Publishing image number %d" % self.i)

        self.i+=1

def main(args=None):
    rclpy.init(args=args)
    publisherObject = PublisherNodeClass()
    rclpy.spin(publisherObject)
    publisherObject.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()