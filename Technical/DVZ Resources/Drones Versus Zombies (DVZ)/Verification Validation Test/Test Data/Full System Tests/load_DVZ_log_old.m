function log = load_DVZ_log(filename)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% load_DVZ_log.m
% Austin Lillard
% Created: 04/06/2015
% Updated: 04/06/2015
% Purpose:
%       -To load the specified log file generated from a flight test for
%       data analysis.
%
% Input:
%       -filename: name of the data file
% 
% Output:
%       -log: structure containing logged information
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Load in data

% Load to structure
data = csvread(filename,4,0);

% Assign to output data structure
%% System time
log.time = data(:,1) - data(1,1);      % [ns?]

%% Vicon position
log.vicon_x = data(:,2);   % [m]
log.vicon_y = data(:,3);    % [m]
log.vicon_z = data(:,4);    % [m]

%% Pixhawk attitude values
log.pixhawk_roll = data(:,5); % [rad]
log.pixhawk_pitch = data(:,6); % [rad]
log.pixhawk_yaw = data(:,7); % [rad]
log.pixhawk_rollspeed = data(:,8); % [rad/s]
log.pixhawk_pitchspeed  = data(:,9); % [rad/s]
log.pixhawk_yawspeed = data(:,10); % [rad/s]

%% AMCL position and heading
log.amcl_x = data(:,11);    % [m]
log.amcl_y = data(:,12);    % [m]
log.amcl_z = data(:,13);    % [m]
log.amcl_yaw = data(:,14);  % [rad]

%% Altitude controller data
log.filtered_px4flow_alt = data(:,15); %[m]
log.unfiltered_px4flow_alt = data(:,16); %[m]
log.alt_RC_P = data(:,17);  % [PWM]
log.alt_RC_I = data(:,18);  % [PWM]
log.alt_RC_D = data(:,19);  % [PWM]
log.rc_T_send = data(:,20); % [PWM]

%% Velocity controller data
log.velx_body = data(:,21); % [m/s]
log.velx_P = data(:,22);    % [PWM]
log.velx_I = data(:,23);    % [PWM]
log.velx_D = data(:,24);    % [PWM]
log.pitch_angle_send = data(:,25); % [rad]
log.pitch_pwm_send = data(:,26); % [PWM]
log.vely_body = data(:,27); % [m/s]
log.vely_P = data(:,28);    % [PWM]
log.vely_I = data(:,29);    % [PWM]
log.vely_D = data(:,30);    % [PWM]
log.roll_angle_send = data(:,31);   % [rad]
log.roll_pwm_send = data(:,32); % [PWM]
log.target_velx_inertial = data(:,33);  % [m/s]
log.target_vely_inertial = data(:,34);  % [m/s]
log.inertial_yaw = data(:,35);  % [rad]
log.target_velx_body = data(:,36);  % [m/s]
log.target_vely_body = data(:,37);  % [m/s]

%% Yaw controller



%% Position controller data
log.velx_inertial_send = data(:,38);    % [m]
log.posx_P = data(:,39);    % [PWM]
log.posx_I = data(:,40);    % [PWM]
log.posx_D = data(:,41);    % [PWM]
log.vely_inertial_send = data(:,42);    % [m]
log.posy_P = data(:,43);    % [PWM]
log.posy_I = data(:,44);    % [PWM]
log.posy_D = data(:,45);    % [PWM]
log.target_x = data(:,46);  % [m]
log.target_y = data(:,47);  % [m]

%% RC handset pwm data
log.handset_roll = data(:,48);  % [PWM]
log.handset_pitch = data(:,49); % [PWM]
log.handset_throttle = data(:,50);  % [PWM]
log.handset_yaw = data(:,51);   % [PWM]
log.handset_ch5 = data(:,52);   % [PWM]
log.handset_ch6 = data(:,53);   % [PWM]

%% Pixhawk battery data
log.voltage = data(:,54);   % [volts]
log.current = data(:,55);   % [amps]
log.battery_remaining = data(:,56); % [percentage]

%% Pixhawk raw imu data
log.pixhawk_xacc = data(:,57);
log.pixhawk_yacc = data(:,58);
log.pixhawk_zacc = data(:,59);
log.pixhawk_xgyro = data(:,60);
log.pixhawk_ygyro = data(:,61);
log.pixhawk_zgyro = data(:,62);
log.pixhawk_xmag = data(:,63);
log.pixhawk_ymag = data(:,64);
log.pixhawk_zmag = data(:,65);

%% Localization subscriber data
log.local_xmap = data(:,66);
log.local_ymap = data(:,67);
log.local_zmap = data(:,68);
log.local_velx_body = data(:,69);
log.local_vely_body = data(:,70);
log.local_velz_map = data(:,71);
log.local_accx_body = data(:,72);
log.local_accy_body = data(:,73);
log.local_accz_map = data(:,74);
log.local_psi_map = data(:,75);

%% PX4Flow subscriber data
log.px4flow_alt = data(:,76);
log.px4flow_quality = data(:,77);
log.px4flow_velx = data(:,78);
log.px4flow_vely = data(:,79);

%% Hokuyo subscriber/collision avoidance data
log.hokuyo_angle_min = data(:,80);
log.hokuyo_angle_max = data(:,81);
log.hokuyo_angle_increment = data(:,82);
log.hokuyo_range_min = data(:,83);
log.hokuyo_range_max = data(:,84);
log.hokuyo_min_dist = data(:,85);
log.hokuyo_min_range = data(:,86);
log.hokuyo_angle = data(:,87);
log.hokuyo_target_velx_body = data(:,88);
log.hokuyo_target_vely_body = data(:,89);
log.hokuyo_ranges = data(:,90:end);

end