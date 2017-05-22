__author__ = 'Mike'

import Settings
import Person


class Vehicle(object):
    #static input features
    vehicle_id = -5
    start_location_x = -1.0
    start_location_y = -1.0
    capacity = -1

    #dynamic information needed for simulation
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
    reassign = 0

    #output information - update throughout simulation
    total_distance = 0.0
    time_in_use = 0
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
        #static input features        
        self.vehicle_id = vehicle_id
        self.start_location_x = start_location_x
        self.start_location_y = start_location_y
        self.capacity = capacity
        
        #dynamic information needed for simulation
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
        self.reassign = 0

        #output information - update throughout simulation
        self.total_distance = 0.0
        self.time_in_use = 0
        self.pass_assgn_list = []
        self.pass_picked_list = []
        self.pass_dropped_list = []
        self.assigned_times = []
        self.pickup_times = []
        self.dropoff_times = []
        self.pass_assgn_count = 0
        self.pass_pick_count = 0
        self.pass_drop_count = 0

#function to create an instance of class/object vehicle
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
#Function to move vehicle every time step
def moveVehicle_manhat(t, vehicle, person, opt_method):
    vehicle.time_in_use +=1
    dest_x = 0.0
    dest_y = 0.0

    if vehicle.state == "enroute_pickup":
        dest_x = person.pickup_location_x
        dest_y = person.pickup_location_y

    elif vehicle.state == "enroute_dropoff":
        dest_x = person.dropoff_location_x
        dest_y = person.dropoff_location_y

    else:
        print("Error in moveVehicle_manhat - wrong vehicle state")
    
    #check for bugs - keep in code
    if dest_x < 0 or dest_y < 0:
        print("Error in moveVehicle_manhat - inproper vehicle-person match")
            
    veh_x = vehicle.position_x
    veh_y = vehicle.position_y
    dist_x = abs(dest_x-veh_x)
    dist_y = abs(dest_y-veh_y)
    total_dist_manhat = dist_x + dist_y

   #if the vehicle is right next to the pickup/dropoff point
    if total_dist_manhat < (Settings.delta_veh_dist):
        vehicle = update_Vehicle(t, person, vehicle, opt_method)
        vehicle.total_distance += total_dist_manhat

    else: #move vehicle one step closer to destination
        proportion_x = dist_x/(dist_x + dist_y)
        proportion_y = dist_y/(dist_x + dist_y)

        if veh_x < dest_x:      vehicle.position_x += proportion_x * Settings.delta_veh_dist
        else:                   vehicle.position_x += -1 * proportion_x * Settings.delta_veh_dist
        if veh_y < dest_y:      vehicle.position_y += proportion_y * Settings.delta_veh_dist
        else:                   vehicle.position_y += -1 * proportion_y * Settings.delta_veh_dist
        vehicle.total_distance += Settings.delta_veh_dist

    return(vehicle)
##############################################################################

##############################################################################
# if more than one traveler demand request in vehicle - decide which demand to drop off first
def get_next_drop(vehicle):
    min_dist = 10000000000
    for i_pass in vehicle.pass_inVeh:
        dist = abs(vehicle.position_x - i_pass.dropoff_location_x)+ abs(vehicle.position_y - i_pass.dropoff_location_y)
        if dist < min_dist:
            min_dist = dist
            Win_Pass = i_pass
    return Win_Pass
##############################################################################
    
    
##############################################################################
# vehicle is changing states - needs to be updated
def update_Vehicle(t, person1, vehicle, opt_method):

  #For vehicles going from idle, to pickup, update Vehicle is the same for all opt methods
    if vehicle.state == "idle":
        vehicle.pass_toPickup.append(person1)
        vehicle.current_dest_x = person1.pickup_location_x
        vehicle.current_dest_y = person1.pickup_location_y
        vehicle.next_pickup = person1
        vehicle.state = state_enroute_pickup()

        vehicle.pass_assgn_list.append(person1.person_id)
        vehicle.assigned_times.append(t)
        vehicle.pass_assgn_count += 1

  #For all other vehicle state changes - update Vehicle varies by opt method
    else:
    #Opt method 1
        if opt_method == "match_idleOnly" or opt_method == "FCFS_nearestIdle" or opt_method == "FCFS_longestIdle" :
            #just picked up passenger - now need to drop him/her off
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

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            #just dropped off passenger - now vehicle is idle
            elif vehicle.state == "enroute_dropoff":
                vehicle.pass_inVeh.remove(person1)
                vehicle.current_load -= person1.group_size
                vehicle.position_x = person1.dropoff_location_x
                vehicle.position_y = person1.dropoff_location_y
                vehicle.next_drop = Person.Person
                vehicle.state = state_idle()

                vehicle.pass_dropped_list.append(person1.person_id)
                vehicle.dropoff_times.append(t)
                vehicle.pass_drop_count += 1
            else:
                "Error No Proper State"

    #Opt method 2
        elif opt_method == "match_RS" or opt_method == "match_RS_old" :
            #just picked up passenger - now need to drop him/her off, but 2 cases
            if vehicle.state == "enroute_pickup":
                #Case 1 - before pickup - no one else in vehicle
                if len(vehicle.pass_inVeh) == 0:
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

                #Case 2 - before pickup - other passenger(s) in vehicle
                else:
                    vehicle.pass_inVeh.append(person1)
                    vehicle.pass_toPickup.remove(person1)
                    vehicle.current_load += person1.group_size
                    if vehicle.current_load > vehicle.capacity:
                        print("Error in update Vehicle - vehicle.current_load > vehicle.capacity")
                    vehicle.position_x = person1.pickup_location_x
                    vehicle.position_y = person1.pickup_location_y
                    ######different for Rideshare#############################
                    next_drop_pass = get_next_drop(vehicle)
                    vehicle.next_drop = next_drop_pass
                    vehicle.current_dest_x = next_drop_pass.dropoff_location_x
                    vehicle.current_dest_y = next_drop_pass.dropoff_location_y
                    ##########################################################
                    vehicle.next_pickup = Person.Person
                    vehicle.state = state_enroute_dropoff()

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            #just dropped off passenger - 2 Cases
            elif vehicle.state == "enroute_dropoff":
                #Case 1: Only one person in vehicle before dropoff
                if len(vehicle.pass_inVeh) == 1:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_pickup = Person.Person
                    vehicle.next_drop = Person.Person
                    vehicle.state = state_idle()

                #Case 2: More than one person in vehicle before dropoff
                elif len(vehicle.pass_inVeh) > 1:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_pickup = Person.Person
                    ######different for Rideshare#############################
                    next_drop_pass = get_next_drop(vehicle)
                    vehicle.next_drop = next_drop_pass
                    vehicle.current_dest_x = next_drop_pass.dropoff_location_x
                    vehicle.current_dest_y = next_drop_pass.dropoff_location_y
                    vehicle.state = state_enroute_dropoff()
                    ##########################################################
                else:
                    print("Error in update vehicle - rideshare vehicle empty")

                vehicle.pass_dropped_list.append(person1.person_id)
                vehicle.dropoff_times.append(t)
                vehicle.pass_drop_count += 1

            #unique RS state - just got assigned to new request even though passenger in car
            elif vehicle.state == "RS_newRequest":
                vehicle.pass_toPickup.append(person1)
                vehicle.current_dest_x = person1.pickup_location_x
                vehicle.current_dest_y = person1.pickup_location_y
                vehicle.next_pickup = person1
                vehicle.next_drop = Person.Person
                vehicle.state = state_enroute_pickup()

                vehicle.pass_assgn_list.append(person1.person_id)
                vehicle.assigned_times.append(t)
                vehicle.pass_assgn_count += 1
            else:
                print("Error in update Vehicle - No Proper State for RS")


    #Opt method 3
        elif opt_method == "match_idleDrop":
            #just picked up passenger - now need to drop him/her off
            #Nothing different than base case
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

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            # just dropped off passenger - now idle - but might already have another pickup lined-up
            elif vehicle.state == "enroute_dropoff":
                #Case 1: No one else to pickup
                if len(vehicle.pass_toPickup) == 0:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_pickup = Person.Person
                    vehicle.next_drop = Person.Person
                    vehicle.state = state_idle()
                #Case 2: Already have next passenger to pickup
                else:
                    vehicle.pass_inVeh.remove(person1)
                    vehicle.current_load -= person1.group_size
                    vehicle.position_x = person1.dropoff_location_x
                    vehicle.position_y = person1.dropoff_location_y
                    vehicle.next_drop = Person.Person
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

            #another case unique to this opt method. enroute dropoff vehicle assigned to next passenger
            elif vehicle.state == "new_assign":
                vehicle.pass_toPickup.append(person1)
                vehicle.next_pickup = person1
                vehicle.state = state_enroute_dropoff()

                vehicle.pass_assgn_list.append(person1.person_id)
                vehicle.assigned_times.append(t)
                vehicle.pass_assgn_count += 1

            else:
                "Error No Proper State"

    #Opt method 4
        elif opt_method == "match_idlePick":
            #same as base idle-only case, except for a special case where vehicles are reassigned
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

                vehicle.pass_picked_list.append(person1.person_id)
                vehicle.pickup_times.append(t)
                vehicle.pass_pick_count += 1

            #just dropped off passenger - now idle
            elif vehicle.state == "enroute_dropoff":
                vehicle.pass_inVeh.remove(person1)
                vehicle.current_load -= person1.group_size
                vehicle.position_x = person1.dropoff_location_x
                vehicle.position_y = person1.dropoff_location_y
                vehicle.next_pickup = Person.Person
                vehicle.next_drop = Person.Person
                vehicle.state = state_idle()

                vehicle.pass_dropped_list.append(person1.person_id)
                vehicle.dropoff_times.append(t)
                vehicle.pass_drop_count += 1
                vehicle.reassign = 0

            #was en_route to  pickup, but have been reassigned
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
                vehicle.reassign = 1

            elif vehicle.state == "unassign":
                vehicle.pass_toPickup = []
                vehicle.current_dest_x = -1.0
                vehicle.current_dest_y = -1.0
                vehicle.next_pickup = Person.Person
                vehicle.state = state_idle()

            else:
                "Error No Proper State"

    return vehicle