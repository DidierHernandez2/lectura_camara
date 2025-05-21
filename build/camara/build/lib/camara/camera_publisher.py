import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
import cv2

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher_node')

        gst_pipeline = (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), width=240, height=120, format=NV12, framerate=30/1 ! "
            "nvvidconv ! video/x-raw, format=BGRx ! "
            "videoconvert ! video/x-raw, format=BGR ! appsink"
        )

        self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().error("Failed to open CSI camera.")
            exit()

        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=1
        )
        self.publisher = self.create_publisher(Image, "/camera/image_raw", qos_profile)
        self.timer = self.create_timer(1.0 / 30, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Frame capture failed.")
            return

        msg = Image()
        msg.height, msg.width = frame.shape[:2]
        msg.encoding = 'bgr8'
        msg.step = msg.width * 3
        msg.data = frame.tobytes()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_frame"

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
