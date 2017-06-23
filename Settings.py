__author__ = 'Mike'

simulation_len = 3.0 #hours
#requests_per_hour = 1500

T_max = int(simulation_len*60*60)  #convert hours to seconds  #simulation time
veh_speed = 36.0 #ft/s = #20mph #vehicle speed
#max_distance = 10.0 * 5280.0 #miles #grid size
#num_requests = int(simulation_len * requests_per_hour)
#num_vehicles = 100
veh_capacity = 5
max_groupSize = 2
time_step = 1 #seconds
delta_veh_dist = veh_speed * time_step #feet
#hold_for = 60 #seconds

inf = 10000000000000


RS_penalty = 30 * veh_speed #30seconds * veh_speed
wait_time_multi =  50.0

demand_Dist = "O_Uniform_D_Uniform" #"O_Uniform_D_Transit" "O_Uniform_D_Cluster"
###Rideshare Constraint Settings
#vehicle cannot increase remaining travel distance by X%
max_deviate = 1.6
#must have an X% decrease with RS
min_improve_perc = 0.8
#must reduce wait time by Xmin
min_improve_min = 1.5
min_improve_ft = min_improve_min * 60 * veh_speed


penalty_reassign = 20.0 #seconds