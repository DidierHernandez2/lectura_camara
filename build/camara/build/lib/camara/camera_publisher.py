import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from builtin_interfaces.msg import Time
import cv2
import numpy as np

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher_node')

        gst_pipeline = (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), width=640, height=480, format=NV12, framerate=60/1 ! "
            "nvvidconv ! video/x-raw, format=BGRx ! "
            "videoconvert ! video/x-raw, format=BGR ! appsink"
        )

        self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().error("❌ No se pudo abrir la cámara CSI con GStreamer.")
            exit()

        self.publisher = self.create_publisher(Image, "/camera/image_raw", 10)
        self.timer = self.create_timer(1.0 / 90, self.timer_callback)

        self.get_logger().info("📷 Nodo de cámara sin cv_bridge activo ✅")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("⚠️ No se pudo capturar el frame.")
            return

        msg = Image()
        msg.height, msg.width = frame.shape[:2]
        msg.encoding = 'bgr8'
        msg.step = msg.width * 3
        msg.data = frame.tobytes()

        now = self.get_clock().now().to_msg()
        msg.header.stamp = now
        msg.header.frame_id = "camera_frame"

        self.publisher.publish(msg)
        self.get_logger().info("📤 Imagen publicada")

def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()