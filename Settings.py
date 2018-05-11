__author__ = 'Mike'

simulation_len = 4.0  # hours

t_max = int(simulation_len * 60 * 60)  # convert hours to seconds  #simulation time
# veh_speed = 53.0  # ft/s = #35mph #vehicle speed
veh_speed = 5.0  # m/s
veh_capacity = 5
max_group_size = 2
time_step = 1  # seconds
delta_veh_dist = veh_speed * time_step  # feet or meters

inf = 10000000000000

pen_reassign = 30.0  # seconds
reassign_penalty = pen_reassign * veh_speed

pen_drop_time = 15.0
dropoff_penalty = pen_drop_time * veh_speed

# converts wait time units to distance units
# 1 minute wait = 60 seconds = 3000 ft = 0.57 miles
gamma = 50.0 / 3.0

curb_pick_time = 45.0  # seconds
curb_drop_time = 15.0  # seconds
