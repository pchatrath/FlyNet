############################################################################################################
# ros_data_func_local.py
# Programmer: Mark Sakaguchi
# Created: 4/6/15
# Updated: 4/6/15
# Purpose:
############################################################################################################
import rospy
import sys, math, time, string
from pymavlink import mavutil
from math import *
############################################################################################################

############################################################################################################
"""
Function for grabbing localization data
"""
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
"""
############################################################################################################

############################################################################################################
def init_write_local(filename):
	f_local = open(filename,'a+')
	f_local.write("%Time, x_map, y_map, z_map, xdot_body, ydot_body, zdot_map, xddot_body, yddot_body, zddot_map, psi_map\n")
	f_local.truncate()
	f_local.close()
	return f_local
############################################################################################################

############################################################################################################
def write_local(filename,f_local,x_map,y_map,z_map,xdot_body,ydot_body,zdot_map,xddot_body,yddot_body,zddot_map,psi_map):
	f_local = open(filename,'a+')
	f_local.write("%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n" % (time.time(), x_map, y_map, z_map, xdot_body, ydot_body, zdot_map, xddot_body, yddot_body, zddot_map, psi_map))
	f_local.close()
	return f_local
############################################################################################################

############################################################################################################
"""
Function for grabbing px4flow data
"""
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
"""
############################################################################################################

############################################################################################################
def init_write_flow(filename):
	f_flow = open(filename,'a+')
	f_flow.write("%Time, px4flow_alt, quality, velocity_x, velocity_y\n")
	f_flow.truncate()
	f_flow.close()
	return f_flow
############################################################################################################

############################################################################################################
def write_flow(filename,f_flow,flow_alt,quality,velocity_x,velocity_y):
	f_flow = open(filename,'a+')
	f_flow.write("%f, %f, %f, %f, %f\n" % (time.time(), flow_alt, quality, velocity_x, velocity_y))
	f_flow.close()
	return f_flow
############################################################################################################

############################################################################################################
"""
Function for grabbing hokuyo data
"""
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
"""
############################################################################################################

############################################################################################################
def init_write_hokuyo(filename):
	f_hokuyo = open(filename,'a+')
	f_hokuyo.write("%Time, angle_min, angle_max, angle_inc, range_min, range_max, min_dist, min_range, angle, com_velx_body, com_vely_body\n")
	f_hokuyo.truncate()
	f_hokuyo.close()
	return f_hokuyo
############################################################################################################

############################################################################################################
def write_hokuyo(filename,min_dist,min_range,angle,target_velx_body,target_vely_body,angle_min,angle_max,angle_increment,range_min,range_max,ranges):
	f_hokuyo = open(filename,'a+')
	f_hokuyo.write("%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f" % (time.time(), angle_min, angle_max, angle_increment, range_min, range_max, min_dist, min_range, angle, target_velx_body, target_vely_body))
	n = 0
	for n in range(0,len(ranges)-1):
		f_hokuyo.write(", %f" % (ranges[n]))
		n = n + 1
	f_hokuyo.write('\n')
	f_hokuyo.close()
	return f_hokuyo
############################################################################################################
