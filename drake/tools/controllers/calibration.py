import time
import numpy as np
from tools.path.execution import *
from tools.visualization import *

class CalibrationController:
    
    def __init__(self, robot, planner) -> None:
        self.robot = robot
        self.planner = planner
        self.diagram = robot.diagram
        self.context = robot.context
        self.plant = self.diagram.plant()
        self.plant_context = self.plant.GetMyContextFromRoot(self.context)
    
    def translate_probe(self, vector):
        """
        translates the robot. 
        """
        
        joints, transform = self.robot.getTCPPose()
        
        transform[0:3, 3] += vector
        
        path = self.planner.plan_to_tcp_pose(joints, transform)
        
        # Now time parametrize for safety
        joint_trajectory, time_trajectory = time_parametrize_toppra(path, self.plant)
        
        return joint_trajectory, time_trajectory, transform
    
    def move_to(self, transform):
        
        joints, _ = self.robot.getTCPPose()
        
        path = self.planner.plan_to_tcp_pose(joints, transform)
        
        # Now time parametrize for safety
        joint_trajectory, time_trajectory = time_parametrize_toppra(path, self.plant)
        
        return joint_trajectory, time_trajectory
        
    def home_probe(self, direction, speed, max_distance, robot):
        
        # Rescale direction to be a unit vector * max_distance. Then plan to that pose
        direction = direction / np.linalg.norm(direction) * max_distance
        joints, orig_ransform = robot.getTCPPose()
        
        transform = orig_ransform.copy()
        transform[0:3, 3] += direction

        path = self.planner.plan_to_tcp_pose(joints, transform)
        print(len(path))
        
        # Now time parametrize for safety
        joint_trajectory, time_trajectory = time_parametrize_toppra(path, self.plant, joint_speed_limit=0.1)
        
        # First zero
        robot.zeroTFSensor()
        
        # Then execute trajectory until force is detected
        def step_function(t):
            tf = robot.getTFValue()
            force_magnitude = np.sqrt( tf[0]**2 + tf[1]**2 + tf[2]**2 )
            
            if force_magnitude > 0.1:
                _, tcp = robot.getTCPPose()
                print("Force detected! (x: {}, y: {}, z: {})".format(tcp[0, 3], tcp[1, 3], tcp[2, 3]))
                return True
            
            return True
        
        robot.publish_trajectory(joint_trajectory, time_trajectory, step_function)
        
        # Now also go back to the original position\
        # jt, tt = self.move_to(orig_ransform)
        # robot.publish_trajectory(jt, tt)\
        
        # TODO return something