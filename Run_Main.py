__author__ = 'Mike'

import Settings as Set
import Initialize as Init
import Main
import csv
import time

t0 = time.time()

#area_size_miles = [6.0]
area_size_miles = [8.0, 6.0, 4.0]
area_size = [x * 5280.0 for x in area_size_miles]

requests_per_hour = [850, 900, 950, 1000, 1050]

#demand_Type = [ "O_Uniform_D_Uniform"]
demand_Type = ["O_Uniform_D_Uniform", "O_Uniform_D_Cluster", "O_Cluster_D_Cluster"]

fleet_size1 =  [j for j in range(160,181,10)]
fleet_size2 =  [j for j in range(210, 300, 25)]
#fleet_size = fleet_size1 + fleet_size2
fleet_size =  [150]

hold_for = [10]

#opt_methods = [ "FCFS_longestIdle", "FCFS_nearestIdle", "match_idleOnly", "match_idlePick", "match_idleDrop", "match_idlePickDrop", "match_RS"]
#opt_methods = [ "match_idleDrop", "match_idlePickDrop"]
opt_methods = ["match_idlePickDrop", "match_RS"]

csv_results2 = open('../Results/BigResults'+ '_holds' + str(len(hold_for)) + '_fleet' + str(len(fleet_size)) + '_opt' + str(len(opt_methods))  +'.csv', 'w')
results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
results_writer2.writerow(["Run#", "Simulation Length", "Requests Per Hour", "Demand Type", "Area Size", "Opt Method", "Hold Time" , "Fleet Size",
                          "num metric people",
                          "% Rideshare", "% Reassigned",
                          "mean ivtt", "sd ivtt", "mean wait pick", "sd wait pick", "mean wait assgn", "sd wait assign",
                          "mean trip dist", "sd trip dist",
                          "fleet miles - all veh", "mean dist - all veh", "sd dist - all veh",
                          "fleet miles - empty veh",
                          "% empty_miles", "fleet_utilization",
                          "mean % increase RS IVTT", "sd % increase RS IVTT",
                          "served", "in vehicle", "assigned", "unassigned"])
                         
for i_run in range(0,3):
    for a_demand_rate in requests_per_hour:
        for p_demand_type in demand_Type:
            for q_area_size in area_size:
                #generate random demand
                Init.generate_Demand(Set.T_max, a_demand_rate, q_area_size,  Set.max_groupSize, p_demand_type)
                for j_fleet_size in fleet_size:
                    jj_fleet_size = j_fleet_size + int(((q_area_size/5280.0)-4.0)*40)
                    #generate fleet
                    Init.generate_Fleet(q_area_size, jj_fleet_size, Set.veh_capacity)
                    for k_hold_for in hold_for:
                        for m_opt_method in opt_methods:

                            print("run # ", i_run, "fleet size ", jj_fleet_size, "hold for ", k_hold_for, "Opt Method ", m_opt_method)
                            #run simulation
                            results = Main.Main(k_hold_for, Set.T_max, Set.time_step, m_opt_method, Set.veh_speed)
                            print(results)
                            results_writer2.writerow([ i_run, Set.T_max, a_demand_rate, p_demand_type, q_area_size/5280, m_opt_method, k_hold_for, jj_fleet_size, results])
                            print(time.time() - t0)


csv_results2.close()