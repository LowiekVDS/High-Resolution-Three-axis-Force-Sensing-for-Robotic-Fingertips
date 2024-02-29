from abc import ABC, abstractmethod

class RobotInterface(ABC):

    def __init__(self):
        self.tf_offset = [0, 0, 0, 0, 0, 0]

    @abstractmethod
    def getTCPPose(self):
        pass

    @abstractmethod
    def getJointPose(self):
        pass

    @abstractmethod
    def getTFValue(self):
        pass
    
    @abstractmethod
    def setJointPose(self, joints):
        pass

    def zeroTFSensor(self):
        self.tf_offset = self.getTFValue()