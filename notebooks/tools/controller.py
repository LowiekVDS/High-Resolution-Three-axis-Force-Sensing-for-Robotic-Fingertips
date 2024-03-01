import rtde_control, rtde_receive
import numpy as np

class CalibrationController:
  
  def __init__(self, rtde_r, rtde_c):
    self.rtde_r = rtde_r
    self.rtde_c = rtde_c
    

  def find_contact_point(self, xyz, speed = 0.01):
    
    # Normalize vector and then scale with speed
    direction = xyz / np.linalg.norm(xyz) * speed
    direction = np.pad(direction, (0, 3))

    self.rtde_c.moveUntilContact(direction)
    
    position = self.rtde_r.getActualTCPPose()[0:3]

    return position

  def move_absolute(self, xyz, velocity = 0.1, acceleration = 0.5):
    tcp_pose_0 = self.rtde_r.getActualTCPPose()
    tcp_pose_1 = np.array(tcp_pose_0.copy())
    tcp_pose_1[0:3] = xyz
  
    path = [list(tcp_pose_0), list(tcp_pose_1)]

    # Append speeds, accelerations and blends
    for p in path:
      p.append(velocity)
      p.append(acceleration) # acceleration
      p.append(0.0) # blend

    # Send a linear path with blending in between - (currently uses separate script)
    self.rtde_c.moveL(path)
    
    return self.rtde_r.getActualTCPPose()[0:3] 

  def move_relative(self, dxyz, velocity = 0.1, acceleration = 0.5):
    tcp_pose_0 = self.rtde_r.getActualTCPPose()
    tcp_pose_1 = np.array(tcp_pose_0.copy())
    tcp_pose_1 += np.pad(dxyz, (0, 3))
  
    path = [list(tcp_pose_0), list(tcp_pose_1)]

    # Append speeds, accelerations and blends
    for p in path:
      p.append(velocity) # velocity
      p.append(acceleration) # acceleration
      p.append(0.0) # blend

    # Send a linear path with blending in between - (currently uses separate script)
    self.rtde_c.moveL(path)
    
    return self.rtde_r.getActualTCPPose()[0:3] 
    # rtde_c.stopScript()
