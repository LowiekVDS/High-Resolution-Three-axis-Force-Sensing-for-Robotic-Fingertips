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
        
        print(transform)
        
        transform[0:3, 3] += vector
        
        path = self.planner.plan_to_tcp_pose(joints, transform)
        
        # Now time parametrize for safety
        joint_trajectory, time_trajectory = time_parametrize_toppra(path, self.plant)
        
        return joint_trajectory, time_trajectory, transform
        
    def home_probe(direction, speed, max_distance, robot):
        
        # Rescale direction to be a unit vector * max_distance. Then plan to that pose
        direction = direction / np.linalg.norm(direction) * max_distance
        joints, transform = robot.getTCPPose()
        print(transform)
        transform[0:3, 3] += direction
        print(transform)
        path = planner.plan_to_tcp_pose(joints, transform)
        
        # First zero
        robot.zeroTFSensor()
        
        # Then move in direction until force is detected
        for joint_config in path:
            
            # Set the joints
            robot.setJointPose(joint_config)
            
            # Then check for reaction force
            tf = robot.getTFValue()
            force_magnitude = np.sqrt( tf[0]**2 + tf[1]**2 + tf[2]**2 )
            
            if force_magnitude > 0.1:
                _, tcp = robot.getTCPPose()
                print("Force detected! (x: {}, y: {}, z: {})".format(tcp[0, 3], tcp[1, 3], tcp[2, 3]))
                
                # Now also go back to the original position
                transform[0:3, 3] -= direction
                translate_probe(transform[0:3, 3] - tcp[0:3, 3], speed, robot)
                
                return True, tcp[0:3, 3]
            
            time.sleep(0.05)
            
        # Now also go back to the original position
        transform[0:3, 3] -= direction
        translate_probe(transform[0:3, 3] - tcp[0:3, 3], speed, robot)
                
        return False, None
        