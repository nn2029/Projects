from controller import Robot
from datetime import datetime
import math
import numpy as np


class Controller:
    def __init__(self, robot):        
        # Robot Parameters
        self.robot = robot
        timestep = int(robot.getBasicTimeStep())
        self.time_step = 32 # ms
        self.max_speed = 1 # m/s
 
        # Enable Motors
        self.left_motor = self.robot.getDevice('left wheel motor')
        self.right_motor = self.robot.getDevice('right wheel motor')
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)
        self.velocity_left = 0
        self.velocity_right = 0
    
        # Enable Proximity Sensors
        self.proximity_sensors = []
        for i in range(8):
            sensor_name = 'ps' + str(i)
            self.proximity_sensors.append(self.robot.getDevice(sensor_name))
            self.proximity_sensors[i].enable(self.time_step)
            
            
        #Enable Ground Sensors
        self.center_ir = self.robot.getDevice('gs1')
        self.center_ir.enable(self.time_step)
        
        #Creating a variable to store sensor data
        self.inputs = []       
     
    def run_robot(self):
        while self.robot.step(self.time_step) != -1:
            # Get Sensors Values
            center = self.center_ir.getValue()
            self.inputs.append(center)
            self_black = 0
      
            #detecting proximity to walls 
            self.left_wall = self.proximity_sensors [5].getValue() > 80
            self.left_corner = self.proximity_sensors [6].getValue() 
            self.right_corner = self.proximity_sensors [1].getValue() 
            self.front_wall = self.proximity_sensors [7].getValue() 
            
            
            #checking if the black square was detected
            for i in self.inputs[3:]:
                        if(i <= 350):
                            self_black = 1 
            if (self.front_wall > 80) and (self_black == 0):  
                    print ("Turning Left")
                    self.left_speed = -self.max_speed
                    self.right_speed = self.max_speed
                
                    if self.left_wall:
                        print("Moving forward")
                        self.left_speed = self.max_speed
                        self.right_speed = self.max_speed
                       
                    if (self.left_corner > 150):
                        self.left_speed = self.max_speed 
                        self.right_speed = self.max_speed * 0.25
                        
                    if (self.right_corner  > 150):
                        self.left_speed = self.max_speed * 0.25
                        self.right_speed = self.max_speed
            else:
                if (self.front_wall> 80) and (self_black == 1):
                    print ("Turning Right")
                    self.left_speed = self.max_speed
                    self.right_speed = -self.max_speed
                
                if self.left_wall:
                        print("Moving forward")
                        self.left_speed = self.max_speed
                        self.right_speed = self.max_speed
                        
                if (self.left_corner  > 150):
                        self.left_speed = self.max_speed
                        self.right_speed = self.max_speed * 0.3
                        
                if (self.right_corner  > 150):
                        self.left_speed = self.max_speed * 0.3
                        self.right_speed = self.max_speed
                        
                if (self.front_wall > 100):
                    print ("Goal Reached")
                    self.left_speed = 0
                    self.right_speed = 0        

            self.left_motor.setVelocity(self.left_speed)
            self.right_motor.setVelocity(self.right_speed)
                
                
if __name__ == "__main__":
    
    #creating robot instance
    my_robot = Robot()
    controller = Controller(my_robot)
    controller.run_robot()