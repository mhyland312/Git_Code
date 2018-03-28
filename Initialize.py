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

    #cluster_x = []
    #cluster_y = []
    #for i in range(4):
    #    cluster_x.append( (int(0.7*max_distance*random.random() + 0.15*max_distance)))
    #    cluster_y.append( (int(0.7*max_distance*random.random() + 0.15*max_distance)))

    temp_x = [0.2, 0.2, 0.8, 0.8]
    cluster_x = [x*max_distance for x in temp_x]
    temp_y = [0.2, 0.8, 0.2, 0.8]
    cluster_y = [y*max_distance for y in temp_y]


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

                e = cluster_x[drop_select] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                while e < 0:
                    e = cluster_x[drop_select] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                f = cluster_y[drop_select] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                while f < 0:
                    f = cluster_y[drop_select] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))

                temp_dist = abs(c-e) + abs(d-f)


            elif demand_type == "O_Cluster_D_Cluster":
                origin = random.randint(0,3)
                dest = random.randint(0,3)
                while origin == dest:
                    origin = random.randint(0,3)
                    dest = random.randint(0,3)

                c = cluster_x[origin] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                while c < 0:
                    c = cluster_x[origin] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                d = cluster_y[origin] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                while d < 0:
                    d = cluster_y[origin] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))

                e = cluster_x[dest] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                while e < 0:
                    e = cluster_x[dest] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                f = cluster_y[dest] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                while f < 0:
                    f = cluster_y[dest] + (round(numpy.random.normal(0, 0.05*max_distance, 1)[0], 4))
                temp_dist = abs(c-e) + abs(d-f)
            else:
                print("Error: Need Demand Distribution")

        g = random.randint(1, max_groupSize)
        row = [a, b, c, d, e, f, g]
        writer.writerow(row)
    csvDemandFile.close()
    return


def generate_Fleet(max_distance, num_vehicles, veh_capacity):
    csvVehicleFile = open('../Inputs/Vehicles_Taxi.csv', 'w')
    writer = csv.writer(csvVehicleFile, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(["vehicle_id", "start_x", "start_y", "capacity"])

    temp_x = [0.2, 0.2, 0.7, 0.7]
    cluster_x = [xx*max_distance for xx in temp_x]
    temp_y = [0.2, 0.7, 0.2, 0.7]
    cluster_y = [yy*max_distance for yy in temp_y]


    for j in range(num_vehicles):
        id = j
        depot_num = random.randint(0,3)
        #x = cluster_x[depot_num]
        #y = cluster_y[depot_num]
        x = max_distance/2.0 #+ random.random()*5280 #max_distance*random.random()
        y = max_distance/2.0 #+ random.random()*5280#max_distance*random.random()
        cap = veh_capacity
        rw = [id, x, y, cap]
        writer.writerow(rw)
    csvVehicleFile.close()

    return