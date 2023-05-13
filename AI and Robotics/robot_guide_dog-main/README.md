# robot_guide_dog
Heriot-Watt Univeristy, Dubai. 
School of Engineering and Physical Sciences
MSc. Robotics
B31XP - Multidisciplinary Group Project,    
 

PAWfessionals, Group Members:-   
Gowresh Rajagopal - H00413256   

Nasir Nasir-Ameen -  H00416471

Yehia AM Gomaa -  H00409854  

Supervisor:-
Dr. Nidhal Abdulaziz



## To run Simulation

roslaunch go1_config gazebo.launch   

roslaunch go1_config navigate.launch rviz:=true

roslaunch go1_config gazebo.launch


Install sound_play ros package
roslaunch sound_play soundplay_node.launch 

rosrun go1_config sound.py

roslaunch darknet_ros darknet_ros


## To run Untree go1 robot

*Connect to Unitree network*

**Ip address of the raspberry pi in Go1 is 192.168.12.1**

*Ensure proper network and IP resolutions, i.e 192.168.12.1 is the ROS_MASTER*


roslaunch unitree_legged_real keyboard_control.launch

roslaunch slamware_ros_sdk slamware_ros_sdk_intergated_with_teb.launch 

roslaunch usb_cam usb_cam-test.launch

roslaunch darknet_ros darknet_ros.launch

roslaunch sound_play soundplay_node.launch 

rosrun go1_config sound.py


