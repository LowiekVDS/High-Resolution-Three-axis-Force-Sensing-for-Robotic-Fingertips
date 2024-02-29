from typing import List, Tuple

import numpy as np
from airo_typing import JointConfigurationType
from pydrake.multibody.optimization import CalcGridPointsOptions, Toppra
from pydrake.multibody.plant import MultibodyPlant
from pydrake.trajectories import PiecewisePolynomial, Trajectory
from tools.interfaces.robot_interface import RobotInterface

def time_parametrize_toppra(
    arm_joint_path: List[Tuple[JointConfigurationType, JointConfigurationType]],
    plant: MultibodyPlant,
    joint_speed_limit: float = 2.0,  # Max 180 degrees/s ~ 3.14 rad/s
    joint_acceleration_limit: float = 4.0,  # UR recommends < 800 degrees/s^2 ~ 13.9 rad/s^2
) -> Tuple[Trajectory, Trajectory]:
    """Time-parametrize a dual arm joint path using TOPP-RA with a Drake plant, takes about ~ 35ms."""
    n_dofs = 6
    path = np.array(arm_joint_path).reshape(-1, n_dofs)  # should be e.g. (500, 12)

    times_dummy = np.linspace(0.0, 1.0, len(path))

    # TODO: maybe we always want FirstOrderHold, because that's what e.g. OMPL assumes between configs?
    if len(path) >= 3:
        joint_trajectory = PiecewisePolynomial.CubicWithContinuousSecondDerivatives(times_dummy, path.T)
    else:
        joint_trajectory = PiecewisePolynomial.FirstOrderHold(times_dummy, path.T)

    gridpoints = Toppra.CalcGridPoints(joint_trajectory, CalcGridPointsOptions())
    toppra = Toppra(joint_trajectory, plant, gridpoints)
    toppra.AddJointAccelerationLimit([-joint_acceleration_limit] * n_dofs, [joint_acceleration_limit] * n_dofs)
    toppra.AddJointVelocityLimit([-joint_speed_limit] * n_dofs, [joint_speed_limit] * n_dofs)
    time_trajectory = toppra.SolvePathParameterization()

    return joint_trajectory, time_trajectory


def calculate_path_array_duration(path_array: np.ndarray, max_allowed_speed: float = 0.5) -> float:
    velocities = np.diff(path_array, axis=0)

    v_max = abs(velocities.max())
    v_min = abs(velocities.min())
    v_max_abs = max(abs(v_min), abs(v_max))

    duration_for_1rads = len(path_array) * v_max_abs

    duration = duration_for_1rads / max_allowed_speed
    return duration


def calculate_dual_path_duration(path, max_allowed_speed: float = 0.5) -> float:
    path_array = np.array(path).reshape(-1, 12)
    return calculate_path_array_duration(path_array, max_allowed_speed)


def interpolate_linearly(a, b, t):
    return a + t * (b - a)


def resample_path(path, n):
    m = len(path)
    path_new = []

    # Prevent division by zero
    if n == 1:
        return [path[-1]]

    # example if m = 2 and n = 3, then i = 0, 1, 2 must produce j = 0, 0.5, 1, this i_to_j = 1/2 = (2-1)/(3-1)
    i_to_j = (m - 1) / (n - 1)

    for i in range(n):
        j_float = i_to_j * i
        j_fractional, j_integral = np.modf(j_float)

        j = int(j_integral)
        j_next = min(j + 1, m - 1)  # If j+1 would be m, then clamping to m-1 will give last element which is desired

        a = path[j]
        b = path[j_next]

        v = interpolate_linearly(a, b, j_fractional)
        path_new.append(v)

    return path_new


def ensure_arm_at_joint_configuration(arm: RobotInterface, joints, tolerance=0.1) -> None:

    current_joints = arm.getJointPose()

    distance = np.linalg.norm(current_joints - joints)

    if distance > tolerance:
        raise ValueError(
            f"Arm is at {current_joints} but should be at {joints}, distance: {distance}"
        )