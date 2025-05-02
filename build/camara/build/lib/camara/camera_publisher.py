#!/usr/bin/env python3
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
import numpy as np

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher_node')

        # Construye el pipeline GStreamer (60 fps, resolución 640×480)
        gst_pipeline = (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM),width=640,height=480,format=NV12,framerate=60/1 ! "
            "videorate ! video/x-raw,framerate=60/1 ! "
            "nvvidconv ! video/x-raw,format=BGRx ! "
            "videoconvert ! video/x-raw,format=BGR ! appsink"
        )

        # Abre la cámara CSI
        self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            self.get_logger().error("❌ No se pudo abrir la cámara CSI con GStreamer.")
            rclpy.shutdown()
            return

        # Publisher de Image
        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.get_logger().info("📷 Nodo de cámara iniciado (60 Hz)")

        # Bandera para parar el hilo y Rate a 60 Hz
        self._stop = False
        self._rate = self.create_rate(60)

        # Lanzar hilo de captura continua
        threading.Thread(target=self._spin_read, daemon=True).start()

    def _spin_read(self):
        while rclpy.ok() and not self._stop:
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().warn("⚠️ No se pudo capturar el frame.")
            else:
                msg = Image()
                msg.height, msg.width = frame.shape[:2]
                msg.encoding = 'bgr8'
                msg.step = msg.width * 3
                msg.data = frame.tobytes()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = "camera_frame"
                self.publisher.publish(msg)
            # Esperar al siguiente ciclo (60 Hz)
            self._rate.sleep()

    def destroy_node(self):
        # Señalar al hilo que pare y liberar recursos
        self._stop = True
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
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
