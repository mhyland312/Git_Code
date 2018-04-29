import csv
import Vehicle
import Person
import Assignment_Algorithm as AA
import numpy
import datetime
import sys
import Regions
__author__ = 'Mike'


# Dandl
# Comment FD:
# I had to add two input parameters
# Since my relocation algorithm will probably have 2 parameters, I might need to add even more.
def main(hold_for, t_max, time_step, opt_method, relocate_method, veh_speed, i_run, taxi, xyt_string, false_forecast_f=None):

    # Dandl
    # Comment FD:
    # this part assumes 'i_run' is given in iso format, e.g. 2016-04-01
    # this is necessary to use the correct forecasts
    (sim_year, sim_month, sim_day) = [int(x) for x in i_run.split("-")]
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    date = datetime.datetime(sim_year, sim_month, sim_day)
    dayNumber = date.weekday()
    weekday = week[dayNumber]


    ##################################################################################################
    # Input Information - Customer Demand
    ##################################################################################################
    # read in information about all customers
    if taxi:
        file_str = "../Inputs/Taxi_Demand_Day" + str(i_run) + "_Sample.csv"
    else:
        file_str = "../Inputs/Demand_Requests.csv"
    demand_file = open(file_str, 'r')

    demand_reader = csv.reader(demand_file)
    customers = []
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
            customers.append(Person.make_person(person_id, pickup_x, pickup_y, request_time, dropoff_x, dropoff_y,
                                             group_size))

    ##################################################################################################
    # Input Information - AV Initial Positions
    ##################################################################################################
    # read in information about all AVs
    if taxi:
        file_str2 = "../Inputs/Vehicles_Taxi.csv"
    else:
        file_str2 = "../Inputs/Vehicles_Taxi.csv"

    veh_file = open(file_str2, 'r')
    vehicle_reader = csv.reader(veh_file)
    av_fleet = []
    cnt = 0
    for j_row in vehicle_reader:
        cnt += 1
        if cnt > 1:
            vehicle_id = int(j_row[0])
            start_x = float(j_row[1])
            start_y = float(j_row[2])
            capacity = int(j_row[3])
            veh_status = "idle"
            av_fleet.append(Vehicle.make_vehicle(vehicle_id, start_x, start_y, capacity, veh_status))

    ##################################################################################################
    # Input Information - Regions/subAreas
    ##################################################################################################

    # Dandl
    ############
    # create a list with all sub_area objects
    # and/or create a list with all subArea-time periods
    # it seems like you might already be reading in the files in Regions, but still need a list of all sub_area objects
    ############
    # Comment FD: the idea is that the main area class does all the work and returns dictionaries for
    # 1) demand forecast
    # 2) vehicle availability
    # with the subarea_key as key of the respective dictionary and the respective quantity as value
    # the respective destination centers can be called by
    # area.sub_areas[subarea_key].relocation_destination
    #
    # read information of area depending on
    # a) xyt_string
    # b) false_forecast_f [optional, if not given, the real forecast value will be read]
    # format of xyt_string: 2x_8y_5min
    # format of xy_string: 2x_8y
    xy_string = "_".join(xyt_string.split("_")[:2])
    prediction_csv_file = "prediction_areas_{0}.csv".format(xy_string)
    # region_csv_file = "prediction_areas_{0}.csv".format(xy_string)
    if false_forecast_f:
        region_csv_file = false_forecast_f
    else:
        region_csv_file = "manhattan_trip_patterns_{0}_only_predictions.csv".format(xyt_string)
    relocation_destination_f = "demand_center_points_{0}.csv".format(xy_string)
    area = Regions.Area(region_csv_file, prediction_csv_file, relocation_destination_f)

    ##################################################################################################
    # Simulation
    ##################################################################################################

    # Initialize Vectors
    i_person = 0

# Begin simulation
    new_t_max = int(1.2 * t_max)
    for t in range(0, new_t_max, time_step):

        for j_av in av_fleet:

            ##################################################################################################
            # decrease curb time, of vehicles that just finished pickup or drop-off
            if j_av.curb_time_remain > 0:
                j_av.curb_time_remain -= time_step

            ##################################################################################################
            # move relocating AVs
            elif j_av.status == "relocating":
                sub_area = j_av.next_sub_area
                Vehicle.move_vehicle_manhat(t, j_av, Person.Person, sub_area)
                # if AV arrives at centroid location, change to idle

                # Dandl
                # may need to update subArea information
                # comment FD: my idea would be to update all subArea information in the
                # decision time steps only
                # it should not matter if a vehicle that is idle served a customer or
                # was relocating

            ##################################################################################################
            # move en_route drop-off AVs
            elif j_av.status == "enroute_dropoff":
                person_drop = j_av.next_drop
                Vehicle.move_vehicle_manhat(t, j_av, person_drop, Regions.SubArea)
                #if AV's status changes, then the AV must have dropped off customer, and traveler status needs to change
                if j_av.status != "enroute_dropoff":
                    Person.update_person(t, person_drop, j_av)

            ##################################################################################################
            # move en_route pickup AVs
            elif j_av.status == "enroute_pickup":
                person_pick = j_av.next_pickup
                Vehicle.move_vehicle_manhat(t, j_av, person_pick, Regions.SubArea)
                # if AV's status changes, then the AV must have picked up customer, and customer status needs to change
                if j_av.status != "enroute_pickup":
                    Person.update_person(t, person_pick, j_av)


        ##################################################################################################
        # check if there are new requests
        if i_person < len(customers):
            while customers[i_person].request_time <= t:
                i_request = customers[i_person]
                Person.update_person(t, i_request, Vehicle.Vehicle)
                i_person += 1
                if i_person == len(customers):
                    break

    ###################################################################################################
    # Assign AVs to customer requests
    ###################################################################################################
        # Get the number of idle AVs and unassigned customers
        count_avail_veh = len(list(j for j in av_fleet
                                   if j.status in ["idle", "enroute_dropoff"]
                                   and j.next_pickup.person_id < 0))
        count_unassigned = len(list(i for i in customers if i.status == "unassigned"))
    # Assign using FCFS methods
        if "FCFS" in opt_method:
            if count_unassigned > 0 and count_avail_veh > 0:
                AA.assign_veh_fcfs(av_fleet, customers, opt_method, t)

        # Dandl
        # Call relocation/rebalancing algorithm
        # Comment FD: give reference to area object instead of sub_areas to relocation algorithm
        # -> this allows use of area.getVehicleAvailabilitiesPerArea() and
        #                       area.getDemandPredictionsPerArea()
        # forecast needs to know which weekday it is
        veh_subarea_assgn = relocate_veh(av_fleet, area, relocate_method, t, weekday)

        # Dandl
        # Need to process sub_Areas, and vehicles that are now relocating
        # Comment FD: veh_subarea_assgn is list of (vehicle_obj, subArea_obj) tuples
        for [j_vehicle, l_subarea] in veh_subarea_assgn:
            temp_veh_status = "relocating"
            Vehicle.update_vehicle(t, Person.Person, j_vehicle, l_subarea, temp_veh_status)

    ###################################################################################################
    # Assign using Optimization-based methods
        else:
            # Every X seconds assign customers in the waiting queue to an AV
            if t % hold_for == 0 and count_unassigned > 0 and count_avail_veh > 0:
                AA.assign_veh_opt(av_fleet, customers, opt_method, t)

        # Dandl
        # Call relocation/rebalancing algorithm
        # Comment FD: give reference to area object instead of sub_areas to relocation algorithm
        # -> this allows use of area.getVehicleAvailabilitiesPerArea() and
        #                       area.getDemandPredictionsPerArea()
        # forecast needs to know which weekday it is
        veh_subarea_assgn = relocate_veh(av_fleet, area, relocate_method, t, weekday)

        # Dandl
        # Need to process sub_Areas, and vehicles that are now relocating
        # Comment FD: veh_subarea_assgn is list of (vehicle_id, subArea-reference) tuples
        for [j_vehicle, l_subarea] in veh_subarea_assgn:
            temp_veh_status = "relocate"
            Vehicle.update_vehicle(t, Person.Person, j_vehicle, l_subarea, temp_veh_status)

    ###################################################################################################
    # Assign AVs to customer requests
    ###################################################################################################
    # Relocate AVs
    # Dandl
    # Call relocation/rebalancing algorithm
    # relocate_veh(av_fleet, sub_areas, relocate_method, t)





    ##################################################################################################
    # Simulation Over
    ##################################################################################################

    ##################################################################################################
    # Calculate Performance Metrics for Single Simulation
    ##################################################################################################

    # Customer Metrics ###############

    # Incomplete Customers Metrics
    num_served = (list(p.status for p in customers)).count("served")
    num_in_veh = (list(p.status for p in customers)).count("inVeh")
    num_assgnd = (list(p.status for p in customers)).count("assigned")
    num_unassgnd = (list(p.status for p in customers)).count("unassigned")
    print("num_served", num_served)

    # Quality of Service Metrics
    # remove edge effects, only count middle 80% <-- previously 60%
    start = round(0.1*len(customers))
    end = round(0.8*len(customers))
    metric__people = customers[start:end]
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

    tot_fleet_miles = int(sum(list(v.total_distance for v in av_fleet))/5280.0)
    mean_tot_veh_dist = round(numpy.mean(list(v.total_distance for v in av_fleet))/5280.0, 2)
    # sd_tot_veh_dist = round(numpy.std(list(v.total_distance for v in Vehicles))/5280.0,2)

    empty_fleet_miles = int(sum(list(v.empty_distance for v in av_fleet))/5280.0)
    # mean_empty_veh_dist= round(numpy.mean(list(v.empty_distance for v in Vehicles))/5280.0,2)
    # sd_empty_veh_dist = round(numpy.std(list(v.empty_distance for v in Vehicles))/5280.0,2)

    # loaded_fleet_miles = int(sum(list(v.loaded_distance for v in Vehicles))/5280.0)
    # mean_loaded_veh_dist= round(numpy.mean(list(v.loaded_distance for v in Vehicles))/5280.0,2)
    # sd_loaded_veh_dist = round(numpy.std(list(v.loaded_distance for v in Vehicles))/5280.0,2)

    perc_empty_miles = round(empty_fleet_miles/float(tot_fleet_miles), 3)

    fleet_hours = ((mean_tot_veh_dist*5280.0)/veh_speed)/3600.0
    fleet_utilization = round(fleet_hours / (new_t_max / 3600.0), 2)

    # Initialize Vector of Metrics
    # sim_results = [num_metric_People,  perc_reassigned,
    #                mean_ivtt, sd_ivtt, mean_wait_pick, sd_wait_pick, mean_wait_assgn, sd_wait_assgn,
    #                mean_trip_dist, sd_trip_dist,
    #                tot_fleet_miles, mean_tot_veh_dist, sd_tot_veh_dist,
    #                empty_fleet_miles, perc_empty_miles, fleet_utilization,
    #                mean_increase_RS_ivtt, sd_increase_RS_ivtt,
    #                num_served, num_inVeh, num_assgnd, num_unassgnd]

    sim_results = [ mean_wait_pick, perc_empty_miles, perc_reassigned, fleet_utilization,
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
    # for j_person in customers[start:end]:
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
    # for k_vehicle in av_fleet:
    #     cum_distance += k_vehicle.total_distance
    #     vehicle_writer.writerow([k_vehicle.vehicle_id, k_vehicle.total_distance, k_vehicle.pass_assgn_count,
    #                              k_vehicle.pass_pick_count, k_vehicle.pass_drop_count, k_vehicle.pass_dropped_list])
    #
    # vehicle_writer.writerow(["cum_distance", cum_distance/5280.0])

    return (sim_results)