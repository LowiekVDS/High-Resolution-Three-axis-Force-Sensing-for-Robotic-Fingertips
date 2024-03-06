
from tools.tf_reader import *
from tools.sensor_reader import *
from threading import Thread
from queue import Queue

class MeasuringInterface:
  
    def __init__(self, controller) -> None:
        self.tf_q = Queue()
        self.sensor_q = Queue()
        self.controller = controller

    def start_measuring(self, name):
        
        self.tf_q = Queue()
        self.sensor_q = Queue()

        # Start sensor readers
        self.tf_reader_thread = Thread(target=read_and_publish_tf_sensor_sync, args=(self.controller, name, self.tf_q, ))
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
              