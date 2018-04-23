import csv
import Vehicle
import Person
import Assignment_Algorithm as AA
import numpy
import sys
import Regions
__author__ = 'Mike'


def main(hold_for, t_max, time_step, opt_method, veh_speed, i_run, taxi):

    ##################################################################################################
    # Input Information - Customer Demand and AV Initial Positions
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
            person_status = "unassigned"
            People.append(Person.make_person(person_id, pickup_x, pickup_y, request_time, dropoff_x, dropoff_y,
                                             group_size, person_status))

    # read in information about all AVs
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
            veh_status = "idle"
            Vehicles.append(Vehicle.make_vehicle(vehicle_id, start_x, start_y, capacity, veh_status))

    ##################################################################################################
    # Simulation
    ##################################################################################################

    # Initialize Vectors
    i_person = 0
    pass_no_assign_q = []
    pass_no_pick_q = []
    fleet_size = len(Vehicles)
    veh_idle_q = Vehicles[0:fleet_size]
    veh_pick_q = []
    veh_drop_q = []
    veh_relocate_q = []

    used_vehicles = []

# Begin simulation
    for t in range(0, t_max, time_step):

    ##################################################################################################
    # Check to make sure AVs have not been deleted or added to multiple queues
        if len(veh_idle_q) + len(veh_pick_q) + len(veh_drop_q) != fleet_size:
            sys.exit("something wrong with AV queues")

    ##################################################################################################
    # move relocating AVs
        for i_veh_relocate in veh_relocate_q:
            if i_veh_relocate.curb_time_remain > 0:
                i_veh_relocate.curb_time_remain = i_veh_relocate.curb_time_remain - 1

            else:
                sub_area = i_veh_relocate.next_sub_area
                Vehicle.move_vehicle_manhat(t, i_veh_relocate, Person.Person, sub_area)

                # AV just made it to subArea relocation centroid and is idle
                if i_veh_relocate.status == "idle":
                    veh_idle_q.append(i_veh_relocate)
                    veh_relocate_q.remove(i_veh_relocate)
                    # may need to update subArea information

    ##################################################################################################
    # move en_route drop-off AVs
        for i_veh_drop in veh_drop_q:
            if i_veh_drop.curb_time_remain > 0:
                i_veh_drop.curb_time_remain = i_veh_drop.curb_time_remain - 1

            else:
                person_drop = i_veh_drop.next_drop
                Vehicle.move_vehicle_manhat(t, i_veh_drop, person_drop, Regions.SubArea)

                # AV just dropped customer off and is now idle
                if i_veh_drop.status == "idle":
                    veh_idle_q.append(i_veh_drop)
                    veh_drop_q.remove(i_veh_drop)
                    Person.update_Person(t, person_drop, i_veh_drop)

                # AV just dropped customer off but already has a next pickup point
                elif i_veh_drop.status == "enroute_pickup":
                    Person.update_Person(t, person_drop, i_veh_drop)
                    veh_pick_q.append(i_veh_drop)
                    veh_drop_q.remove(i_veh_drop)

    ##################################################################################################
    # move en_route pickup AVs
        for ii_veh_pick in veh_pick_q:
            if ii_veh_pick.curb_time_remain > 0:
                ii_veh_pick.curb_time_remain = ii_veh_pick.curb_time_remain - 1
            else:
                person_pick = ii_veh_pick.next_pickup
                Vehicle.move_vehicle_manhat(t, ii_veh_pick, person_pick, Regions.SubArea)

                if ii_veh_pick.status == "enroute_dropoff":
                    pass_no_pick_q.remove(person_pick)
                    veh_drop_q.append(ii_veh_pick)
                    veh_pick_q.remove(ii_veh_pick)
                    Person.update_Person(t, person_pick, ii_veh_pick)

    ##################################################################################################
    # update idle AVs curb wait time
        for iii_veh_idle in veh_idle_q:
            if iii_veh_idle.curb_time_remain > 0:
                iii_veh_idle.curb_time_remain = iii_veh_idle.curb_time_remain - 1

    ##################################################################################################
    # check if there are new requests
        if i_person < len(People):
            while People[i_person].request_time <= t:
                pass_no_assign_q.append(People[i_person])
                i_person += 1
                if i_person == len(People):
                    break

    ###################################################################################################
    # Assign AVs to customer requests

    ###################################################################################################
    # Assign using FCFS methods
        if "FCFS" in opt_method:
            if len(pass_no_assign_q) > 0 and len(veh_idle_q + veh_drop_q) > 0:

                pass_veh_assgn = AA.assign_veh_fcfs(veh_idle_q, veh_drop_q, pass_no_assign_q, opt_method)

                remaining_persons = []
                used_vehicles = []

                for [i_pass, j_vehicle] in pass_veh_assgn:
                    temp_veh_status = "base_assign"

                    # customer not assigned
                    if j_vehicle.vehicle_id < 0:
                        remaining_persons.append(i_pass)

                    # customer assigned to a real AV
                    elif j_vehicle.vehicle_id >= 0:
                        used_vehicles.append(j_vehicle)

                        # customer assigned to an idle AV
                        if j_vehicle in veh_idle_q:
                            veh_pick_q.append(j_vehicle)
                            pass_no_pick_q.append(i_pass)

                        # customer assigned to en-route drop-off AV
                        else:
                            pass_no_pick_q.append(i_pass)
                            temp_veh_status = "new_assign"

                        Person.update_Person(t, i_pass, j_vehicle)
                        Vehicle.update_vehicle(t, i_pass, j_vehicle, Regions.SubArea, temp_veh_status)

                    else:
                        sys.exit("Error in Assignment!")

                len_remain = len(remaining_persons)
                pass_no_assign_q = remaining_persons[0:len_remain]

                # remove AVs that have been assigned to a customer from the vehicle_idle_queue
                for i_used in used_vehicles:
                    if i_used in veh_idle_q:
                        veh_idle_q.remove(i_used)

    ###################################################################################################
    # Assign using Optimization-based methods
        else:
            # Every X seconds assign customers in the waiting queue to an AV
            if t % hold_for == 0 and len(pass_no_assign_q) > 0:

                # If assigned customers have already been reassigned once, do not include in assignment problem
                pass_veh_assign1 = []
                temp_veh_idle_q = veh_idle_q[0:len(veh_idle_q)]
                temp_veh_pick_q = veh_pick_q[0:len(veh_pick_q)]
                temp_veh_drop_q = veh_drop_q[0:len(veh_drop_q)]
                temp_pass_no_pick_q = pass_no_pick_q[0:len(pass_no_pick_q)]

                for i_trav in pass_no_pick_q:
                    if i_trav.reassigned == 1:
                        car = Vehicles[i_trav.vehicle_id]
                        pass_veh_assign1.append([i_trav, car])
                        temp_pass_no_pick_q.remove(i_trav)
                        if car in veh_idle_q:
                            temp_veh_idle_q.remove(car)
                        elif car in veh_pick_q:
                            temp_veh_pick_q.remove(car)
                        elif car in veh_drop_q:
                            temp_veh_drop_q.remove(car)

                # # If assigned customers have already been reassigned once, do not include in assignment problem
                # pass_veh_assign1 = []
                # temp_veh_pick_q = veh_pick_q[0:len(veh_pick_q)]
                # temp_pass_no_pick_q = pass_no_pick_q[0:len(pass_no_pick_q)]
                # for j_car in veh_pick_q:
                #     if j_car.next_pickup.reassigned == 1:
                #         pass_veh_assign1.append([j_car.next_pickup, j_car])
                #         temp_veh_pick_q.remove(j_car)
                #         temp_pass_no_pick_q.remove(j_car.next_pickup)

                # call assignment algorithm
                pass_veh_assign2 = AA.assign_veh_opt(temp_veh_idle_q, temp_veh_pick_q, temp_veh_drop_q,
                                                     pass_no_assign_q, temp_pass_no_pick_q, opt_method, t)
                pass_veh_assgn = pass_veh_assign2 + pass_veh_assign1

                remaining_persons = []
                check_used_vehicles = used_vehicles[0:len(used_vehicles)]  # used_vehicles + reassign_veh
                used_vehicles = []
                used_vehicles = list(jj_car for [ii_person, jj_car] in pass_veh_assign1)
                old_veh_pick_q = veh_pick_q[0:len(veh_pick_q)]

                for [i_pass, j_vehicle] in pass_veh_assgn:
                    temp_veh_status = "base_assign"

                    # customer is not assigned to a real AV, and the person is real
                    if j_vehicle.vehicle_id < 0:
                        remaining_persons.append(i_pass)
                        if i_pass in pass_no_pick_q:
                            sys.exit("Error - customer was assigned, now is unassigned")

                    # customer re-assigned to AV he/she already was assigned to
                    elif j_vehicle.next_pickup == i_pass:
                        used_vehicles.append(j_vehicle)

                    # customer assigned to a real AV
                    elif j_vehicle.vehicle_id >= 0:
                        used_vehicles.append(j_vehicle)

                        # if customer assigned to AV previously (remember that already checked if reassigned to same AV)
                        if i_pass.vehicle_id >= 0:
                            i_pass.status = "reassign"
                        else:
                            pass_no_pick_q.append(i_pass)

                        # customer assigned to an idle AV
                        if j_vehicle in veh_idle_q:
                            veh_pick_q.append(j_vehicle)

                        # customer assigned to en-route pickup AV (that is not her own because of early if condition)
                        elif j_vehicle in veh_pick_q:
                            temp_veh_status = "reassign"

                        # customer assigned to en-route drop-off AV
                        elif j_vehicle in veh_drop_q:
                            temp_veh_status = "new_assign"

                        Person.update_Person(t, i_pass, j_vehicle)
                        Vehicle.update_vehicle(t, i_pass, j_vehicle, Regions.SubArea, temp_veh_status)

                    else:
                        sys.exit("Error in Assignment!")

                len_remain = len(remaining_persons)
                pass_no_assign_q = remaining_persons[0:len_remain]

                # remove AVs that have been assigned to a customer from the vehicle_idle_queue
                for i_used in used_vehicles:
                    if i_used in veh_idle_q:
                        veh_idle_q.remove(i_used)

                # AV was going to pick up customer, now it is not
                # if opt_method == "match_idlePick":
                #     for ijk_veh in old_veh_pick_q:
                #         if ijk_veh not in used_vehicles:
                #             temp_veh_status = "unassign"
                #             Vehicle.update_vehicle(t, Person.Person, ijk_veh, Regions.SubArea, temp_veh_status)
                #             veh_pick_q.remove(ijk_veh)
                #             veh_idle_q.append(ijk_veh)

                if "Pick" in opt_method:#opt_method == "match_idlePickDrop":
                    for abc_veh in check_used_vehicles:
                        if abc_veh not in used_vehicles:  # and abc_veh not in reassgn_veh_pick_Q:
                            temp_veh_status = "unassign"
                            Vehicle.update_vehicle(t, Person.Person, abc_veh, Regions.SubArea, temp_veh_status)
                            if abc_veh in veh_pick_q:
                                veh_pick_q.remove(abc_veh)
                                veh_idle_q.append(abc_veh)
                            # i think it is possible that we should also check veh_drop_q
                            elif abc_veh in veh_drop_q:
                                abc_veh.next_pickup = Person.Person

    ##################################################################################################
    # Simulation Over
    ##################################################################################################

    ##################################################################################################
    # Calculate Performance Metrics for Single Simulation
    ##################################################################################################

    # Customer Metrics ###############

    # Incomplete Customers Metrics
    num_served = (list(p.status for p in People)).count("served")
    num_in_veh = (list(p.status for p in People)).count("inVeh")
    num_assgnd = (list(p.status for p in People)).count("assigned")
    num_unassgnd = (list(p.status for p in People)).count("unassigned")
    print("num_served", num_served)

    # Quality of Service Metrics
    # remove edge effects, only count middle 80% <-- previously 60%
    start = round(0.1*len(People))
    end = round(0.8*len(People))
    metric__people = People[start:end]
    # num_metric_people = len(metric__people)

    # perc__rideshare = round(numpy.mean(list(p.rideshare for p in metric__people if p.status == "served")),2)
    perc_reassigned = round(numpy.mean(list(p.reassigned for p in metric__people if p.status == "served")),2)

    # mean_ivtt = int(numpy.mean(list(p.travel_time for p in metric__people if p.status == "served")))
    # sd_ivtt = int(numpy.std(list(p.travel_time for p in metric__people if p.status == "served")))

    mean_wait_pick = int(numpy.mean(list(p.wait_pick_time for p in metric__people if p.status == "served")))
    # sd_wait_pick = int(numpy.std(list(p.wait_pick_time for p in metric__people if p.status == "served")))

    # mean_wait_assgn = int(numpy.mean(list(p.wait_assgn_time for p in metric__people if p.status == "served")))
    # sd_wait_assgn = int(numpy.std(list(p.wait_assgn_time for p in metric__people if p.status == "served")))

    # mean_trip_dist = round(numpy.mean(list(p.in_veh_dist for p in metric__people if p.status == "served"))/5280, 3)
    # sd_trip_dist = round(numpy.std(list(p.in_veh_dist for p in metric__people if p.status == "served"))/5280, 3)

    # AV Metrics ###############

    tot_fleet_miles = int(sum(list(v.total_distance for v in Vehicles))/5280.0)
    mean_tot_veh_dist = round(numpy.mean(list(v.total_distance for v in Vehicles))/5280.0, 2)
    # sd_tot_veh_dist = round(numpy.std(list(v.total_distance for v in Vehicles))/5280.0,2)

    empty_fleet_miles = int(sum(list(v.empty_distance for v in Vehicles))/5280.0)
    # mean_empty_veh_dist= round(numpy.mean(list(v.empty_distance for v in Vehicles))/5280.0,2)
    # sd_empty_veh_dist = round(numpy.std(list(v.empty_distance for v in Vehicles))/5280.0,2)

    # loaded_fleet_miles = int(sum(list(v.loaded_distance for v in Vehicles))/5280.0)
    # mean_loaded_veh_dist= round(numpy.mean(list(v.loaded_distance for v in Vehicles))/5280.0,2)
    # sd_loaded_veh_dist = round(numpy.std(list(v.loaded_distance for v in Vehicles))/5280.0,2)

    perc_empty_miles = round(empty_fleet_miles/float(tot_fleet_miles), 3)

    fleet_hours = ((mean_tot_veh_dist*5280.0)/veh_speed)/3600.0
    fleet_utilization = round(fleet_hours / (t_max / 3600.0), 2)

    # Initialize Vector of Metrics
    # sim_results = [num_metric_People,  perc_reassigned,
    #                mean_ivtt, sd_ivtt, mean_wait_pick, sd_wait_pick, mean_wait_assgn, sd_wait_assgn,
    #                mean_trip_dist, sd_trip_dist,
    #                tot_fleet_miles, mean_tot_veh_dist, sd_tot_veh_dist,
    #                empty_fleet_miles, perc_empty_miles, fleet_utilization,
    #                mean_increase_RS_ivtt, sd_increase_RS_ivtt,
    #                num_served, num_inVeh, num_assgnd, num_unassgnd]

    sim_results = [perc_reassigned, mean_wait_pick, perc_empty_miles, fleet_utilization,
                   num_served, num_in_veh, num_assgnd, num_unassgnd]

    ##################################################################################################
    # Customer and AV Results
    ##################################################################################################

    ####### Customer Results ###############
    # file_string1 = '../Results_Rev2/taxi_trvlr_results'+ '_hold' + str(hold_for) + '_fleet' + str(fleet_size) \
    #                + '_opt' + str(opt_method)  +'.csv'
    # csv_traveler = open(file_string1, 'w')
    # traveler_writer = csv.writer(csv_traveler, lineterminator='\n', delimiter=',', quotechar='"',
    #                              quoting=csv.QUOTE_NONNUMERIC)
    # traveler_writer.writerow(["person_id", "base_ivtt", "simulate_ivtt", "wait_assgn_time","wait_pick_time",
    #                           "vehicle", "old_veh"]) #, "rideshare"])
    #
    # for j_person in People[start:end]:
    #     base_ivtt = j_person.in_veh_dist/veh_speed
    #     traveler_writer.writerow([j_person.person_id, base_ivtt, j_person.travel_time, j_person.wait_assgn_time,
    #                               j_person.wait_pick_time, j_person.vehicle_id, j_person.old_vehicles])
    #
    # ####### AV Results ###############
    # file_string2 = '../Results_Rev2/taxi_veh_results'+ '_hold' + str(hold_for) + '_fleet' + str(fleet_size) \
    #                + '_opt' + str(opt_method)  +'.csv'
    # csv_vehicle = open(file_string2, 'w')
    # vehicle_writer = csv.writer(csv_vehicle, lineterminator='\n', delimiter=',', quotechar='"',
    #                             quoting=csv.QUOTE_NONNUMERIC)
    # vehicle_writer.writerow(["vehicle_id", "distance", "pass_assgn", "pass_pick", "pass_drop",
    #                          "pass_drop_list"])
    #
    # cum_distance = 0
    # for k_vehicle in Vehicles:
    #     cum_distance += k_vehicle.total_distance
    #     vehicle_writer.writerow([k_vehicle.vehicle_id, k_vehicle.total_distance, k_vehicle.pass_assgn_count,
    #                              k_vehicle.pass_pick_count, k_vehicle.pass_drop_count, k_vehicle.pass_dropped_list])
    #
    # vehicle_writer.writerow(["cum_distance", cum_distance/5280.0])

    return (sim_results)