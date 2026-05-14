import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import String
from turtlesim.srv import Kill
import math
import json

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')

        # Subscribe to main turtle's position
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)

        # Subscribe to target turtle info from spawner
        self.target_subscriber = self.create_subscription(
            String, '/target_turtle', self.target_callback, 10)

        # Publisher to move the main turtle
        self.cmd_publisher = self.create_publisher(
            Twist, '/turtle1/cmd_vel', 10)

        # Kill service to remove caught turtle
        self.kill_client = self.create_client(Kill, '/kill')

        self.my_pose = None
        self.target = None
        self.catching = False

        # Control loop runs 10 times per second
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info('Controller Node is Ready! 🎯')

    def pose_callback(self, msg):
        self.my_pose = msg

    def target_callback(self, msg):
        data = json.loads(msg.data)
        self.target = data
        self.catching = False
        self.get_logger().info(
            f"New target: {data['name']} at ({data['x']:.2f}, {data['y']:.2f})")

    def control_loop(self):
        # Wait until we have both position and target
        if self.my_pose is None or self.target is None:
            return

        # Calculate distance to target
        dx = self.target['x'] - self.my_pose.x
        dy = self.target['y'] - self.my_pose.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # If close enough → turtle is caught!
        if distance < 0.5:
            self.get_logger().info(
                f"✅ Caught {self.target['name']}!")
            self.kill_turtle(self.target['name'])
            self.target = None
            self.stop_turtle()
            return

        # P Control — calculate angle to target
        angle_to_target = math.atan2(dy, dx)
        angle_error = angle_to_target - self.my_pose.theta

        # Normalize angle to [-pi, pi]
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi

        # Create movement command
        cmd = Twist()
        cmd.linear.x = 1.5 * distance      # Speed proportional to distance
        cmd.angular.z = 6.0 * angle_error  # Turn proportional to angle error
        self.cmd_publisher.publish(cmd)

    def stop_turtle(self):
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.cmd_publisher.publish(cmd)

    def kill_turtle(self, name):
        request = Kill.Request()
        request.name = name
        self.kill_client.call_async(request)

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
