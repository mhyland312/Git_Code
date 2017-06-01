__author__ = 'Mike'

import csv
import Vehicle
import Person
import Assignment_Algorithm as AA


def Main(hold_for, T_max, time_step, opt_method, veh_speed):
    
        
    ##################################################################################################
    #Input Information - Traveler Demand and Vehicle Initial Positions
    ##################################################################################################

    #read in information about all customers
    demandFile = open('../Inputs/Demand_Requests.csv', 'r')
    demand_reader = csv.reader(demandFile)
    People = []
    count = 0
    for i_row in demand_reader:
        count += 1
        if count == 1: mike = 1
        else:
            person_id = int(i_row[0])
            pickup_x = float(i_row[1])
            pickup_y = float(i_row[2])
            request_time = int(i_row[3])
            dropoff_x = float(i_row[4])
            dropoff_y = float(i_row[5])
            group_size = int(i_row[6])
            person_state = "unassigned"
            People.append(Person.make_Person(person_id, pickup_x, pickup_y, request_time, dropoff_x, dropoff_y, group_size, person_state))
    
    #read in information about all vehicles
    vehFile = open('../Inputs/Vehicles.csv', 'r')
    vehicle_reader = csv.reader(vehFile)
    Vehicles = []
    cnt = 0
    for j_row in vehicle_reader:
        cnt += 1
        if cnt == 1: mike = 1
        else:
            vehicle_id = int(j_row[0])
            start_x = float(j_row[1])
            start_y = float(j_row[2])
            capacity = int(j_row[3])
            veh_state = "idle"
            Vehicles.append(Vehicle.make_Vehicle(vehicle_id, start_x, start_y, capacity, veh_state))
    
    
    
    ##################################################################################################
    #Simulation
    ##################################################################################################

    #Initialize Vectors
    i_person = 0
    pass_noAssign_Q = []
    pass_noPick_Q = []
    fleet_size = len(Vehicles)
    veh_idle_Q = Vehicles[0:fleet_size]
    veh_pick_Q = []
    veh_drop_Q = []
    remaining_persons = []
    
    #begin simulation
    for t in range(0, T_max, time_step ):

    # move en_route dropoff vehicles
        for i_veh_drop in veh_drop_Q:
            person_id_drop = i_veh_drop.next_drop.person_id
            person_drop = People[person_id_drop]
    
            veh_id_drop = i_veh_drop.vehicle_id
            temp_check_RS = i_veh_drop.next_drop
            Vehicles[veh_id_drop] = Vehicle.moveVehicle_manhat(t, i_veh_drop, person_drop, opt_method)

            #vehicle just dropped someone off and is now idle
            if i_veh_drop.state == "idle":
                veh_idle_Q.append(i_veh_drop)
                veh_drop_Q.remove(i_veh_drop)
                People[person_id_drop] = Person.update_Person(t, person_drop, i_veh_drop)

            #vehicle just dropped someone off but already has a next pickup point
            elif i_veh_drop.state == "enroute_pickup":
                People[person_id_drop] = Person.update_Person(t, person_drop, i_veh_drop)
                veh_pick_Q.append(i_veh_drop)
                veh_drop_Q.remove(i_veh_drop)

            #vehicle just dropped someone off but is not empty and now is going to dropoff the next person
            elif i_veh_drop.state == "enroute_dropoff" and (i_veh_drop.next_drop != temp_check_RS):
                People[person_id_drop] = Person.update_Person(t, person_drop, i_veh_drop)


    ##################################################################################################
    #move en_route pickup vehicles
        for ii_veh_pick in veh_pick_Q:
            person_id_pick = ii_veh_pick.next_pickup.person_id
            person_pick = People[person_id_pick]
    
            veh_id_pick = ii_veh_pick.vehicle_id
            Vehicles[veh_id_pick] = Vehicle.moveVehicle_manhat(t, ii_veh_pick, person_pick, opt_method)
    
            if ii_veh_pick.state == "enroute_dropoff":
                pass_noPick_Q.remove(person_pick)
                veh_drop_Q.append(ii_veh_pick)
                veh_pick_Q.remove(ii_veh_pick)
                People[person_id_pick] = Person.update_Person(t, person_pick, ii_veh_pick)
    
    
    ##################################################################################################
    #add new demand requests that just arrived to the queue of waiting passengers
        if i_person < len(People):
            if People[i_person].request_time <= t:
                pass_noAssign_Q.append(People[i_person])
                i_person += 1

    
    ###################################################################################################
    #Every X seconds assign passengers in the waiting queue to a vehicle
        if t%hold_for == 0:
            if len(pass_noAssign_Q) > 0 and len(veh_idle_Q) > 0: #Mike - probably want to check removing second if condition
                #return index of vehicle_idle_queue for every passenger
                pass_veh_assgn = AA.assign_veh(veh_idle_Q, veh_pick_Q, veh_drop_Q, pass_noAssign_Q, pass_noPick_Q, opt_method, t)

                remaining_persons = []
                used_vehicles = []
                old_veh_pick_Q = veh_pick_Q[0:len(veh_pick_Q)]
                for [i_pass, j_vehicle] in pass_veh_assgn:
                    #passenger is not assigned to a real vehicle, and the person is real
                    if j_vehicle.vehicle_id < 0 and i_pass.person_id >= 0 :
                        remaining_persons.append(i_pass)
                        if i_pass in pass_noPick_Q:
                            pass_noPick_Q.remove(i_pass)
                            People[i_pass.person_id].state = "unassigned"
                            People[i_pass.person_id].vehicle_id = -4

                    #passenger re-assigned to vehicle he/she already were assigned to
                    elif j_vehicle.next_pickup == i_pass:
                        used_vehicles.append(j_vehicle)

                    #passenger assigned to a real vehicle
                    elif j_vehicle.vehicle_id >= 0:
                        used_vehicles.append(j_vehicle)

                        # passenger assigned to an idle vehicle
                        if j_vehicle in veh_idle_Q:
                            #if passenger already had a vehicle coming towards it, but then assigned a new vehicle
                            if i_pass.vehicle_id >= 0:
                                i_pass.state = "reassign"
                            else:
                                pass_noPick_Q.append(i_pass)
                            People[i_pass.person_id] = Person.update_Person(t, i_pass, j_vehicle)
                            Vehicles[j_vehicle.vehicle_id] = Vehicle.update_Vehicle(t, i_pass, j_vehicle, opt_method)
                            veh_pick_Q.append(j_vehicle)
                        #passenger assigned to non-idle vehicle
                        else:
                            if opt_method == "match_RS" or opt_method == "match_RS_old":
                                pass_noPick_Q.append(i_pass)
                                People[i_pass.person_id] = Person.update_Person(t, i_pass, j_vehicle)
                                veh_drop_Q.remove(j_vehicle)
                                j_vehicle.state = "RS_newRequest"
                                Vehicles[j_vehicle.vehicle_id] = Vehicle.update_Vehicle(t, i_pass, j_vehicle, opt_method)
                                veh_pick_Q.append(j_vehicle)
                            
                            elif opt_method == "match_idleDrop":
                                pass_noPick_Q.append(i_pass)
                                People[i_pass.person_id] = Person.update_Person(t, i_pass, j_vehicle)
                                j_vehicle.state = "new_assign"
                                Vehicles[j_vehicle.vehicle_id] = Vehicle.update_Vehicle(t, i_pass, j_vehicle, opt_method)

                            elif opt_method == "match_idlePick":
                                j_vehicle.state = "reassign"
                                if i_pass.vehicle_id >= 0:
                                    i_pass.state = "reassign"
                                else:
                                    pass_noPick_Q.append(i_pass)
                                People[i_pass.person_id] = Person.update_Person(t, i_pass, j_vehicle)
                                Vehicles[j_vehicle.vehicle_id] = Vehicle.update_Vehicle(t, i_pass, j_vehicle, opt_method)

                            #elif opt_method == "match_idlePickDrop":




                    else:
                        print("Error in Assignment!")

                len_remain = len(remaining_persons)
                pass_noAssign_Q = remaining_persons[0:len_remain]

                #remove vehicles that have been  assigned to a passenger from the vehicle_idle_queue
                for i_used in used_vehicles:
                    if i_used in veh_idle_Q:
                        veh_idle_Q.remove(i_used)

                #vehicle was going to pick up traveler, now it is not
                if opt_method == "match_idlePick":
                    for ijk_veh in old_veh_pick_Q:
                        if ijk_veh not in used_vehicles:
                            ijk_veh.state = "unassign"
                            Vehicles[ijk_veh.vehicle_id] = Vehicle.update_Vehicle(t, Person.Person, ijk_veh, opt_method)
                            veh_pick_Q.remove(ijk_veh)
                            veh_idle_Q.append(ijk_veh)


    ##################################################################################################
    #Simulation Over
    ##################################################################################################






    answer = []
    #hold_for, T_max, time_step, opt_method
    file_string1 = '../Results/trvlr_results'+ '_hold' + str(hold_for) + '_fleet' + str(fleet_size) + '_opt' + str(opt_method)  +'.csv'
    csv_traveler = open(file_string1, 'w')
    traveler_writer = csv.writer(csv_traveler, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    traveler_writer.writerow(["person_id", "base_ivtt", "simulate_ivtt", "wait_assgn_time","wait_pick_time", "vehicle", "old_veh", "rideshare"])
    non_rideshare_count = 0
    cum_real_ivtt = 0
    cum_base_ivtt = 0
    cum_wait_assgn = 0
    cum_wait_pick = 0
    #cum_missed_pass = 0
    cum_rideshare = 0
    
    start = round(0.2*len(People))
    end = round(0.8*len(People))

    for j_person in People[start:end]:
        non_rideshare_count += 1
        cum_real_ivtt += j_person.travel_time
        base_ivtt = j_person.in_veh_dist/veh_speed
        cum_base_ivtt += j_person.in_veh_dist/veh_speed
        cum_wait_assgn += j_person.wait_assgn_time
        cum_wait_pick += j_person.wait_pick_time
        cum_rideshare += j_person.rideshare
        #if j_person.wait_assgn_time < 0: #also need did not drop off yet
         #   cum_missed_pass += 1
          #  if j_person.wait_pick_time < 0:

        traveler_writer.writerow([j_person.person_id, base_ivtt, j_person.travel_time, j_person.wait_assgn_time, j_person.wait_pick_time, j_person.vehicle_id, j_person.old_vehicles, j_person.rideshare])


    answer.append(int(cum_real_ivtt/60.0))
    answer.append(int(cum_base_ivtt/60.0))
    answer.append(int(cum_wait_assgn/60.0))
    answer.append(int(cum_wait_pick/60.0))
    num_people = len(People)*1.0
    answer.append(cum_rideshare/num_people)


    file_string2 = '../Results/veh_results'+ '_hold' + str(hold_for) + '_fleet' + str(fleet_size) + '_opt' + str(opt_method)  +'.csv'
    csv_vehicle = open(file_string2, 'w')
    vehicle_writer = csv.writer(csv_vehicle, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    vehicle_writer.writerow(["vehicle_id", "distance", "pass_assgn", "pass_pick", "pass_drop", "pass_drop_list"])
    cum_distance = 0
    for k_vehicle in Vehicles:
        cum_distance += k_vehicle.total_distance
        vehicle_writer.writerow([k_vehicle.vehicle_id, k_vehicle.total_distance, k_vehicle.pass_assgn_count,
                                 k_vehicle.pass_pick_count, k_vehicle.pass_drop_count, k_vehicle.pass_dropped_list  ])

    vehicle_writer.writerow(["cum_distance", cum_distance/5280.0])

    answer.append(int(cum_distance/5280.0))
    
    answer.append(len(pass_noAssign_Q))
    answer.append(len(pass_noAssign_Q) + len(pass_noPick_Q))
    

    return (answer)