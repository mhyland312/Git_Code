__author__ = 'Mike'

simulation_len = 2.0 #hours
#requests_per_hour = 1500

T_max = int(simulation_len*60*60)  #convert hours to seconds  #simulation time
veh_speed = 53.0 #ft/s = #35mph #vehicle speed
#max_distance = 10.0 * 5280.0 #miles #grid size
#num_requests = int(simulation_len * requests_per_hour)
#num_vehicles = 100
veh_capacity = 5
max_groupSize = 2
time_step = 1 #seconds
delta_veh_dist = veh_speed * time_step #feet
#hold_for = 60 #seconds

inf = 10000000000000


pen_RS = 30.0 #30seconds * veh_speed
shared_ride_penalty = pen_RS * veh_speed

#wait_time_multi =  50.0

#demand_Dist = "O_Uniform_D_Uniform" #"O_Uniform_D_Transit" "O_Uniform_D_Cluster"
###Rideshare Constraint Settings
#vehicle cannot increase remaining travel distance by X%
max_deviate = 1.6
#must have an X% decrease with RS
min_improve_perc = 0.8
#must reduce wait time by Xmin
min_improve_min = 1.5
min_improve_ft = min_improve_min * 60 * veh_speed


pen_reassign = 7.0#seconds
reassign_penalty = pen_reassign * veh_speed


pen_drop_time = 15.0
dropoff_penalty = pen_drop_time * veh_speed


#converts wait time units to distance units
#1 minute wait = 60 seconds = 3000 ft = 0.57 miles
gamma = 50.0

curb_pick_time = 45.0 #seconds
curb_drop_time = 15.0 #seconds
