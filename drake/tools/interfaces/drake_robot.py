from ur_analytic_ik import ur3e, ur5e
from .robot_interface import RobotInterface
import numpy as np
from typing import List, Tuple

from loguru import logger
from pydrake.geometry import Cylinder, Meshcat, Rgba
from pydrake.math import RigidTransform, RotationMatrix
from pydrake.multibody.tree import ModelInstanceIndex
from pydrake.planning import RobotDiagram
from pydrake.systems.framework import Context
from pydrake.trajectories import Trajectory
from tools.visualization import add_meshcat_triad

class DrakeRobot(RobotInterface):
    
    def __init__(self, diagram, context, arm_index, meshcat, tcp_transform, ur_ik):
 
        super().__init__()
        
        self.context = context
        self.plant = diagram.plant()
        self.plant_context = self.plant.GetMyContextFromRoot(context)
        self.diagram = diagram
        self.arm_index = arm_index
        self.meshcat = meshcat
        self.tcp_transform = tcp_transform
        self.ur_ik = ur_ik
    
    def publish_trajectory(
        self,
        joint_trajectory: Trajectory,
        time_trajectory: Trajectory,
        step_function: callable = None,
    ):
        plant = self.diagram.plant()
        plant_context = plant.GetMyContextFromRoot(self.context)

        self.meshcat.StartRecording(set_visualizations_while_recording=False)

        duration = time_trajectory.end_time()
        fps = 60.0
        frames = duration * fps

        for t in np.linspace(0, duration, int(np.ceil(frames))):
            self.context.SetTime(t)
            q = joint_trajectory.value(time_trajectory.value(t).item())
            plant.SetPositions(plant_context, self.arm_index, q[0:6])
            self.diagram.ForcedPublish(self.context)

            if step_function is not None:

                # If step function returns False, then break
                if not step_function(t):
                    break

        self.meshcat.StopRecording()
        self.meshcat.PublishRecording()
    
    def getJointPose(self):
        joints = self.plant.GetPositions(self.plant_context)
        return joints
    
    def setJointPose(self, joints):
      
        self.plant.SetPositions(self.plant_context, joints)
        self.diagram.ForcedPublish(self.context)
        
    def getTFValue(self):
        reaction_forces = self.plant.get_reaction_forces_output_port().Eval(self.plant_context)
        
        tool_reaction_force = reaction_forces[-1]
        
        return np.array(list(tool_reaction_force.translational()) + list(tool_reaction_force.rotational())) - np.array(self.tf_offset)
        
    # def zeroTFSensor(self):
    #     reaction_forces = self.plant.get_reaction_forces_output_port().Eval(self.plant_context)
    #     reaction_forces[-1].SetZero()
         
    def getTCPPose(self):

        joints = self.plant.GetPositions(self.plant_context)
        transform = self.ur_ik.forward_kinematics(joints[0], joints[1], joints[2], joints[3], joints[4], joints[5])
        
        transform = transform.dot(self.tcp_transform)
        
        return joints, transform