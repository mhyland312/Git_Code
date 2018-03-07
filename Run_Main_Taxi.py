__author__ = 'Mike'

import Settings as Set
import Initialize as Init
import Main
import csv
import time

t0 = time.time()

# area_size_miles = [6.0]
area_size_miles = [25.0]
area_size = [x * 5280.0 for x in area_size_miles]


fleet_size = [350]
hold_for = [30]
opt_methods = [  "match_idleDrop", "match_idlePickDrop"] #"match_idleOnly",  "match_idlePick",

#csv_results2 = open(
#    '../Results/Taxi_Day7Sample_SmallFleet' + '_holds' + str(len(hold_for)) + '_fleet' + str(len(fleet_size)) + '_opt' + str(
#        len(opt_methods)) + '.csv', 'w')
#results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"',
#                             quoting=csv.QUOTE_NONNUMERIC)
# results_writer2.writerow(
#     ["Run#", "Simulation Length", "Requests Per Hour", "Demand Type",
#      "Area Size", "Opt Method", "Hold Time", "Fleet Size"
#      "% Reassign",
#      "mean wait pick", "sd wait pick", "mean wait assign", "sd wait assign",
#         "mean trip dist", "sd trip dist",
#      "% empty_miles", "fleet_utilization",
#      "served", "in vehicle", "assigned", "unassigned"])

for i_run in range(7, 8):
    # generate random demand
    #Init.generate_Demand(Set.T_max, a_demand_rate, q_area_size, Set.max_groupSize, p_demand_type)
    for j_fleet_size in fleet_size:
        jj_fleet_size = j_fleet_size #+ int(((q_area_size / 5280.0) - 4.0) * 20)
        # generate fleet
        Init.generate_Fleet(area_size[0], jj_fleet_size, Set.veh_capacity)
        for k_hold_for in hold_for:
            for m_opt_method in opt_methods:
                print("run #:", i_run, " demand type:", "Taxis",)
                print("fleet size:", jj_fleet_size, " hold for:", k_hold_for, " Opt Method:", m_opt_method)
                # run simulation
                results = Main.Main(k_hold_for, Set.T_max, Set.time_step, m_opt_method, Set.veh_speed, i_run)
                print(results)
#                results_writer2.writerow(
#                    [i_run, Set.T_max,  "Taxi", area_size[0]/5280, m_opt_method,
#                     k_hold_for, jj_fleet_size, results])
                #print(time.time() - t0)

#csv_results2.close()