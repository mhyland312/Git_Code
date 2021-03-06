__author__ = 'Mike'

import sys
import Settings as Set

class Person(object):
    person_id = -1
    pickup_location_x = -1.0
    pickup_location_y = -1.0
    request_time = -1
    dropoff_location_x = -1.0
    dropoff_location_y = -1.0
    group_size = -1
    in_veh_dist = -1

    assign_time = -3
    pickup_time = -3
    dropoff_time = -3
    wait_assgn_time = -3
    wait_pick_time = -3
    travel_time = -3
    vehicle_id = -3
    old_vehicles = []
    status = "string"
    reassigned = 0

    # The class "constructor" - It's actually an initializer
    def __init__(self, person_id, pickup_location_x, pickup_location_y, request_time, dropoff_location_x, dropoff_location_y, group_size):
        self.person_id = person_id
        self.pickup_location_x = pickup_location_x
        self.pickup_location_y = pickup_location_y
        self.request_time = request_time
        self.dropoff_location_x = dropoff_location_x
        self.dropoff_location_y = dropoff_location_y
        self.group_size = group_size
        self.in_veh_dist = abs(pickup_location_x-dropoff_location_x) + abs(pickup_location_y-dropoff_location_y)

        self.assign_time = -3
        self.pickup_time = -3
        self.dropoff_time = -3
        self.wait_assgn_time = -3
        self.wait_pick_time = -3
        self.travel_time = -3
        self.vehicle_id = -3
        self.old_vehicles = []
        self.status = "un_requested"
        self.reassigned = 0


def make_person(person_id, pickup_location_x, pickup_location_y, request_time, dropoff_location_x, dropoff_location_y, group_size):
    person_a = Person(person_id, pickup_location_x, pickup_location_y, request_time, dropoff_location_x, dropoff_location_y, group_size)
    return person_a

def get_wait_assgn_time(request_time, assgn_time):
    wait_assgn_time = assgn_time - request_time
    return wait_assgn_time

def get_wait_pick_time(request_time, pickup_time):
    wait_pick_time = pickup_time - request_time
    return wait_pick_time

def get_travel_time(pickup_time, dropoff_time):
    travel_time = dropoff_time - pickup_time
    return travel_time

def made_request():
    status = "unassigned"
    return status

def status_assigned():
    status = "assigned"
    return status

def status_inVeh():
    status = "inVeh"
    return status

def status_served():
    status = "served"
    return status


def update_person(t, person_1, vehicle1):
    if person_1.status == "un_requested":
        person_1.status = made_request()
    
    elif person_1.status == "unassigned":
        person_1.status = status_assigned()
        person_1.vehicle_id = vehicle1.vehicle_id
        person_1.old_vehicles.append(vehicle1.vehicle_id)
        person_1.assign_time = t
        person_1.wait_assgn_time = get_wait_assgn_time(person_1.request_time, person_1.assign_time)
        
    elif person_1.status == "assigned":
        person_1.status = status_inVeh()
        person_1.vehicle_id = vehicle1.vehicle_id
        person_1.pickup_time = t
        person_1.wait_pick_time = get_wait_pick_time(person_1.request_time, person_1.pickup_time)

    elif person_1.status == "reassign":
        person_1.status = status_assigned()
        person_1.vehicle_id = vehicle1.vehicle_id
        person_1.old_vehicles.append(vehicle1.vehicle_id)
        person_1.reassigned = 1

    elif person_1.status == "inVeh":
        person_1.status = status_served()
        person_1.dropoff_time = t
        person_1.travel_time = get_travel_time(person_1.pickup_time, person_1.dropoff_time)

    return person_1
