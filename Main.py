import csv
import Vehicle
import Person
import Assignment_Algorithm as AA
import numpy
import sys
__author__ = 'Mike'


def main(hold_for, T_max, time_step, opt_method, veh_speed, i_run, taxi):

    ##################################################################################################
    # Input Information - Traveler Demand and Vehicle Initial Positions
    ##################################################################################################

    # read in information about all customers
    if taxi:
        file_str = "../Inputs/Taxi_Demand_Day" + str(i_run) + "_Sample.csv"
    else:
        file_str = "../Inputs/Demand_Requests.csv"
    demand_file = open(file_str, 'r')

    demand_reader = csv.reader(demand_file)
    People = []
    count = 0
    for i_row in demand_reader:
        count += 1
        if count > 1:
            person_id = int(i_row[0])
            request_time = int(i_row[1])
            pickup_x = float(i_row[2])
            pickup_y = float(i_row[3])
            dropoff_x = float(i_row[4])
            dropoff_y = float(i_row[5])
            group_size = int(i_row[6])
            person_state = "unassigned"
            People.append(Person.make_Person(person_id, pickup_x, pickup_y, request_time, dropoff_x, dropoff_y,
                                             group_size, person_state))

    # read in information about all vehicles
    # vehFile = open('../Inputs/Vehicles_Taxi.csv', 'r')
    if taxi:
        file_str2 = "../Inputs/Vehicles_Taxi.csv"
    else:
        file_str2 = "../Inputs/Vehicles_Taxi.csv"

    veh_file = open(file_str2, 'r')
    vehicle_reader = csv.reader(veh_file)
    Vehicles = []
    cnt = 0
    for j_row in vehicle_reader:
        cnt += 1
        if cnt > 1:
            vehicle_id = int(j_row[0])
            start_x = float(j_row[1])
            start_y = float(j_row[2])
            capacity = int(j_row[3])
            veh_state = "idle"
            Vehicles.append(Vehicle.make_Vehicle(vehicle_id, start_x, start_y, capacity, veh_state))

    ##################################################################################################
    # Simulation
    ##################################################################################################

    # Initialize Vectors
    i_person = 0
    pass_no_assign__q = []
    pass_no_pick__q = []
    fleet_size = len(Vehicles)
    veh_idle__q = Vehicles[0:fleet_size]
    veh_pick__q = []
    veh_drop__q = []

    used_vehicles = []

    # Begin simulation
    for t in range(0, T_max, time_step):

        ##################################################################################################
        # Check to make sure vehicles have not been deleted or added to multiple queues
        if len(veh_idle__q) + len(veh_pick__q) + len(veh_drop__q) != len(Vehicles):
            sys.exit("something wrong with vehicle queues")

        ##################################################################################################
        # move en_route drop-off vehicles
        for i_veh_drop in veh_drop__q:
            if i_veh_drop.curb_time_remain > 0:
                i_veh_drop.curb_time_remain = i_veh_drop.curb_time_remain - 1

            else:
                person_id_drop = i_veh_drop.next_drop.person_id
                person_drop = People[person_id_drop]

                veh_id_drop = i_veh_drop.vehicle_id
                Vehicles[veh_id_drop] = Vehicle.moveVehicle_manhat(t, i_veh_drop, person_drop, opt_method)

                # vehicle just dropped someone off and is now idle
                if i_veh_drop.state == "idle":
                    veh_idle__q.append(i_veh_drop)
                    veh_drop__q.remove(i_veh_drop)
                    People[person_id_drop] = Person.update_Person(t, person_drop, i_veh_drop)

                # vehicle just dropped someone off but already has a next pickup point
                elif i_veh_drop.state == "enroute_pickup":
                    People[person_id_drop] = Person.update_Person(t, person_drop, i_veh_drop)
                    veh_pick__q.append(i_veh_drop)
                    veh_drop__q.remove(i_veh_drop)

    ##################################################################################################
    # move en_route pickup vehicles
        for ii_veh_pick in veh_pick__q:
            if ii_veh_pick.curb_time_remain > 0:
                ii_veh_pick.curb_time_remain = ii_veh_pick.curb_time_remain - 1
            else:
                person_id_pick = ii_veh_pick.next_pickup.person_id
                person_pick = People[person_id_pick]

                veh_id_pick = ii_veh_pick.vehicle_id
                Vehicles[veh_id_pick] = Vehicle.moveVehicle_manhat(t, ii_veh_pick, person_pick, opt_method)

                if ii_veh_pick.state == "enroute_dropoff":
                    pass_no_pick__q.remove(person_pick)
                    veh_drop__q.append(ii_veh_pick)
                    veh_pick__q.remove(ii_veh_pick)
                    People[person_id_pick] = Person.update_Person(t, person_pick, ii_veh_pick)

    ##################################################################################################
    # update idle vehicles curb wait time
        for iii_veh_idle in veh_idle__q:
            if iii_veh_idle.curb_time_remain > 0:
                iii_veh_idle.curb_time_remain = iii_veh_idle.curb_time_remain - 1

    ##################################################################################################
    # check if there are new requests
        if i_person < len(People):
            while People[i_person].request_time <= t:
                pass_no_assign__q.append(People[i_person])
                i_person += 1
                if i_person == len(People):
                    break

     ###################################################################################################
    # Assign AVs to traveler requests

    ###################################################################################################
    # Assign using FCFS methods
        if "FCFS" in opt_method:
            if len(pass_no_assign__q) > 0 and len(veh_idle__q + veh_drop__q) > 0:

                pass_veh_assgn = AA.assign_veh_fcfs(veh_idle__q, veh_drop__q, pass_no_assign__q, opt_method)

                remaining_persons = []
                used_vehicles = []

                for [i_pass, j_vehicle] in pass_veh_assgn:

                    # passenger not assigned
                    if j_vehicle.vehicle_id < 0:
                        remaining_persons.append(i_pass)

                    # passenger assigned to a real vehicle
                    elif j_vehicle.vehicle_id >= 0:
                        used_vehicles.append(j_vehicle)

                        # passenger assigned to an idle vehicle
                        if j_vehicle in veh_idle__q:
                            veh_pick__q.append(j_vehicle)
                            pass_no_pick__q.append(i_pass)

                        # passenger assigned to non-idle vehicle
                        else:
                            pass_no_pick__q.append(i_pass)
                            j_vehicle.state = "new_assign"

                        People[i_pass.person_id] = Person.update_Person(t, i_pass, j_vehicle)
                        Vehicles[j_vehicle.vehicle_id] = Vehicle.update_Vehicle(t, i_pass, j_vehicle, opt_method)

                    else:
                        sys.exit("Error in Assignment!")

                len_remain = len(remaining_persons)
                pass_no_assign__q = remaining_persons[0:len_remain]

                # remove vehicles that have been assigned to a passenger from the vehicle_idle_queue
                for i_used in used_vehicles:
                    if i_used in veh_idle__q:
                        veh_idle__q.remove(i_used)

    ###################################################################################################
    # Assign using Optimization-based methods
        else:
            # Every X seconds assign passengers in the waiting queue to a vehicle
            if t % hold_for == 0:
                # if len(pass_no_assign__q) > 0 and len(veh_idle__q) > 0: # Mike -  check removing second if condition
                if len(pass_no_assign__q) > 0:
                    pass_veh_assign1 = []
                    temp_veh_pick__q = veh_pick__q[0:len(veh_pick__q)]
                    temp_pass_no_pick__q = pass_no_pick__q[0:len(pass_no_pick__q)]

                    for j_car in veh_pick__q:
                        if j_car.next_pickup.reassigned == 1:
                            pass_veh_assign1.append([j_car.next_pickup, j_car])
                            temp_veh_pick__q.remove(j_car)
                            temp_pass_no_pick__q.remove(j_car.next_pickup)

                    pass_veh_assign2 = AA.assign_veh_opt(veh_idle__q, temp_veh_pick__q, veh_drop__q,
                                                         pass_no_assign__q, temp_pass_no_pick__q, opt_method, t)
                    pass_veh_assgn = pass_veh_assign2 + pass_veh_assign1

                    remaining_persons = []
                    check_used_vehicles = used_vehicles[0:len(used_vehicles)]  # used_vehicles + reassign_veh
                    used_vehicles = []
                    old_veh_pick_q = veh_pick__q[0:len(veh_pick__q)]
                    for [i_pass, j_vehicle] in pass_veh_assgn:

                        # passenger is not assigned to a real vehicle, and the person is real
                        if j_vehicle.vehicle_id < 0:
                            remaining_persons.append(i_pass)
                            if i_pass in pass_no_pick__q:
                                sys.exit("Error - traveler was assigned, now is unassigned")

                        # passenger re-assigned to vehicle he/she already were assigned to
                        elif j_vehicle.next_pickup == i_pass:
                            used_vehicles.append(j_vehicle)

                        # passenger assigned to a real vehicle
                        elif j_vehicle.vehicle_id >= 0:
                            used_vehicles.append(j_vehicle)

                            # passenger assigned to an idle vehicle
                            if j_vehicle in veh_idle__q:

                                # if passenger already had a vehicle coming towards it, but then assigned a new vehicle
                                if i_pass.vehicle_id >= 0:
                                    i_pass.state = "reassign"
                                else:
                                    pass_no_pick__q.append(i_pass)

                                veh_pick__q.append(j_vehicle)

                            # passenger assigned to non-idle vehicle
                            else:
                                if opt_method == "match_idleDrop":
                                    pass_no_pick__q.append(i_pass)
                                    j_vehicle.state = "new_assign"

                                elif opt_method == "match_idlePick":
                                    j_vehicle.state = "reassign"
                                    if i_pass.vehicle_id >= 0:
                                        i_pass.state = "reassign"
                                    else:
                                        pass_no_pick__q.append(i_pass)

                                elif opt_method == "match_idlePickDrop":
                                    if i_pass.vehicle_id >= 0:
                                        i_pass.state = "reassign"
                                    else:
                                        pass_no_pick__q.append(i_pass)

                                    if j_vehicle in veh_pick__q:
                                        j_vehicle.state = "reassign"
                                    elif j_vehicle in veh_drop__q:
                                        j_vehicle.state = "new_assign"
                                    else:
                                        sys.exit("Error - something wrong with j_vehicle in match_idlePickDrop")

                            People[i_pass.person_id] = Person.update_Person(t, i_pass, j_vehicle)
                            Vehicles[j_vehicle.vehicle_id] = Vehicle.update_Vehicle(t, i_pass, j_vehicle, opt_method)

                        else:
                            sys.exit("Error in Assignment!")

                    len_remain = len(remaining_persons)
                    pass_no_assign__q = remaining_persons[0:len_remain]

                    # remove vehicles that have been  assigned to a passenger from the vehicle_idle_queue
                    for i_used in used_vehicles:
                        if i_used in veh_idle__q:
                            veh_idle__q.remove(i_used)

                    # vehicle was going to pick up traveler, now it is not
                    if opt_method == "match_idlePick":
                        for ijk_veh in old_veh_pick_q:
                            if ijk_veh not in used_vehicles:
                                ijk_veh.state = "unassign"
                                Vehicles[ijk_veh.vehicle_id] = Vehicle.update_Vehicle(t, Person.Person,
                                                                                      ijk_veh, opt_method)
                                veh_pick__q.remove(ijk_veh)
                                veh_idle__q.append(ijk_veh)

                    if opt_method == "match_idlePickDrop":
                        for abc_veh in check_used_vehicles:
                            if abc_veh not in used_vehicles:  # and abc_veh not in reassgn_veh_pick_Q:
                                abc_veh.state = "unassign"
                                Vehicles[abc_veh.vehicle_id] = Vehicle.update_Vehicle(t, Person.Person,
                                                                                      abc_veh, opt_method)
                                if abc_veh in veh_pick__q:
                                    veh_pick__q.remove(abc_veh)
                                    veh_idle__q.append(abc_veh)

    ##################################################################################################
    # Simulation Over
    ##################################################################################################

    ##################################################################################################
    # Calculate Performance Metrics for Single Simulation
    ##################################################################################################

    # Traveler Metrics ###############

    # Incomplete Travelers Metrics
    num_served = (list(p.state for p in People)).count("served")
    num_in_veh = (list(p.state for p in People)).count("inVeh")
    num_assgnd = (list(p.state for p in People)).count("assigned")
    num_unassgnd = (list(p.state for p in People)).count("unassigned")
    print("num_unassgnd", num_unassgnd)

    # Quality of Service Metrics
    # remove edge effects, only count middle 80% <-- previously 60%
    start = round(0.1*len(People))
    end = round(0.8*len(People))
    metric__people = People[start:end]
    num_metric_people = len(metric__people)

    # perc__rideshare = round(numpy.mean(list(p.rideshare for p in metric__people if p.state == "served")),2)
    perc_reassigned = round(numpy.mean(list(p.reassigned for p in metric__people if p.state == "served")),2)

    mean_ivtt = int(numpy.mean(list(p.travel_time for p in metric__people if p.state == "served")))
    sd_ivtt = int(numpy.std(list(p.travel_time for p in metric__people if p.state == "served")))

    mean_wait_pick = int(numpy.mean(list(p.wait_pick_time for p in metric__people if p.state == "served")))
    sd_wait_pick = int(numpy.std(list(p.wait_pick_time for p in metric__people if p.state == "served")))

    mean_wait_assgn = int(numpy.mean(list(p.wait_assgn_time for p in metric__people if p.state == "served")))
    sd_wait_assgn = int(numpy.std(list(p.wait_assgn_time for p in metric__people if p.state == "served")))

    mean_trip_dist = round(numpy.mean(list(p.in_veh_dist for p in metric__people if p.state == "served"))/5280, 3)
    sd_trip_dist = round(numpy.std(list(p.in_veh_dist for p in metric__people if p.state == "served"))/5280, 3)

    # Vehicle Metrics ###############

    tot_fleet_miles = int(sum(list(v.total_distance for v in Vehicles))/5280.0)
    mean_tot_veh_dist= round(numpy.mean(list(v.total_distance for v in Vehicles))/5280.0,2)
    sd_tot_veh_dist = round(numpy.std(list(v.total_distance for v in Vehicles))/5280.0,2)

    empty_fleet_miles = int(sum(list(v.empty_distance for v in Vehicles))/5280.0)
    mean_empty_veh_dist= round(numpy.mean(list(v.empty_distance for v in Vehicles))/5280.0,2)
    sd_empty_veh_dist = round(numpy.std(list(v.empty_distance for v in Vehicles))/5280.0,2)

    loaded_fleet_miles = int(sum(list(v.loaded_distance for v in Vehicles))/5280.0)
    mean_loaded_veh_dist= round(numpy.mean(list(v.loaded_distance for v in Vehicles))/5280.0,2)
    sd_loaded_veh_dist = round(numpy.std(list(v.loaded_distance for v in Vehicles))/5280.0,2)

    perc_empty_miles = round(empty_fleet_miles/float(tot_fleet_miles), 3)

    fleet_hours = ((mean_tot_veh_dist*5280.0)/veh_speed)/3600.0
    fleet_utilization = round(fleet_hours/(T_max/3600.0),2)


    #Initialize Vector of Metrics
    # sim_results = [num_metric_People,  perc_reassigned,
    #                mean_ivtt, sd_ivtt, mean_wait_pick, sd_wait_pick, mean_wait_assgn, sd_wait_assgn,
    #                mean_trip_dist, sd_trip_dist,
    #                tot_fleet_miles, mean_tot_veh_dist, sd_tot_veh_dist,
    #                empty_fleet_miles, perc_empty_miles, fleet_utilization,
    #                mean_increase_RS_ivtt, sd_increase_RS_ivtt,
    #                num_served, num_inVeh, num_assgnd, num_unassgnd]

    sim_results = [perc_reassigned, mean_wait_pick, perc_empty_miles , fleet_utilization,
                   num_served, num_in_veh, num_assgnd, num_unassgnd]


    ##################################################################################################
    #Traveler and Vehicle Results
    ##################################################################################################

    # ####### Traveler Results ###############
    # file_string1 = '../Results_Rev2/taxi_trvlr_results'+ '_hold' + str(hold_for) + '_fleet' + str(fleet_size) + '_opt' + str(opt_method)  +'.csv'
    # csv_traveler = open(file_string1, 'w')
    # traveler_writer = csv.writer(csv_traveler, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    # traveler_writer.writerow(["person_id", "base_ivtt", "simulate_ivtt", "wait_assgn_time","wait_pick_time", "vehicle", "old_veh"]) #, "rideshare"])
    #
    # for j_person in People[start:end]:
    #     base_ivtt = j_person.in_veh_dist/veh_speed
    #     traveler_writer.writerow([j_person.person_id, base_ivtt, j_person.travel_time, j_person.wait_assgn_time, j_person.wait_pick_time, j_person.vehicle_id, j_person.old_vehicles]) #, j_person.rideshare])
    #
    # ####### Vehicle Results ###############
    # file_string2 = '../Results_Rev2/taxi_veh_results'+ '_hold' + str(hold_for) + '_fleet' + str(fleet_size) + '_opt' + str(opt_method)  +'.csv'
    # csv_vehicle = open(file_string2, 'w')
    # vehicle_writer = csv.writer(csv_vehicle, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    # vehicle_writer.writerow(["vehicle_id", "distance", "pass_assgn", "pass_pick", "pass_drop", "pass_drop_list"])
    #
    # cum_distance = 0
    # for k_vehicle in Vehicles:
    #     cum_distance += k_vehicle.total_distance
    #     vehicle_writer.writerow([k_vehicle.vehicle_id, k_vehicle.total_distance, k_vehicle.pass_assgn_count,
    #                              k_vehicle.pass_pick_count, k_vehicle.pass_drop_count, k_vehicle.pass_dropped_list  ])
    #
    # vehicle_writer.writerow(["cum_distance", cum_distance/5280.0])




    return (sim_results)