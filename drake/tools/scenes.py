from typing import Tuple

import airo_models
import numpy as np
from tools.urdf.robotiq import create_static_robotiq_2f_85_urdf
from pydrake.math import RigidTransform, RollPitchYaw
from pydrake.multibody.tree import ModelInstanceIndex
from pydrake.planning import RobotDiagramBuilder

X_URTOOL0_ROBOTIQ = RigidTransform(rpy=RollPitchYaw([0, 0, np.pi / 2]), p=[0, 0, 0])

def add_ur3e_and_table_to_builder(
    robot_diagram_builder: RobotDiagramBuilder,
) -> Tuple[ModelInstanceIndex, ModelInstanceIndex]:
    plant = robot_diagram_builder.plant()
    parser = robot_diagram_builder.parser()
    parser.SetAutoRenaming(True)

    # Load URDF files
    ur5e_urdf_path = airo_models.get_urdf_path("ur3e")
    robotiq_urdf_path = create_static_robotiq_2f_85_urdf()

    table_thickness = 0.2
    table_urdf_path = airo_models.box_urdf_path((2.0, 2.4, table_thickness), "table")

    arm_index = parser.AddModels(ur5e_urdf_path)[0]
    gripper_index = parser.AddModels(robotiq_urdf_path)[0]
    table_index = parser.AddModels(table_urdf_path)[0]

    # Weld some frames together
    world_frame = plant.world_frame()
    table_frame = plant.GetFrameByName("base_link", table_index)
    arm_frame = plant.GetFrameByName("base_link", arm_index)
    arm_tool_frame = plant.GetFrameByName("tool0", arm_index)
    gripper_frame = plant.GetFrameByName("base_link", gripper_index)

    arm_transform = RigidTransform(rpy=RollPitchYaw([0, 0, np.pi]), p=[0, 0, 0])
    table_transform = RigidTransform(p=[0, 0, -table_thickness / 2])

    plant.WeldFrames(world_frame, arm_frame, arm_transform)
    plant.WeldFrames(arm_tool_frame, gripper_frame, X_URTOOL0_ROBOTIQ)
    plant.WeldFrames(world_frame, table_frame, table_transform)

    return arm_index, gripper_index

def add_probing_tool_to_builder():
    
    pass