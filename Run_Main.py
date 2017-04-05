__author__ = 'Mike'

import Settings
import Initialize as Init
import Main
import csv
import time

t0 = time.time()

fleet_size1 =  [j for j in range(120,131,3)]
fleet_size2 =  [j for j in range(160,240,10)]
fleet_size = fleet_size1 + fleet_size2
#fleet_size =  [250]

hold_for = [1, 3, 7]
#hold_for = [10]

#opt_methods = [ "match_RS", "match_idlePick", "match_idleOnly", "match_idleDrop"]
opt_methods = ["match_idleOnly", "match_idlePick",  "match_idleDrop"]

csv_results2 = open('../Results/BigResults'+ '_holds' + str(len(hold_for)) + '_fleet' + str(len(fleet_size)) + '_opt' + str(len(opt_methods))  +'.csv', 'w')
results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
results_writer2.writerow(["demand_set" , "opt method", "hold time" , "fleet size", 
                          "cumul ivtt", "base ivtt", "wait assgn time", "wait pick time", "%Rideshare", "fleet miles", 
                          "unassigned pass", "noPick pass"])
                         


for i_run in range(0,1):
    #generate random demand
    Init.generate_Demand(Settings.T_max, Settings.num_requests, Settings.max_distance,  Settings.max_groupSize)
    for j_fleet_size in fleet_size:
        #generate fleet 
        Init.generate_Fleet(Settings.max_distance,j_fleet_size, Settings.veh_capacity)
        for k_hold_for in hold_for:
            for m_opt_method in opt_methods:

                print("run # ", i_run, "fleet size ", j_fleet_size, "hold for ", k_hold_for, "Opt Method ", m_opt_method)
                #run simulation
                results = Main.Main(k_hold_for, Settings.T_max, Settings.time_step, m_opt_method, Settings.veh_speed)
                print(results)                
                results_writer2.writerow([i_run, m_opt_method, k_hold_for, j_fleet_size, results ])
                print(time.time() - t0)
                                          

csv_results2.close()