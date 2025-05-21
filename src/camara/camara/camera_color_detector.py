import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
import numpy as np
import cv2

# límites HSV para rojo (dos rangos) y azul
R1 = ([160,  95, 130], [179, 255, 255])
R2 = ([  0,  95, 130], [  5, 255, 255])
B  = ([ 95,  90,  90], [110, 255, 255])

class CameraColorDetector(Node):
    def __init__(self):
        super().__init__('camera_color_detector')
        qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.BEST_EFFORT
        )
        self.sub = self.create_subscription(
            Image, '/camera/image_raw',
            self.cb_image, qos)
        self.get_logger().info("ColorDetector listo: mostrando rojo/azul con BEST_EFFORT QoS")

    def cb_image(self, msg: Image):
        h, w = msg.height, msg.width
        frame = np.frombuffer(msg.data, np.uint8).reshape(h, w, 3)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower1, upper1 = map(np.array, R1)
        lower2, upper2 = map(np.array, R2)
        m1 = cv2.inRange(hsv, lower1, upper1)
        m2 = cv2.inRange(hsv, lower2, upper2)
        red_mask = cv2.bitwise_or(m1, m2)
        red_res  = cv2.bitwise_and(frame, frame, mask=red_mask)

        lowerb, upperb = map(np.array, B)
        blue_mask = cv2.inRange(hsv, lowerb, upperb)
        blue_res  = cv2.bitwise_and(frame, frame, mask=blue_mask)

        kernel = np.ones((5,5), np.uint8)
        red_res  = cv2.erode(cv2.dilate(red_res, kernel, iterations=2), kernel, iterations=2)
        blue_res = cv2.erode(cv2.dilate(blue_res, kernel, iterations=2), kernel, iterations=2)

        cv2.imshow('Original',    frame)
        cv2.imshow('Red Mask',    red_mask)
        cv2.imshow('Red Result',  red_res)
        cv2.imshow('Blue Mask',   blue_mask)
        cv2.imshow('Blue Result', blue_res)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = CameraColorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
