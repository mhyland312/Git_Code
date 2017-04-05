__author__ = 'Mike'

import random
import numpy
import csv


def generate_Demand(T_max, num_requests, max_distance, max_groupSize):
    lambd = 0.8 * T_max/float(num_requests)

    demand_time = numpy.random.exponential(lambd, num_requests)
    demand_time = numpy.cumsum(demand_time)

    drop_x = []
    drop_y = []
    for i in range(20):
        drop_x.append((round(max_distance*random.random(), 4)))
        drop_y.append((round(max_distance*random.random(), 4)))


    csvDemandFile = open('../Inputs/Demand_Requests.csv', 'w')
    writer = csv.writer(csvDemandFile, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(["person_id", "start_x", "start_y", "request_time", "dropoff_x", "dropoff_y", "group_size"])
    for i in range(num_requests):
        a = i
        b = (round(max_distance*random.random(), 4))
        c = (round(max_distance*random.random(), 4))
        d = int(demand_time[i])
        drop_select = random.randint(0,19)
        e = drop_x[drop_select]
        f = drop_y[drop_select]
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