import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

class CameraSubscriber(Node):
    def _init_(self):
        super()._init_('camera_subscriber_node')

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
        self.get_logger().info("📥 Suscrito a /camera/image_raw con Best Effort")

    def listener_callback(self, msg):
        try:
            frame = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height, msg.width, 3))
            cv2.imshow("🖼️ Imagen recibida", frame)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f"❌ Error al procesar imagen: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = CameraSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if _name_ == 'main':
    main()