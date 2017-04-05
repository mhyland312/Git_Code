__author__ = 'Mike'

import math
import Vehicle
import Settings

def dist_euclid(person, vehicle):
    x_pass = person.pickup_location_x
    y_pass = person.pickup_location_y
    x_veh = vehicle.position_x
    y_veh = vehicle.position_y
    dist = math.sqrt((x_veh - x_pass)**2 + (y_veh - y_pass)**2)

    return dist

def dist_manhat(person, vehicle):
    x_pass = person.pickup_location_x
    y_pass = person.pickup_location_y
    x_veh = vehicle.position_x
    y_veh = vehicle.position_y
    dist = abs(x_veh-x_pass) + abs(y_veh-y_pass)

    return dist


def dyn_dist_manhat(person, vehicle):
    x_veh = vehicle.position_x
    y_veh = vehicle.position_y
    x_drop1 = vehicle.next_drop.dropoff_location_x
    y_drop1 = vehicle.next_drop.dropoff_location_y
    dist1 = abs(x_drop1-x_veh) + abs(y_drop1-y_veh)

    x_pick2 = person.pickup_location_x
    y_pick2 = person.pickup_location_y
    dist2 = abs(x_pick2-x_drop1) + abs(y_pick2-y_drop1)

    tot_dist = dist1 + dist2

    return tot_dist



def delta_manhat_dist(t, vehicle, person):
    if vehicle.state == "enroute_pickup":
        dest_x = person.pickup_location_x
        dest_y = person.pickup_location_y

    elif vehicle.state == "enroute_dropoff":
        dest_x = person.dropoff_location_x
        dest_y = person.dropoff_location_y

    veh_x = vehicle.position_x
    veh_y = vehicle.position_y
    dist_x = abs(dest_x-veh_x)
    dist_y = abs(dest_y-veh_y)
    total_dist_manhat = dist_x + dist_y
    #hyp = math.sqrt((dist_x)**2 + (dist_y)**2)

   #if the vehicle is right next to the pickup/dropoff point
    if total_dist_manhat < (Settings.delta_veh_dist):

        vehicle = Vehicle.update_Vehicle(t, person, vehicle)
        vehicle.total_distance += total_dist_manhat

    else:
        proportion_x = dist_x/(dist_x + dist_y)
        proportion_y = dist_y/(dist_x + dist_y)

        if veh_x < dest_x:
            vehicle.position_x += proportion_x * Settings.delta_veh_dist
        else:
            vehicle.position_x += -1 * proportion_x * Settings.delta_veh_dist

        if veh_y < dest_y:
            vehicle.position_y += proportion_y * Settings.delta_veh_dist
        else:
            vehicle.position_y += -1 * proportion_y * Settings.delta_veh_dist

        vehicle.total_distance += Settings.delta_veh_dist
    
    return (vehicle)




    
    
