#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, www.guyuehome.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy, cv2, cv_bridge, numpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

class Follower(Node):
        def __init__(self):
            super().__init__('line_follower')
            self.get_logger().info("Start line follower.")

            self.bridge = cv_bridge.CvBridge()

            self.image_sub = self.create_subscription(Image, '/image_raw', self.image_callback, 10)
            self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
            self.pub = self.create_publisher(Image, '/camera/process_image', 10)

            self.twist = Twist()
        def image_callback(self, msg):
            image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lower_yellow = numpy.array([100, 10, 20])       # hsv三通道下限
            upper_yellow = numpy.array([130, 100, 120])     # hsv三通道上限
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)


            h, w, d = image.shape
            search_top = int(h/2)
            search_bot = int(h/2 + 20)
            mask[0:search_top, 0:w] = 0
            mask[search_bot:h, 0:w] = 0

            kernel = numpy.ones((3,3),numpy.uint8)    # 腐蚀用的卷积核为3*3
            mask = cv2.erode(mask, kernel, iterations=1)    # 腐蚀操作只需进行一次

            M = cv2.moments(mask)

            if M['m00'] > 0:        # 当视野中存在黑线时
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.circle(image, (cx, cy), 20, (0,0,255), -1)
                err = cx - w/2
                if abs(err)<60:     # 偏差值较小时，即直线行驶时
                    self.twist.linear.x = 0.12
                    self.twist.angular.z = -float(err) / 700
                    self.cmd_vel_pub.publish(self.twist)
                else:               # 偏差值较大时，即需要调整方向时
                    self.twist.linear.x = 0.07
                    self.twist.angular.z = -float(err) / 500
                    self.cmd_vel_pub.publish(self.twist)
            else:                   # 当视野中不存在黑线时
                self.twist.linear.x = -0.07
                self.twist.angular.z = 0.0
                self.cmd_vel_pub.publish(self.twist)

            self.pub.publish(self.bridge.cv2_to_imgmsg(image, 'bgr8'))

def main(args=None):
        rclpy.init(args=args)
        follower = Follower()
        rclpy.spin(follower)
        follower.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
        main()