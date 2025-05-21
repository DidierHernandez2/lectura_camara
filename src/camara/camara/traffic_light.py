import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String
import numpy as np
import cv2

# Rangos HSV: rojo y verde ya ok, amarillo ampliado
R1 = ([170, 200, 200], [180, 255, 255])
R2 = ([  0, 200, 200], [ 10, 255, 255])
Y  = ([ 15,  80,  80], [ 45, 255, 255])  # amarillo ampliado
G  = ([ 45,  50,  50], [ 85, 255, 255])

class TrafficLightDetector(Node):
    def __init__(self):
        super().__init__('traffic_light')
        qos = QoSProfile(depth=1,
                         reliability=QoSReliabilityPolicy.BEST_EFFORT)
        self.sub = self.create_subscription(
            Image, '/camera/image_raw',
            self.cb_image, qos)
        self.light_pub = self.create_publisher(String, '/light', 10)
        self.get_logger().info(
            "TrafficLightDetector listo: amarillo con rango ampliado")

    def cb_image(self, msg: Image):
        h, w = msg.height, msg.width
        frame = np.frombuffer(msg.data, np.uint8).reshape(h, w, 3)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Máscara rojo
        l1, u1 = map(np.array, R1)
        l2, u2 = map(np.array, R2)
        m1 = cv2.inRange(hsv, l1, u1)
        m2 = cv2.inRange(hsv, l2, u2)
        red_mask = cv2.bitwise_or(m1, m2)

        # Máscara amarillo
        ly, uy = map(np.array, Y)
        yellow_mask = cv2.inRange(hsv, ly, uy)

        # Máscara verde
        lg, ug = map(np.array, G)
        green_mask = cv2.inRange(hsv, lg, ug)

        # Limpieza morfológica ligera
        kernel = np.ones((3,3), np.uint8)
        red_mask    = cv2.erode(cv2.dilate(red_mask,    kernel, iterations=1), kernel, iterations=1)
        yellow_mask = cv2.erode(cv2.dilate(yellow_mask, kernel, iterations=1), kernel, iterations=1)
        green_mask  = cv2.erode(cv2.dilate(green_mask,  kernel, iterations=1), kernel, iterations=1)

        # Conteo de píxeles
        r_count = int(cv2.countNonZero(red_mask))
        y_count = int(cv2.countNonZero(yellow_mask))
        g_count = int(cv2.countNonZero(green_mask))

        # Selección de color dominante (o green si empate/no detección)
        if   r_count > y_count and r_count > g_count:
            detected = 'red'
        elif y_count > r_count and y_count > g_count:
            detected = 'yellow'
        elif g_count > r_count and g_count > y_count:
            detected = 'green'
        else:
            detected = 'green'  # por defecto green

        # Publica
        msg_out = String()
        msg_out.data = detected
        self.light_pub.publish(msg_out)

        # Mostrar resultados
        res_r = cv2.bitwise_and(frame, frame, mask=red_mask)
        res_y = cv2.bitwise_and(frame, frame, mask=yellow_mask)
        res_g = cv2.bitwise_and(frame, frame, mask=green_mask)
        cv2.imshow('Original', frame)
        cv2.imshow('Rojo',     res_r)
        cv2.imshow('Amarillo',  res_y)
        cv2.imshow('Verde',     res_g)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = TrafficLightDetector()
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
