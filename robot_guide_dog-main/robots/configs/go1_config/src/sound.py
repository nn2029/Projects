#!/usr/bin/env python

import rospy

from time import sleep
from darknet_ros_msgs.msg import BoundingBoxes
from sound_play.msg import SoundRequest

class Sound:

   def __init__(self):
      self.sub = rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, self.callback)
      self.pub = rospy.Publisher('/robotsound', SoundRequest, queue_size = 10)
     
      rospy.spin()
      
   def callback(self, msg):
   	print(msg.bounding_boxes[0].Class)
   	if (msg.bounding_boxes[0].Class == 'person'):
   		pub_msg = SoundRequest()
   		pub_msg.sound= -3 
   		pub_msg.command= 1
   		pub_msg.volume= 1.0
   		pub_msg.arg= 'There is a person in front'
   		
   		self.pub.publish(pub_msg)
   		rospy.sleep(2)
   	elif (msg.bounding_boxes[0].Class == 'car'):
   		pub_msg = SoundRequest()
   		pub_msg.sound= -3 
   		pub_msg.command= 1
   		pub_msg.volume= 1.0
   		pub_msg.arg= 'There is a car in front'
   		
   		self.pub.publish(pub_msg)
   		rospy.sleep(2)
   	elif (msg.bounding_boxes[0].Class == 'stop sign'):
   		pub_msg = SoundRequest()
   		pub_msg.sound= -3 
   		pub_msg.command= 1
   		pub_msg.volume= 1.0
   		pub_msg.arg= 'There is a stop sign'
   		
   		self.pub.publish(pub_msg)
   		rospy.sleep(2)
   	elif (msg.bounding_boxes[0].Class == 'traffic light'):
   		pub_msg = SoundRequest()
   		pub_msg.sound= -3 
   		pub_msg.command= 1
   		pub_msg.volume= 1.0
   		pub_msg.arg= 'There is a traffic light'
   		
   		self.pub.publish(pub_msg)
   		rospy.sleep(2)
if __name__ == '__main__':
    rospy.init_node('dog_sound', anonymous=True)
    check = Sound()
