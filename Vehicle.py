import Settings
import Person
import sys
import Regions

__author__ = 'Mike'


class Vehicle(object):
    # static input features
    vehicle_id = -5
    start_location_x = -1.0
    start_location_y = -1.0
    capacity = -1

    # dynamic information needed for simulation
    current_load = 0
    position_x = start_location_x
    position_y = start_location_y
    current_dest_x = -1.0
    current_dest_y = -1.0
    next_pickup = Person.Person
    next_drop = Person.Person
    next_sub_area = Regions.SubArea
    status = "string"
    reassigned = 0
    curb_time_remain = 0
    last_drop_time = 0

    # output information - update throughout simulation
    total_distance = 0.0
    empty_distance = 0.0
    loaded_distance = 0.0
    pass_assgn_list = []
    pass_picked_list = []
    pass_dropped_list = []
    assigned_times = []
    pickup_times = []
    dropoff_times = []
    pass_assgn_count = 0
    pass_pick_count = 0
    pass_drop_count = 0
    reposition_count = 0

    # The class "constructor" - It's actually an initializer
    def __init__(self, vehicle_id, start_location_x, start_location_y, capacity, status):
        # static input features
        self.vehicle_id = vehicle_id
        self.start_location_x = start_location_x
        self.start_location_y = start_location_y
        self.capacity = capacity

        # dynamic information needed for simulation
        self.current_load = 0
        self.position_x = start_location_x
        self.position_y = start_location_y
        self.current_dest_x = -1
        self.current_dest_y = -1
        self.next_pickup = Person.Person
        self.next_drop = Person.Person
        self.next_sub_area = Regions.SubArea
        self.status = status
        self.reassigned = 0
        self.curb_time_remain = 0
        self.last_drop_time = 0

        # output information - update throughout simulation
        self.total_distance = 0.0
        self.empty_distance = 0.0
        self.loaded_distance = 0.0
        self.pass_assgn_list = []
        self.pass_picked_list = []
        self.pass_dropped_list = []
        self.assigned_times = []
        self.pickup_times = []
        self.dropoff_times = []
        self.pass_assgn_count = 0
        self.pass_pick_count = 0
        self.pass_drop_count = 0
        self.reposition_count = 0


# function to create an instance of class/object vehicle
def make_vehicle(vehicle_id, start_location_x, start_location_y, capacity, status):
    vehicle1 = Vehicle(vehicle_id, start_location_x, start_location_y, capacity, status)
    return vehicle1
##############################################################################


##############################################################################
# Function to move vehicle every time step
def move_vehicle_manhat(t, vehicle, person, sub_area):

    if vehicle.status == "relocating":
        dest_x = sub_area.relocation_destination[0]
        dest_y = sub_area.relocation_destination[1]
        vehicle.empty_distance += Settings.delta_veh_dist

    elif vehicle.status == "enroute_pickup":
        dest_x = person.pickup_location_x
        dest_y = person.pickup_location_y
        if vehicle.current_load > 0:
            vehicle.loaded_distance += Settings.delta_veh_dist
        else:
            vehicle.empty_distance += Settings.delta_veh_dist

    elif vehicle.status == "enroute_dropoff":
        dest_x = person.dropoff_location_x
        dest_y = person.dropoff_location_y
        vehicle.loaded_distance += Settings.delta_veh_dist

    else:
        sys.exit("Error in moveVehicle_manhat - wrong vehicle status")

    # # check for bugs - keep in code
    # if dest_x < 0.0 or dest_y < 0.0:
    #     print(dest_x, dest_y)
    #     sys.exit("Error in moveVehicle_manhat - improper vehicle-person match")

    veh_x = vehicle.position_x
    veh_y = vehicle.position_y
    dist_x = abs(dest_x - veh_x)
    dist_y = abs(dest_y - veh_y)
    total_dist_manhat = dist_x + dist_y

    # if the vehicle is right next to the pickup/dropoff point
    if total_dist_manhat < Settings.delta_veh_dist:
        temp_veh_status = "at_destination"
        update_vehicle(t, person, vehicle, sub_area, temp_veh_status)
        vehicle.total_distance += total_dist_manhat

    else:  # move vehicle one step closer to destination
        proportion_x = dist_x / (dist_x + dist_y)
        proportion_y = dist_y / (dist_x + dist_y)

        if veh_x < dest_x:
            vehicle.position_x += proportion_x * Settings.delta_veh_dist
        else:
            vehicle.position_x += -1 * proportion_x * Settings.delta_veh_dist
        if veh_y < dest_y:
            vehicle.position_y += proportion_y * Settings.delta_veh_dist
        else:
            vehicle.position_y += -1 * proportion_y * Settings.delta_veh_dist

        vehicle.total_distance += Settings.delta_veh_dist

    return vehicle
##############################################################################


##############################################################################
# if more than one traveler demand request in vehicle - decide which demand to drop off first
# def get_next_drop(vehicle):
#     min_dist = 10000000000
#     for i_pass in vehicle.pass_inVeh:
#         dist = abs(vehicle.position_x - i_pass.dropoff_location_x) \
#                + abs(vehicle.position_y - i_pass.dropoff_location_y)
#         if dist < min_dist:
#             min_dist = dist
#             Win_Pass = i_pass
#     return Win_Pass
##############################################################################


##############################################################################
# returns position and dynamic distance to last drop-off point
def get_next_availability(vehicle):
    total_rem_dist = 0
    last_x = vehicle.position_x
    last_y = vehicle.position_y
    if vehicle.status == "enroute_pickup":
        i_pick = vehicle.next_pickup
        total_rem_dist += abs(vehicle.position_x - i_pick.pickup_location_x) \
                          + abs(vehicle.position_y - i_pick.pickup_location_y)
        total_rem_dist += abs(i_pick.dropoff_location_x - i_pick.pickup_location_x) \
                          + abs(i_pick.dropoff_location_y - i_pick.pickup_location_y)
        last_x = i_pick.dropoff_location_x
        last_y = i_pick.dropoff_location_y

    elif vehicle.status == "enroute_dropoff":
        i_pass = vehicle.next_drop
        total_rem_dist += abs(vehicle.position_x - i_pass.dropoff_location_x) \
                          + abs(vehicle.position_y - i_pass.dropoff_location_y)
        if vehicle.next_pickup.person_id >= 0:
            i_pick2 = vehicle.next_pickup
            total_rem_dist += abs(i_pass.dropoff_location_x - i_pick2.pickup_location_x) \
                              + abs(i_pass.dropoff_location_y - i_pick2.pickup_location_y)
            total_rem_dist += abs(i_pick2.dropoff_location_x - i_pick2.pickup_location_x) \
                              + abs(i_pick2.dropoff_location_y - i_pick2.pickup_location_y)
            last_x = i_pick2.dropoff_location_x
            last_y = i_pick2.dropoff_location_y
        else:
            last_x = i_pass.dropoff_location_x
            last_y = i_pass.dropoff_location_y

    return last_x, last_y, total_rem_dist


##############################################################################
# # Flo code: more general - works for shared-ride case
#
#     # inVeh (drop off order according to logic from get_next_drop)
#     tmp_list_pass_inVeh = vehicle.pass_inVeh[:]
#     while len(tmp_list_pass_inVeh) > 0:
#         min_dist = 10000000000
#         for i_pass in vehicle.pass_inVeh:
#             dist = abs(last_x - i_pass.dropoff_location_x) + abs(last_y - i_pass.dropoff_location_y)
#             if dist < min_dist:
#                 min_dist = dist
#                 Win_Pass = i_pass
#         last_x = Win_Pass.dropoff_location_x
#         last_y = Win_Pass.dropoff_location_y
#         total_rem_dist += min_dist
#         tmp_list_pass_inVeh.remove(Win_Pass)
#     # toPickup (assumption: list is already sorted)
#     for w_pass in vehicle.pass_toPickup:
#         q_dist = abs(last_x - w_pass.dropoff_location_x) + abs(last_y - w_pass.dropoff_location_y)
#         last_x = w_pass.dropoff_location_x
#         last_y = w_pass.dropoff_location_y
#         total_rem_dist += min_dist
#     return (last_x, last_y, total_rem_dist)
##############################################################################


##############################################################################
# vehicle is changing statuses - needs to be updated
def update_vehicle(t, person1, vehicle, sub_area, temp_veh_status):

    # Option 1
    if temp_veh_status == "at_destination":

        # Option 1a - AV reached pickup location
        if vehicle.status == "enroute_pickup":
            # dynamic information
            vehicle.current_load += person1.group_size
            vehicle.position_x = person1.pickup_location_x
            vehicle.position_y = person1.pickup_location_y
            vehicle.current_dest_x = person1.dropoff_location_x
            vehicle.current_dest_y = person1.dropoff_location_y
            vehicle.next_pickup = Person.Person
            vehicle.next_drop = person1
            vehicle.next_sub_area = Regions.SubArea
            vehicle.status = "enroute_dropoff"
            vehicle.reassigned = 0
            vehicle.curb_time_remain = Settings.curb_pick_time

            # output information
            vehicle.pass_picked_list.append(person1.person_id)
            vehicle.pickup_times.append(t)
            vehicle.pass_pick_count += 1

        # Option 1b - AV reached drop-off location
        elif vehicle.status == "enroute_dropoff":
            # dynamic information
            vehicle.current_load = vehicle.current_load - person1.group_size
            vehicle.position_x = person1.dropoff_location_x
            vehicle.position_y = person1.dropoff_location_y
            vehicle.curb_time_remain = Settings.curb_drop_time
            vehicle.next_drop = Person.Person
            vehicle.next_sub_area = Regions.SubArea
            vehicle.last_drop_time = t

            # Option 1b,i
            # after drop-off, check to see if AV has next traveler to pick up
            if vehicle.next_pickup.person_id >= 0:
                # dynamic information cont.
                vehicle.current_dest_x = vehicle.next_pickup.pickup_location_x
                vehicle.current_dest_y = vehicle.next_pickup.pickup_location_y
                # vehicle.next_pickup = vehicle.next_pickup
                vehicle.status = "enroute_pickup"

            # Option 1b,ii
            # after drop-off, vehicle is now idle
            else:
                # dynamic information cont.
                vehicle.current_dest_x = vehicle.position_x
                vehicle.current_dest_y = vehicle.position_y
                vehicle.next_pickup = Person.Person
                vehicle.status = "idle"

            # output information
            vehicle.pass_dropped_list.append(person1.person_id)
            vehicle.dropoff_times.append(t)
            vehicle.pass_drop_count += 1

        # Option 1c - AV reached relocation centroid
        elif vehicle.status == "relocating":
            # dynamic information
            vehicle.position_x = sub_area.relocation_destination[0]
            vehicle.position_y = sub_area.relocation_destination[1]
            vehicle.next_sub_area = Regions.Area
            vehicle.status = "idle"

            # output information
            vehicle.reposition_count += 1

        else:
            sys.exit("At Destination, no proper Vehicle Status")

    # Option 2 - idle AV assigned to pickup a traveler
    elif temp_veh_status == "base_assign":

        # dynamic information
        vehicle.current_dest_x = person1.pickup_location_x
        vehicle.current_dest_y = person1.pickup_location_y
        vehicle.next_pickup = person1
        vehicle.next_drop = Person.Person
        vehicle.next_sub_area = Regions.SubArea
        vehicle.status = "enroute_pickup"
        vehicle.reassigned = 0
        vehicle.curb_time_remain = 0

        # output information
        vehicle.pass_assgn_list.append(person1.person_id)
        vehicle.assigned_times.append(t)
        vehicle.pass_assgn_count += 1

    # Option 3 - En-route Drop-off AV assigned to its next pickup
    elif temp_veh_status == "new_assign":
        # dynamic information
        vehicle.next_pickup = person1
        vehicle.next_sub_area = Regions.SubArea
        # current load, position_x/y, current_dest_x/y, next_drop, status, reassigned, curb_remain_time - do not change

        # output information
        vehicle.pass_assgn_list.append(person1.person_id)
        vehicle.assigned_times.append(t)
        vehicle.pass_assgn_count += 1

    # Option 4 - AV reassigned from one traveler to another
    elif temp_veh_status == "reassign":

        # dynamic information
        vehicle.current_dest_x = person1.pickup_location_x
        vehicle.current_dest_y = person1.pickup_location_y
        vehicle.next_pickup = person1
        vehicle.next_sub_area = Regions.SubArea
        vehicle.status = "enroute_pickup"
        vehicle.reassigned = 1
        # current load, position_x/y, next_drop, status, curb_remain_time - do not change

        # output information
        vehicle.pass_assgn_list.append(person1.person_id)
        vehicle.assigned_times.append(t)
        vehicle.pass_assgn_count += 1

    # Option 5 - AV was assigned to a traveler, but no longer assigned to any traveler
    elif temp_veh_status == "unassign":

        # dynamic information
        vehicle.next_pickup = Person.Person
        vehicle.next_sub_area = Regions.SubArea
        if vehicle.next_drop.person_id < 0:
            vehicle.status = "idle"
            vehicle.current_dest_x = vehicle.position_x
            vehicle.current_dest_y = vehicle.position_y
        # current load, position_x/y, next_drop, status, reassigned, curb_remain_time - do not change

    # Option 6 - AV was assigned to relocate/reposition to a different subArea
    elif temp_veh_status == "relocate":

        # dynamic information
        vehicle.current_load = 0
        vehicle.current_dest_x = sub_area.relocation_destination[0]
        vehicle.current_dest_y = sub_area.relocation_destination[1]
        vehicle.next_pickup = Person.Person
        vehicle.next_drop = Person.Person
        vehicle.next_sub_area = sub_area
        vehicle.status = "relocating"
        vehicle.reassigned = 0

        # output information
        vehicle.reposition_count += 1

    else:
        sys.exit("update Vehicle - no Proper Vehicle Status")
