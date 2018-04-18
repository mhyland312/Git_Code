__author__ = 'Mike'

import Settings
import Person
import sys


class Vehicle(object):
    # static input features
    vehicle_id = -5
    start_location_x = -1.0
    start_location_y = -1.0
    capacity = -1

    # dynamic information needed for simulation
    pass_inVeh = []
    pass_toPickup = []
    current_load = 0
    position_x = start_location_x
    position_y = start_location_y
    current_dest_x = -1.0
    current_dest_y = -1.0
    next_pickup = Person.Person
    next_drop = Person.Person
    state = "string"
    reassigned = 0
    curb_time_remain = 0

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

    # The class "constructor" - It's actually an initializer
    def __init__(self, vehicle_id, start_location_x, start_location_y, capacity, state):
        # static input features
        self.vehicle_id = vehicle_id
        self.start_location_x = start_location_x
        self.start_location_y = start_location_y
        self.capacity = capacity

        # dynamic information needed for simulation
        self.pass_inVeh = []
        self.pass_toPickup = []
        self.current_load = 0
        self.position_x = start_location_x
        self.position_y = start_location_y
        self.current_dest_x = -1
        self.current_dest_y = -1
        self.next_pickup = Person.Person
        self.next_drop = Person.Person
        self.state = state
        self.reassigned = 0
        self.curb_time_remain = 0

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


# function to create an instance of class/object vehicle
def make_Vehicle(vehicle_id, start_location_x, start_location_y, capacity, state):
    vehicle1 = Vehicle(vehicle_id, start_location_x, start_location_y, capacity, state)
    return vehicle1


##############################################################################



##update vehicle state########################################################
def state_enroute_pickup():
    state = "enroute_pickup"
    return state


def state_enroute_dropoff():
    state = "enroute_dropoff"
    return state


def state_idle():
    state = "idle"
    return state


##############################################################################


##############################################################################
# Function to move vehicle every time step
def moveVehicle_manhat(t, vehicle, person, opt_method):
    # vehicle.time_in_use +=1
    dest_x = 0.0
    dest_y = 0.0

    if vehicle.state == "enroute_pickup":
        dest_x = person.pickup_location_x
        dest_y = person.pickup_location_y
        if vehicle.current_load > 0:
            vehicle.loaded_distance += Settings.delta_veh_dist
        else:
            vehicle.empty_distance += Settings.delta_veh_dist

    elif vehicle.state == "enroute_dropoff":
        dest_x = person.dropoff_location_x
        dest_y = person.dropoff_location_y
        vehicle.loaded_distance += Settings.delta_veh_dist

    else:
        sys.exit("Error in moveVehicle_manhat - wrong vehicle state")

    # check for bugs - keep in code
    if dest_x < 0.0 or dest_y < 0.0:
        print(dest_x, dest_y)
        sys.exit("Error in moveVehicle_manhat - improper vehicle-person match")

    veh_x = vehicle.position_x
    veh_y = vehicle.position_y
    dist_x = abs(dest_x - veh_x)
    dist_y = abs(dest_y - veh_y)
    total_dist_manhat = dist_x + dist_y

    # if the vehicle is right next to the pickup/dropoff point
    if total_dist_manhat < (Settings.delta_veh_dist):
        vehicle = update_Vehicle(t, person, vehicle, opt_method)
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

    return (vehicle)


##############################################################################

##############################################################################
# if more than one traveler demand request in vehicle - decide which demand to drop off first
def get_next_drop(vehicle):
    min_dist = 10000000000
    for i_pass in vehicle.pass_inVeh:
        dist = abs(vehicle.position_x - i_pass.dropoff_location_x) + abs(vehicle.position_y - i_pass.dropoff_location_y)
        if dist < min_dist:
            min_dist = dist
            Win_Pass = i_pass
    return Win_Pass


##############################################################################



##############################################################################
# returns position and dynamic distance of last drop-off point
def get_final_availability(vehicle):
    total_dist = 0
    last_x = vehicle.position_x
    last_y = vehicle.position_y
    # inVeh (drop off order according to logic from get_next_drop)
    tmp_list_pass_inVeh = vehicle.pass_inVeh[:]
    while len(tmp_list_pass_inVeh) > 0:
        min_dist = 10000000000
        for i_pass in vehicle.pass_inVeh:
            dist = abs(last_x - i_pass.dropoff_location_x) + abs(last_y - i_pass.dropoff_location_y)
            if dist < min_dist:
                min_dist = dist
                Win_Pass = i_pass
        last_x = Win_Pass.dropoff_location_x
        last_y = Win_Pass.dropoff_location_y
        total_dist += min_dist
        tmp_list_pass_inVeh.remove(Win_Pass)
    # toPickup (assumption: list is already sorted)
    for w_pass in vehicle.pass_toPickup:
        q_dist = abs(last_x - w_pass.dropoff_location_x) + abs(last_y - w_pass.dropoff_location_y)
        last_x = w_pass.dropoff_location_x
        last_y = w_pass.dropoff_location_y
        total_dist += min_dist
    return (last_x, last_y, total_dist)


##############################################################################



##############################################################################
def update_Vehicle_Assgnmnt(t, person_2, vehicle_2):
    # check to see if Vehicle is real!
    vehicle_2.pass_toPickup.insert(0, person_2)
    vehicle_2.current_dest_x = person_2.pickup_location_x
    vehicle_2.current_dest_y = person_2.pickup_location_y
    if vehicle_2.next_pickup.person_id >= 0 and vehicle_2.next_pickup.person_id != person_2.person_id:
        vehicle_2.reassigned = 1
    vehicle_2.next_pickup = person_2
    vehicle_2.state = state_enroute_pickup()

    vehicle_2.pass_assgn_list.append(person_2)
    vehicle_2.assigned_times.append(t)
    vehicle_2.pass_assgn_count += 1


##############################################################################



##############################################################################
# vehicle is changing states - needs to be updated
def update_Vehicle(t, person1, vehicle, opt_method):
    # For vehicles going from idle, to pickup, update Vehicle is the same for all opt methods
    if vehicle.state == "idle":
        vehicle.pass_toPickup.append(person1)
        vehicle.current_dest_x = person1.pickup_location_x
        vehicle.current_dest_y = person1.pickup_location_y
        vehicle.next_pickup = person1
        vehicle.state = state_enroute_pickup()

        vehicle.pass_assgn_list.append(person1.person_id)
        vehicle.assigned_times.append(t)
        vehicle.pass_assgn_count += 1

        # For all other vehicle state changes - update Vehicle varies by opt method
    else:
        # comment:
        # necessity to treat queued passengers in FCFS_drop_smartNN
        # 1) either add code from match_idleDrop to FCFS
        # 2) changing opt_method for FCFS from FCFS_drop_smartNN
        # the first should be the cleaner solution, but to reduce risk of unwanted control structure, I will use the second method and modify the string
        if opt_method == "FCFS_drop_smartNN" or "FCFS_drop_smartNN2":
            opt_method = "match_idleDrop"
            # Opt method 1
        if opt_method == "match_idleOnly" or "FCFS" in opt_method:
            # just picked up passenger - now need to drop him/her off
            if vehicle.state == "enroute_pickup":
                vehicle.pass_inVeh.append(person1)
                vehicle.pass_toPickup.remove(person1)
                vehicle.current_load += person1.group_size
                vehicle.position_x = person1.pickup_location_x
                vehicle.position_y = person1.pickup_location_y
                vehicle.current_dest_x = person1.dropoff_location_x
                vehicle.current_dest_y = person1.dropoff_location_y
                vehicle.next_pickup = Person.Person
                vehicle.next_drop = person1
                vehicle.state = state_enroute_dropoff()
                vehicle.curb_time_remain = Settings.curb_pick_time

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            # just dropped off passenger - now vehicle is idle
            elif vehicle.state == "enroute_dropoff":
                vehicle.pass_inVeh.remove(person1)
                vehicle.current_load -= person1.group_size
                vehicle.position_x = person1.dropoff_location_x
                vehicle.position_y = person1.dropoff_location_y
                vehicle.next_drop = Person.Person
                vehicle.state = state_idle()
                vehicle.curb_time_remain = Settings.curb_drop_time

                vehicle.pass_dropped_list.append(person1.person_id)
                vehicle.dropoff_times.append(t)
                vehicle.pass_drop_count += 1
            else:
                print("Error No Proper State - Opt Method 1")

                # Opt method 3
        elif opt_method == "match_idleDrop":
            # just picked up passenger - now need to drop him/her off
            # Nothing different than base case
            if vehicle.state == "enroute_pickup":
                vehicle.pass_inVeh.append(person1)
                vehicle.pass_toPickup.remove(person1)
                vehicle.current_load += person1.group_size
                vehicle.position_x = person1.pickup_location_x
                vehicle.position_y = person1.pickup_location_y
                vehicle.current_dest_x = person1.dropoff_location_x
                vehicle.current_dest_y = person1.dropoff_location_y
                vehicle.next_pickup = Person.Person
                vehicle.next_drop = person1
                vehicle.state = state_enroute_dropoff()
                vehicle.curb_time_remain = Settings.curb_pick_time

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            # just dropped off passenger - now idle - but might already have another pickup lined-up
            elif vehicle.state == "enroute_dropoff":
                # Case 1: No one else to pickup
                if len(vehicle.pass_toPickup) == 0:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_pickup = Person.Person
                    vehicle.next_drop = Person.Person
                    vehicle.state = state_idle()
                    vehicle.curb_time_remain = Settings.curb_drop_time
                # Case 2: Already have next passenger to pickup
                else:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_drop = Person.Person
                    vehicle.curb_time_remain = Settings.curb_drop_time
                    ####different for idleDrop##########
                    vehicle.next_pickup = vehicle.pass_toPickup[0]
                    vehicle.state = state_enroute_pickup()
                    next_pickup_pass = vehicle.next_pickup
                    vehicle.current_dest_x = next_pickup_pass.pickup_location_x
                    vehicle.current_dest_y = next_pickup_pass.pickup_location_y
                    ######################################

                vehicle.pass_dropped_list.append(person1.person_id)
                vehicle.dropoff_times.append(t)
                vehicle.pass_drop_count += 1

            # another case unique to this opt method. enroute dropoff vehicle assigned to next passenger
            elif vehicle.state == "new_assign":
                vehicle.pass_toPickup.append(person1)
                vehicle.next_pickup = person1
                vehicle.state = state_enroute_dropoff()

                vehicle.pass_assgn_list.append(person1.person_id)
                vehicle.assigned_times.append(t)
                vehicle.pass_assgn_count += 1

            else:
                print("Error No Proper State - Opt Method 3")

                # Opt method 4
        elif opt_method == "match_idlePick":
            # same as base idle-only case, except for a special case where vehicles are reassigned
            if vehicle.state == "enroute_pickup":
                vehicle.pass_inVeh.append(person1)
                vehicle.pass_toPickup.remove(person1)
                vehicle.current_load += person1.group_size
                vehicle.position_x = person1.pickup_location_x
                vehicle.position_y = person1.pickup_location_y
                vehicle.current_dest_x = person1.dropoff_location_x
                vehicle.current_dest_y = person1.dropoff_location_y
                vehicle.next_pickup = Person.Person
                vehicle.next_drop = person1
                vehicle.state = state_enroute_dropoff()
                vehicle.curb_time_remain = Settings.curb_pick_time

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            # just dropped off passenger - now idle
            elif vehicle.state == "enroute_dropoff":
                vehicle.pass_inVeh.remove(person1)
                vehicle.current_load -= person1.group_size
                vehicle.position_x = person1.dropoff_location_x
                vehicle.position_y = person1.dropoff_location_y
                vehicle.next_pickup = Person.Person
                vehicle.next_drop = Person.Person
                vehicle.state = state_idle()
                vehicle.curb_time_remain = Settings.curb_drop_time

                vehicle.pass_dropped_list.append(person1.person_id)
                vehicle.dropoff_times.append(t)
                vehicle.pass_drop_count += 1
                vehicle.reassigned = 0

            # was en_route to  pickup, but have been reassigned
            elif vehicle.state == "reassign":
                ####different#######
                vehicle.pass_toPickup.remove(vehicle.pass_toPickup[0])
                ######################################
                vehicle.pass_toPickup.append(person1)
                vehicle.current_dest_x = person1.pickup_location_x
                vehicle.current_dest_y = person1.pickup_location_y
                vehicle.next_pickup = person1
                vehicle.state = state_enroute_pickup()

                vehicle.pass_assgn_list.append(person1.person_id)
                vehicle.assigned_times.append(t)
                vehicle.pass_assgn_count += 1
                vehicle.reassigned = 1

            elif vehicle.state == "unassign":
                vehicle.pass_toPickup = []
                vehicle.current_dest_x = -1.0
                vehicle.current_dest_y = -1.0
                vehicle.next_pickup = Person.Person
                vehicle.state = state_idle()
                vehicle.reassigned = 0
            else:
                sys.exit("Error No Proper State - Opt Method 4")

                # Opt method 5
        elif opt_method == "match_idlePickDrop":

            # same as base idle-only case, except for a special case where vehicles are reassigned
            if vehicle.state == "enroute_pickup":
                vehicle.pass_inVeh.append(person1)
                vehicle.pass_toPickup.remove(person1)
                vehicle.current_load += person1.group_size
                vehicle.position_x = person1.pickup_location_x
                vehicle.position_y = person1.pickup_location_y
                vehicle.current_dest_x = person1.dropoff_location_x
                vehicle.current_dest_y = person1.dropoff_location_y
                vehicle.next_pickup = Person.Person
                vehicle.next_drop = person1
                vehicle.state = state_enroute_dropoff()
                vehicle.curb_time_remain = Settings.curb_pick_time

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            # just dropped off passenger - now idle - but might already have another pickup lined-up
            elif vehicle.state == "enroute_dropoff":
                # Case 1: No one else to pickup
                if len(vehicle.pass_toPickup) == 0:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_pickup = Person.Person
                    vehicle.next_drop = Person.Person
                    vehicle.state = state_idle()
                    vehicle.curb_time_remain = Settings.curb_drop_time
                # Case 2: Already have next passenger to pickup
                else:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_drop = Person.Person
                    vehicle.curb_time_remain = Settings.curb_drop_time
                    ####different for idleDrop##########
                    vehicle.next_pickup = vehicle.pass_toPickup[0]
                    vehicle.state = state_enroute_pickup()
                    next_pickup_pass = vehicle.next_pickup
                    vehicle.current_dest_x = next_pickup_pass.pickup_location_x
                    vehicle.current_dest_y = next_pickup_pass.pickup_location_y
                    ######################################

                vehicle.pass_dropped_list.append(person1.person_id)
                vehicle.dropoff_times.append(t)
                vehicle.pass_drop_count += 1
                vehicle.reassigned = 0

            # another case unique to this opt method. enroute dropoff vehicle assigned to next passenger
            elif vehicle.state == "new_assign":
                if vehicle.next_pickup.person_id >= 0:
                    vehicle.pass_toPickup.remove(vehicle.pass_toPickup[0])

                vehicle.pass_toPickup.append(person1)
                vehicle.next_pickup = person1
                vehicle.state = state_enroute_dropoff()

                vehicle.pass_assgn_list.append(person1.person_id)
                vehicle.assigned_times.append(t)
                vehicle.pass_assgn_count += 1

            # was en_route to  pickup, but have been reassigned
            elif vehicle.state == "reassign":
                ####different#######
                vehicle.pass_toPickup.remove(vehicle.pass_toPickup[0])
                ######################################
                vehicle.pass_toPickup.append(person1)
                vehicle.current_dest_x = person1.pickup_location_x
                vehicle.current_dest_y = person1.pickup_location_y
                vehicle.next_pickup = person1
                vehicle.state = state_enroute_pickup()

                vehicle.pass_assgn_list.append(person1.person_id)
                vehicle.assigned_times.append(t)
                vehicle.pass_assgn_count += 1
                vehicle.reassigned = 1

            elif vehicle.state == "unassign":
                vehicle.pass_toPickup = []
                vehicle.reassigned = 0

                vehicle.next_pickup = Person.Person

                if vehicle.next_drop.person_id >= 0:
                    vehicle.state = state_enroute_dropoff()
                else:
                    vehicle.state = state_idle()
                    vehicle.current_dest_x = -1.0
                    vehicle.current_dest_y = -1.0
            else:
                sys.exit("Error No Proper State - Opt Method 5")

    return vehicle