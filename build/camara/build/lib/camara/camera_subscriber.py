import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
import threading

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber_node')

        qos_best_effort = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            qos_best_effort
        )

        self.get_logger().info("Subscribed to /camera/image_raw with Best Effort QoS")
        self.frame = None
        self.lock = threading.Lock()
        self.display_thread = threading.Thread(target=self.display_frame)
        self.display_thread.start()

    def listener_callback(self, msg):
        try:
            frame = np.frombuffer(msg.data, dtype=np.uint8).reshape((120,240 , 3))
            with self.lock:
                self.frame = frame
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

    def display_frame(self):
        while rclpy.ok():
            if self.frame is not None:
                with self.lock:
                    cv2.imshow("Received Image", self.frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    node = CameraSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
