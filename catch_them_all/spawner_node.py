import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill
from std_msgs.msg import String
import random
import math
import json

class SpawnerNode(Node):
    def __init__(self):
        super().__init__('spawner_node')
        
        # Service clients
        self.spawn_client = self.create_client(Spawn, '/spawn')
        self.kill_client = self.create_client(Kill, '/kill')
        
        # Publisher to broadcast target position
        self.target_publisher = self.create_publisher(String, '/target_turtle', 10)
        
        self.turtle_counter = 1
        self.current_turtle_name = None
        self.current_x = 0.0
        self.current_y = 0.0
        
        # Wait for services
        self.get_logger().info('Waiting for /spawn service...')
        self.spawn_client.wait_for_service()
        self.get_logger().info('Spawner Node is Ready!')
        
        # Spawn first turtle immediately
        self.spawn_new_turtle()
        
        # Keep republishing target every 1 second
        self.timer = self.create_timer(1.0, self.timer_callback)

    def spawn_new_turtle(self):
        x = random.uniform(1.0, 10.0)
        y = random.uniform(1.0, 10.0)
        theta = random.uniform(0.0, 2 * math.pi)
        name = f'turtle{self.turtle_counter + 1}'
        
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = name
        
        future = self.spawn_client.call_async(request)
        future.add_done_callback(lambda f: self.on_turtle_spawned(f, x, y, name))
        self.turtle_counter += 1

    def on_turtle_spawned(self, future, x, y, name):
        try:
            future.result()
            self.current_turtle_name = name
            self.current_x = x
            self.current_y = y
            self.get_logger().info(f'Spawned {name} at ({x:.2f}, {y:.2f})')
            
            # Broadcast the target info immediately
            msg = String()
            msg.data = json.dumps({'name': name, 'x': x, 'y': y})
            self.target_publisher.publish(msg)
        except Exception as e:
            self.get_logger().error(f'Spawn failed: {e}')

    def timer_callback(self):
        # Keep republishing target so controller never misses it
        if self.current_turtle_name:
            msg = String()
            msg.data = json.dumps({
                'name': self.current_turtle_name,
                'x': self.current_x,
                'y': self.current_y
            })
            self.target_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SpawnerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
