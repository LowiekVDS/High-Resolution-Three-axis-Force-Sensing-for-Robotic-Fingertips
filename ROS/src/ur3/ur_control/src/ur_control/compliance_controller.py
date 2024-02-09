# Copyright (c) 2018-2021, Cristian Beltran.  All rights reserved.
#
# Cristian Beltran and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from Cristian Beltran is strictly prohibited.

import rospy
import numpy as np
import types

from ur_control.arm import Arm
from ur_control import transformations, spalg, utils
from ur_control.constants import ExecutionResult


# Returns the new average
# after including x
def getAvg(prev_avg, x, n):
    return ((prev_avg *
             n + x) /
            (n + 1))


class CompliantController(Arm):
    def __init__(self,
                 model,
                 **kwargs):
        """ Compliant controllertrajectory_time_compensation
        """
        Arm.__init__(self, **kwargs)

        self.model = model

        # read publish rate if it does exist, otherwise set publish rate
        js_rate = utils.read_parameter(self.ns + 'joint_state_controller/publish_rate', 500.0)
        self.rate = rospy.Rate(js_rate)

    def set_hybrid_control_trajectory(self, trajectory, max_force_torque, timeout=5.0,
                                      stop_on_target_force=False, termination_criteria=None,
                                      displacement_epsilon=0.002, check_displacement_time=2.0,
                                      verbose=True, debug=False, time_compensation=True):
        """ Move the robot according to a hybrid controller model
            trajectory: array[array[7]] or array[7], can define a single target pose or a trajectory of multiple poses.
            model: force control model, see hybrid_controller.py 
            max_force_torque: array[6], max force/torque allowed before stopping controller
            timeout: float, maximum duration of controller's operation
            stop_on_target_force: bool: stop once the model's target force has been achieved, stopping controller when all non-zero target forces/torques are reached
            termination_criteria: lambda/function, special termination criteria based on current pose of the robot w.r.t the robot's base
            displacement_epsilon: float,  minimum displacement necessary to consider the robot in standby 
            check_displacement_time: float,  time interval to check whether the displacement has been larger than displacement_epsilon
        """

        reduced_speed = np.deg2rad([100, 100, 100, 250, 250, 250])

        xb = self.end_effector()
        failure_counter = 0

        ptp_index = 0
        q_last = self.joint_angles()

        trajectory_time_compensation = self.model.dt * 10. if time_compensation else 0.0 # Hyperparameter

        if trajectory.ndim == 1:  # just one point
            ptp_timeout = timeout
            self.model.set_goals(position=trajectory)
        else:  # trajectory
            ptp_timeout = timeout / float(len(trajectory)) - trajectory_time_compensation
            self.model.set_goals(position=trajectory[ptp_index])

        log = {ExecutionResult.SPEED_LIMIT_EXCEEDED: 0, ExecutionResult.IK_NOT_FOUND: 0}

        result = ExecutionResult.DONE

        standby_timer = rospy.get_time()
        standby_last_pose = self.end_effector()
        standby = False

        if debug:
            avg_step_time = 0.0
            step_num = 0

        # Timeout for motion
        initime = rospy.get_time()
        sub_inittime = rospy.get_time()
        while not rospy.is_shutdown() \
                and (rospy.get_time() - initime) < timeout:
            if debug:
                start_time = rospy.get_time()

            # Transform wrench to the base_link frame
            Wb = self.get_wrench(base_frame_control=True)
            # Current position in task-space
            xb = self.end_effector()

            if termination_criteria is not None:
                assert isinstance(termination_criteria, types.LambdaType), "Invalid termination criteria, expecting lambda/function with one argument[current pose array[7]]"
                if termination_criteria(xb, standby):
                    rospy.loginfo("Termination criteria returned True, stopping force control")
                    result = ExecutionResult.TERMINATION_CRITERIA
                    break

            if (rospy.get_time() - sub_inittime) > ptp_timeout:
                sub_inittime = rospy.get_time()
                ptp_index += 1
                if ptp_index >= len(trajectory):
                    self.model.set_goals(position=trajectory[-1])
                elif not trajectory.ndim == 1:  # For some reason the timeout validation is not robust enough
                    self.model.set_goals(position=trajectory[ptp_index])

            Fb = -1 * Wb # Move in the opposite direction of the force
            if stop_on_target_force and np.all(np.abs(Fb)[self.model.target_force != 0] > np.abs(self.model.target_force)[self.model.target_force != 0]):
                rospy.loginfo('Target F/T reached {}'.format(np.round(Wb, 3)) + ' Stopping!')
                self.set_target_pose(pose=xb, target_time=self.model.dt)
                result = ExecutionResult.STOP_ON_TARGET_FORCE
                break

            # Safety limits: max force
            if np.any(np.abs(Wb) > max_force_torque):
                rospy.logerr('Maximum force/torque exceeded {}'.format(np.round(Wb, 3)))
                self.set_target_pose(pose=xb, target_time=self.model.dt)
                result = ExecutionResult.FORCE_TORQUE_EXCEEDED
                break

            # Current Force in task-space
            dxf = self.model.control_position_orientation(Fb, xb)  # angular velocity

            xc = transformations.pose_from_angular_velocity(xb, dxf, dt=self.model.dt)

            # Avoid extra acceleration when a point failed due to IK or other violation
            # So, this corrects the allowed time for the next point
            dt = self.model.dt * (failure_counter+1)

            result = self._actuate(xc, dt, q_last, reduced_speed)


            if result != ExecutionResult.DONE:
                failure_counter += 1
                if result == ExecutionResult.IK_NOT_FOUND:
                    log[ExecutionResult.IK_NOT_FOUND] += 1
                if result == ExecutionResult.SPEED_LIMIT_EXCEEDED:
                    log[ExecutionResult.SPEED_LIMIT_EXCEEDED] += 1
                continue  # Don't wait since there is not motion
            else:
                failure_counter = 0
                q_last = self.joint_angles()

            # Compensate the time allocated to the next command when there are failures
            # Especially important for following a motion trajectory
            for _ in range(failure_counter+1):
                self.rate.sleep()

            standby_time = (rospy.get_time() - standby_timer)
            if standby_time > check_displacement_time:
                displacement_dt = np.linalg.norm(standby_last_pose[:3] - self.end_effector()[:3])
                standby = displacement_dt < displacement_epsilon
                if standby:
                    rospy.logwarn("No more than %s displacement in the last %s seconds" % (round(displacement_dt, 6), check_displacement_time))
                last_pose = self.end_effector()
                standby_timer = rospy.get_time()
                standby_last_pose = self.end_effector()

            if debug:
                step_time = rospy.get_time() - start_time
                avg_step_time = step_time if avg_step_time == 0 else getAvg(avg_step_time, step_time, step_num)
                step_num += 1

        if verbose:
            rospy.logwarn("Total # of commands ignored: %s" % log)
        return result

    def _actuate(self, pose, dt, q_last, reduced_speed, attempts=5):
        """
            Evaluate IK solution several times if it fails.
            Similarly, evaluate that the IK solution is viable
        """
        result = None
        q = self.inverse_kinematics(pose, attempts=0, verbose=False)
        if q is None:
            if attempts > 0:
                return self._actuate(pose, dt, q_last, reduced_speed, attempts-1)
            rospy.logwarn("IK not found")
            result = ExecutionResult.IK_NOT_FOUND
        else:
            q_speed = (q_last - q)/dt
            if np.any(np.abs(q_speed) > reduced_speed):
                if attempts > 0:
                    return self._actuate(pose, dt, q_last, reduced_speed, attempts-1)
                rospy.logwarn_once("Exceeded reduced max speed %s deg/s, Ignoring command" % np.round(np.rad2deg(q_speed), 0))
                result = ExecutionResult.SPEED_LIMIT_EXCEEDED
            else:
                result = self.set_joint_positions(positions=q, target_time=dt)
                self.rate.sleep()
        return result

    # TODO(cambel): organize this code to avoid this repetition of code
    def set_hybrid_control(self, model, max_force_torque, timeout=5.0, stop_on_target_force=False):
        """ Move the robot according to a hybrid controller model"""

        reduced_speed = np.deg2rad([100, 100, 100, 150, 150, 150])
        q_last = self.joint_angles()

        # Timeout for motion
        initime = rospy.get_time()
        xb = self.end_effector()
        failure_counter = 0

        while not rospy.is_shutdown() \
                and (rospy.get_time() - initime) < timeout:

            # Transform wrench to the base_link frame
            Wb = self.get_wrench()

            # Current Force in task-space
            Fb = -1 * Wb
            # Safety limits: max force
            if np.any(np.abs(Fb) > max_force_torque):
                rospy.logerr('Maximum force/torque exceeded {}'.format(np.round(Wb, 3)))
                self.set_target_pose(pose=xb, target_time=model.dt)
                return ExecutionResult.FORCE_TORQUE_EXCEEDED

            if stop_on_target_force and np.any(np.abs(Fb)[model.target_force != 0] > model.target_force[model.target_force != 0]):
                rospy.loginfo('Target F/T reached {}'.format(np.round(Wb, 3)) + ' Stopping!')
                self.set_target_pose(pose=xb, target_time=model.dt)
                return ExecutionResult.STOP_ON_TARGET_FORCE

            # Current position in task-space
            xb = self.end_effector()

            dxf = model.control_position_orientation(Fb, xb)  # angular velocity

            # Limit linear/angular velocity
            dxf[:3] = np.clip(dxf[:3], -0.5, 0.5)
            dxf[3:] = np.clip(dxf[3:], -5., 5.)

            xc = transformations.pose_from_angular_velocity(xb, dxf, dt=model.dt)

            # Avoid extra acceleration when a point failed due to IK or other violation
            # So, this corrects the allowed time for the next point
            dt = model.dt * (failure_counter+1)

            q = self.inverse_kinematics(xc)
            if q is None:
                rospy.logwarn("IK not found")
                result = ExecutionResult.IK_NOT_FOUND
            else:
                q_speed = (q_last - q)/dt
                if np.any(np.abs(q_speed) > reduced_speed):
                    rospy.logwarn("Exceeded reduced max speed %s deg/s, Ignoring command" % np.round(np.rad2deg(q_speed), 0))
                    result = ExecutionResult.SPEED_LIMIT_EXCEEDED
                else:
                    result = self.set_joint_positions(positions=q, target_time=dt)

            if result != ExecutionResult.DONE:
                failure_counter += 1
                continue  # Don't wait since there is not motion
            else:
                failure_counter = 0

            # Compensate the time allocated to the next command when there are failures
            for _ in range(failure_counter+1):
                self.rate.sleep()

            q_last = self.joint_angles()
        return ExecutionResult.DONE
