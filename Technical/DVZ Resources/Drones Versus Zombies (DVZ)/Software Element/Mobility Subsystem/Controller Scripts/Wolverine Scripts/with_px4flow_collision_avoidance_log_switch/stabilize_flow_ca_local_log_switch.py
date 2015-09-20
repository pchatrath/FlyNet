#!/usr/bin/env python

############################################################################################################
# stabilize_flow_ca_local.py
# Programmer: Mark Sakaguchi
# Created: 4/6/2015
# Updated: 4/8/2015
# Purpose:
############################################################################################################
import rospy
import sys, math, time, string
import vrpn_Tracker
import transformations
import roscopter.msg
from std_msgs.msg import String, Header, Float64, Float32MultiArray
from px_comm.msg import OpticalFlow
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped
from pymavlink import mavutil
from math import *
from controllers_func_flow_ca_local_log_switch import *
from pixhawk_func_ca_local_log_switch import *
from collision_avoidance_func_local_log_switch import *
from data_logging import *
############################################################################################################
# Logging files
fname_log = 'info_files/full_system_test.txt'

# Initialize controller info files
f_log = init_log(fname_log)
############################################################################################################

############################################################################################################
"""
Function for grabbing localization data
"""
x_map = 0
y_map = 0
z_map = 0
xdot_body = 0
ydot_body = 0
zdot_map = 0
xddot_body = 0
yddot_body = 0
zddot_map = 0
psi_map = 0

def get_local(data):
	global x_map, y_map, z_map, xdot_body, ydot_body, zdot_map, xddot_body, yddot_body, zddot_map, psi_map
	x_map = data.data[0]
	y_map = data.data[1]
	z_map = data.data[2]
	xdot_body = data.data[3]
	ydot_body = data.data[4]
	zdot_map = data.data[5]
	xddot_body = data.data[6]
	yddot_body = data.data[7]
	zddot_map = data.data[8]
	psi_map = data.data[9]
############################################################################################################

############################################################################################################
"""
Function for grabbing px4flow data
"""
flow_alt = 0
velocity_x = 0
velocity_y = 0
quality = 0

def get_px4flow(data):
	global flow_alt, velocity_x, velocity_y, quality
	flow_alt = data.ground_distance
	velocity_x = data.velocity_x
	velocity_y = data.velocity_y
	quality = data.quality
############################################################################################################

############################################################################################################
"""
Function for grabbing hokuyo data
"""
angle_min = 0
angle_max = 0
angle_increment = 0
scan_time = 0
range_min = 0
range_max = 0
ranges = (1.0, 0.0)
intensities = (1.0, 0.0)

def get_hokuyo(data):
	global angle_min, angle_max, angle_increment, scan_time ,range_min, range_max, ranges, intensities
	angle_min = data.angle_min
	angle_max = data.angle_max
	angle_increment = data.angle_increment
	scan_time = data.scan_time
	range_min = data.range_min
	range_max = data.range_max
	ranges = data.ranges
	intensities = data.intensities
############################################################################################################

############################################################################################################
"""
Function for grabbing navigation goal
"""
x_goal = 0
y_goal = 0
psi_goal = 0

def get_nav_goal(data):
	global x_goal, y_goal, psi_goal
	x_goal = data.pose.position.x
	y_goal = data.pose.position.y
	
	quatx = data.pose.orientation.x
	quaty = data.pose.orientation.y
	quatz = data.pose.orientation.z
	quatw = data.pose.orientation.w
	
	quat = [quatw, quatx, quaty, quatz]
	
	euler = transformations.euler_from_quaternion(quat,'rxyz')
	psi_goal = euler[2]
############################################################################################################

############################################################################################################
"""
Function for streaming vicon position and orientation
"""
def handle_tracker(userdata,t):
	global vicon_pos, vicon_orient, got_report
	(qx, qy, qz, qw) = t[4:8]
	quat = [qw, qx, qy, qz]
	euler = transformations.euler_from_quaternion(quat,'rxyz')
	vicon_orient = [euler[1], euler[0], euler[2]]
	vicon_pos = [t[1], t[2], t[3]]
	got_report = 1
############################################################################################################

############################################################################################################
## Start Script ##
############################################################################################################
# Specify using vicon or amcl
use_vicon = 1

# Specify Pixhawk device
device = '/dev/pixhawk'

# Specify baudrate
baud = 1500000

# Initialize connection
master = mavutil.mavlink_connection(device,baud)
print "Attempting to get HEARTBEAT message from Pixhawk..."

# Initialize rate for data stream send
rate = 25
test = dir(master.mav)
#print test

# Request heartbeat from APM
master.wait_heartbeat()
print "Got HEARTBEAT!"

# Initialize current Pixhawk value arrays
current_rc_channels = [None]*6
battery = [None]*3
pix_att = [None]*6
pix_imu = [None]*11

# Grab initial Pixhawk values
init_pix_rc_channels(master,current_rc_channels,rate)
init_pix_battery(master,battery,rate)
init_pix_att(master,pix_att,rate)
header = header_type()
init_pix_imu(master,pix_imu,rate,header)

# Initialize ROS controller node
print "Initializing controller nodes..."
rospy.init_node('controller',anonymous=True)
print "		ROS controller node initialized!"

# Initialize Pixhawk attitude and raw_imu ROS publishers
print "Initializing publishers..."
pub_attitude = rospy.Publisher('attitude',roscopter.msg.Attitude,queue_size = 10)
print "		Pixhawk attitude ROS publisher initialized!"
pub_raw_imu = rospy.Publisher('raw_imu',roscopter.msg.Mavlink_RAW_IMU,queue_size = 10)
print "		Pixhawk raw_imu ROS publisher initialized!"

# Set ROS subscriber rate
rate = 20
r = rospy.Rate(rate)
print "Setting ROS subscriber rates..."
print "		PX4Flow ROS subscriber rate set to: %f Hz" % (rate)
print "		Hokuyo ROS subscriber rate set to: %f Hz" % (rate)
print "		AMCL ROS subscriber rate set to: %f Hz" % (rate)
print "		Position Goal ROS subscriber rate set to: %f Hz" % (rate)
print " "

# Initialize quad structure
quad = vehicle()

# Initialize quad fields
quad = init_vehicle(quad)

# Set controller integrator bounds
quad.I_alt_bounds = 0.8
quad.I_vel_bounds = 0.5
quad.I_pos_bounds = 1
# Set x,y velocity saturation bounds
quad.velx_sat_bounds = 0.25
quad.vely_sat_bounds = 0.25
# Set gains for PID altitude controller
quad.alt_K_P = 20#30
quad.alt_K_I = 7#20
quad.alt_K_D = -60#-100
#quad.alt_K_P = 20
#quad.alt_K_I = 7
#quad.alt_K_D = -60
# Set gains for PID yaw controller
quad.yaw_K_P = 150
quad.yaw_K_I = 10
quad.yaw_K_D = -100
# Set gains for PID velocity controller
quad.velx_K_P = -0.26
quad.velx_K_I = -0.05
quad.velx_K_D = 0
quad.vely_K_P = 0.25
quad.vely_K_I = 0.05
quad.vely_K_D = 0
# Set gains for PID position controller
quad.posx_K_P = 0.15#0.6
quad.posx_K_I = 0
quad.posx_K_D = 0
quad.posy_K_P = 0.15#0.5
quad.posy_K_I = 0
quad.posy_K_D = 0

# Set base RC levels
quad.base_rc_throttle = 1300
quad.base_rc_roll = 1627
quad.base_rc_pitch = 1436
quad.base_rc_yaw = 1558

# Set collision avoidance parameters
min_dist = 0.7
K_mark = 0.115
K_drew = 0.0038

# If user presses enter, start script
raw_input("Press Enter to start script...")

if use_vicon == 1:
	# Set up VRPN
	print " "
	print "Setting up VRPN..."
	print " "
	t = vrpn_Tracker.vrpn_Tracker_Remote("wolverine@192.168.20.10")
	vrpn_Tracker.register_tracker_change_handler(handle_tracker)
	vrpn_Tracker.vrpn_Tracker_Remote.register_change_handler(t,None,vrpn_Tracker.get_tracker_change_handler())

# Initialize variables so that log file can be written
(quad, vicon_pos, pix_att, x_map, y_map, z_map, psi_map, battery, pix_imu, xdot_body, ydot_body, zdot_map, xddot_body, yddot_body, zddot_map, psi_map) = init_variables()

flag = 0
start_time = time.time()
while not rospy.is_shutdown():
	# Subscribe to PX4Flow and Hokuyo data
	rospy.Subscriber("/px4flow/opt_flow",OpticalFlow,get_px4flow)
	rospy.Subscriber("/scan",LaserScan,get_hokuyo)
	rospy.Subscriber("/state_estimate",Float32MultiArray,get_local)
	rospy.Subscriber("/move_base_simple/goal",PoseStamped,get_nav_goal)
	r.sleep()
	
	current_time = time.time()

	if use_vicon == 1:
		# Get vicon data
		got_report = 0
		vrpn_Tracker.vrpn_Tracker_Remote.mainloop(t)
		while(got_report != 1):
			vrpn_Tracker.vrpn_Tracker_Remote.mainloop(t)
		if flag == 0:
			print " "
			print "VRPN Successful!"
			print " "

			quad.previous_x_inertial_velx = vicon_pos[0]#x_map
			quad.previous_y_inertial_vely = vicon_pos[1]#y_map
			quad.previous_x_inertial = vicon_pos[0]#x_map
			quad.previous_y_inertial = vicon_pos[1]#y_map
			quad.previous_alt = z_map#flow_alt
			quad.previous_roll = pix_att[0]
			quad.previous_pitch = pix_att[1]
			flag = 1
	else:
		quad.previous_x_inertial_velx = x_map
		quad.previous_y_inertial_vely = y_map
		quad.previous_x_inertial = x_map
		quad.previous_y_inertial = y_map
		quad.previous_alt = z_map
		quad.previous_roll = pix_att[0]
		quad.previous_pitch = pix_att[1]
		flag = 1

	# Update Pixhawk values
	current_rc_channels = update_pix_rc_channels(master,current_rc_channels,rate)
	battery = update_pix_battery(master,battery,rate)
	pix_att = update_pix_att(master,pix_att,rate)
	pix_imu = update_pix_imu(master,pix_imu,rate,header)

	# Publish Pixhawk attitude and raw imu
	pub_attitude.publish(pix_att[0],pix_att[1],pix_att[2],pix_att[3],pix_att[4],pix_att[5])
	pub_raw_imu.publish(pix_imu[0],pix_imu[1],pix_imu[2],pix_imu[3],pix_imu[4],pix_imu[5],pix_imu[6],pix_imu[7],pix_imu[8],pix_imu[9],pix_imu[10])
	
	# Call collision avoidance
	(angle,min_range,target_velx_body,target_vely_body,ca_active_flag) = collision_avoidance_drew(K_drew,min_dist,angle_min,angle_max,angle_increment,range_min,range_max,ranges)
	#(angle,min_range,target_velx_body,target_vely_body,ca_active_flag) = collision_avoidance_mark(K_mark,min_dist,angle_min,angle_max,angle_increment,range_min,range_max,ranges)

	# Set targets for controllers
	target_alt = 0.75
	target_x = x_goal
	target_y = y_goal
	
	# Get current values for controller
	if use_vicon == 1:
		x = vicon_pos[0]
		y = vicon_pos[1]
		alt = z_map
		inertial_yaw = vicon_orient[2]
	else:
		x = x_map
		y = y_map
		alt = z_map
		inertial_yaw = psi_map

	roll = pix_att[0]
	pitch = pix_att[1]
	yaw = pix_att[2]
	
	# Call controllers
	alt_controller(master,quad,target_alt,alt,current_rc_channels,zdot_map)
	#alt_controller_alternative(master,quad,target_alt,alt,current_rc_channels,zdot_map,roll,pitch)

	if ca_active_flag == 1:
		velocity_controller(master,quad,0,0,target_velx_body,target_vely_body,x,y,inertial_yaw,current_rc_channels,ca_active_flag,xdot_body,ydot_body,xddot_body,yddot_body)
	else:
		rc_roll_reset(master)
		rc_pitch_reset(master)
	#position_controller(master,quad,target_x,target_y,x,y)
	#velocity_controller(master,quad,quad.velx_inertial_send,quad.vely_inertial_send,0,0,x,y,inertial_yaw,current_rc_channels,ca_active_flag,xdot_body,ydot_body,xddot_body,yddot_body)
		
	###############################
	##### Write to info files #####
	###############################
	if current_rc_channels[5] > 1400:
		f_log = write_log(fname_log,quad,vicon_pos,pix_att,x_map,y_map,z_map,psi_map,flow_alt,current_rc_channels,battery,pix_imu,xdot_body,ydot_body,zdot_map,xddot_body,yddot_body,zddot_map,quality,velocity_x,velocity_y,min_dist,min_range,angle,target_velx_body,target_vely_body,angle_min,angle_max,angle_increment,range_min,range_max,ranges)

	##### EXIT SCRIPT #####
	# If channel 5 is high
	#######################
	if current_rc_channels[4] > 1400:
		rc_all_reset(master)
		print " "
		print "Resetting all RC overrides..."
		print " "
		print "r = %f, p = %f, t = %f, y = %f, ch5 = %f, ch6 = %f" % (current_rc_channels[0], current_rc_channels[1], current_rc_channels[2], current_rc_channels[3], current_rc_channels[4], current_rc_channels[5])
		current_rc_channels = update_pix_rc_channels(master,current_rc_channels,rate)
		# Close MAVLINK port
		print " "
		print "Closing MAVLINK port..."
		master.close()
		break