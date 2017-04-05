__author__ = 'Mike'

simulation_len = 2 #hours
requests_per_hour = 1500

T_max = simulation_len*60*60  #conver hourse to seconds  #simulation time
veh_speed = 36.0 #ft/s = #20mph #vehicle speed
max_distance = 2.5 * 5280.0 #miles #grid size
num_requests = simulation_len * requests_per_hour
#num_vehicles = 100
veh_capacity = 5
max_groupSize = 2
time_step = 1 #seconds
delta_veh_dist = veh_speed * time_step #feet
#hold_for = 60 #seconds
max_deviate = 1.6


RS_penalty = 30 * veh_speed #30seconds * veh_speed
#wait_time_multi =           #sec * 
