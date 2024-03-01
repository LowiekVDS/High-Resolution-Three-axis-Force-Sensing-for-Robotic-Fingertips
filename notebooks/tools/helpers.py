import numpy as np

def get_square_corners(a, b, c, width_x, width_y, tool_width):
    c1 = (a[0] - c[0]) * (a[0] - b[0]) + (a[1] - c[1]) * (a[1] - b[1])
    c2 = (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])
    t = c1 / c2
    
    corner1 = [a[0] + (b[0] - a[0])*t, a[1] + t * (b[1] - a[1])]
    
    dx1 = a[0] - corner1[0]
    dy1 = a[1] - corner1[1]
    norm = np.sqrt(dx1**2 + dy1**2)
    dx1 /= norm
    dy1 /= norm
    
    dx2 = c[0] - corner1[0]
    dy2 = c[1] - corner1[1]
    norm = np.sqrt(dx2**2 + dy2**2)
    dx2 /= norm
    dy2 /= norm
    
    # Correct corners for tool width
    corner1[0] += dx2 * tool_width
    corner1[1] += dy1 * tool_width
    
    corner2 = [corner1[0] + dx1 * width_x, corner1[1] + dy1 * width_y]
    corner3 = [corner1[0] + (dx1 + dx2) * width_x, corner1[1] + (dy1 + dy2) * width_y]    
    corner4 = [corner1[0] + dx2 * width_x, corner1[1] + dy2 * width_y]
  
    return np.array([corner1, corner2, corner3, corner4]), ((dx1, dy1), (dx2, dy2))
  
def calculate_grid_on_square(corners, grid_size):
    dx1, dy1 = corners[1] - corners[0]
    dx2, dy2 = corners[3] - corners[0]
    dx1 /= grid_size
    dy1 /= grid_size
    dx2 /= grid_size
    dy2 /= grid_size
    
    start_point = corners[0] + np.array([(dx1 + dx2) / 2, (dy1 + dy2) / 2])
    
    grid = np.zeros((grid_size, grid_size, 2))
    for i in range(grid_size):
        for j in range(grid_size):
            grid[i, j] = start_point + np.array([i * dx1 + j * dx2, i * dy1 + j * dy2])
    
    return grid

from tools.tf_reader import *
from tools.sensor_reader import *
from threading import Thread
from queue import Queue

class MeasuringInterface:
  
    def __init__(self, rtde_r) -> None:
        self.tf_q = Queue()
        self.sensor_q = Queue()
        self.rtde_r = rtde_r

    def start_measuring(self, name):
        
        self.tf_q = Queue()
        self.sensor_q = Queue()

        # Start sensor readers
        self.tf_reader_thread = Thread(target=read_and_publish_tf_sensor_sync, args=(self.rtde_r, name, self.tf_q, ))
        self.tf_reader_thread.start()

        self.sensor_reader_thread = Thread(target=read_and_publish_sensor_sync, args=(name, self.sensor_q, ))
        self.sensor_reader_thread.start()
      
    def stop_measuring(self):
        self.tf_q.put(None)
        self.sensor_q.put(None)
        
        self.sensor_reader_thread.join()
        self.tf_reader_thread.join()
        
        self.tf_q.get()
        self.sensor_q.get()
              