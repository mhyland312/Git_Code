__author__ = 'Mike'

import math


def dist_euclid(person, vehicle):
    x_pass = person.pickup_location_x
    y_pass = person.pickup_location_y
    x_veh = vehicle.position_x
    y_veh = vehicle.position_y
    dist_euclid1 = math.sqrt((x_veh - x_pass)**2 + (y_veh - y_pass)**2)

    return dist_euclid1


def dist_manhat(person, vehicle):
    x_pass = person.pickup_location_x
    y_pass = person.pickup_location_y
    x_veh = vehicle.position_x
    y_veh = vehicle.position_y
    dist_manhat1 = abs(x_veh-x_pass) + abs(y_veh-y_pass)

    return dist_manhat1


def dyn_dist_manhat(person, vehicle):
    x_veh = vehicle.position_x
    y_veh = vehicle.position_y
    x_drop1 = vehicle.next_drop.dropoff_location_x
    y_drop1 = vehicle.next_drop.dropoff_location_y
    dyn_dist_manhat1 = abs(x_drop1-x_veh) + abs(y_drop1-y_veh)

    x_pick2 = person.pickup_location_x
    y_pick2 = person.pickup_location_y
    dyn_dist_manhat2 = abs(x_pick2-x_drop1) + abs(y_pick2-y_drop1)

    tot_dist = dyn_dist_manhat1 + dyn_dist_manhat2

    return tot_dist
