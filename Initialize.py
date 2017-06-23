__author__ = 'Mike'

import random
import numpy
import csv



def generate_Demand(T_max, requests_per_hour, max_distance, max_groupSize, demand_type):
    simul_len = (T_max/3600.0)
    num_requests = int(simul_len * requests_per_hour)


    lambd = 0.8 * T_max/float(num_requests)

    demand_time = numpy.random.exponential(lambd, num_requests)
    demand_time = numpy.cumsum(demand_time)

    drop_x = []
    drop_y = []
    for i in range(4):
        drop_x.append((round(max_distance*random.random(), 4)))
        drop_y.append((round(max_distance*random.random(), 4)))


    csvDemandFile = open('../Inputs/Demand_Requests.csv', 'w')
    writer = csv.writer(csvDemandFile, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(["person_id", "start_x", "start_y", "request_time", "dropoff_x", "dropoff_y", "group_size"])
    for i in range(num_requests):
        a = i
        b = int(demand_time[i])
        temp_dist = 0

        while temp_dist < 0.8 * 5280.0:
            if demand_type == "O_Uniform_D_Uniform":
                c = (round(max_distance*random.random(), 4))
                d = (round(max_distance*random.random(), 4))
                e = (round(max_distance*random.random(), 4))
                f = (round(max_distance*random.random(), 4))
                temp_dist = abs(c-e) + abs(d-f)
            elif demand_type == "O_Uniform_D_Cluster":
                c = (round(max_distance*random.random(), 4))
                d = (round(max_distance*random.random(), 4))
                drop_select = random.randint(0,3)
                e = drop_x[drop_select] + (round(numpy.random.normal(0, 0.4*5280, 1)[0], 4))
                f = drop_y[drop_select] + (round(numpy.random.normal(0, 0.4*5280, 1)[0], 4))
                temp_dist = abs(c-e) + abs(d-f)
            elif demand_type == "O_Cluster_D_Cluster":
                origin = random.randint(0,3)
                dest = random.randint(0,3)
                while origin != dest:
                    origin = random.randint(0,3)
                    dest = random.randint(0,3)
                c = drop_x[origin] + (round(numpy.random.normal(0, 0.4*5280, 1)[0], 4))
                d = drop_y[origin] + (round(numpy.random.normal(0, 0.4*5280, 1)[0], 4))
                e = drop_x[dest] + (round(numpy.random.normal(0, 0.4*5280, 1)[0], 4))
                f = drop_y[dest] + (round(numpy.random.normal(0, 0.4*5280, 1)[0], 4))
                temp_dist = abs(c-e) + abs(d-f)
            else:
                print("Error: Need Demand Distribution")

        g = random.randint(1, max_groupSize)
        row = [a, b, c, d, e, f, g]
        writer.writerow(row)
    csvDemandFile.close()


def generate_Fleet( max_distance, num_vehicles, veh_capacity):
    csvVehicleFile = open('../Inputs/Vehicles.csv', 'w')
    writer = csv.writer(csvVehicleFile, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(["vehicle_id", "start_x", "start_y", "capacity"])
    for j in range(num_vehicles):
        z = j
        y = (round(max_distance*random.random(), 4))
        x = (round(max_distance*random.random(), 4))
        w = veh_capacity
        rw = [z, y, x, w]
        writer.writerow(rw)
    csvVehicleFile.close()


    return()