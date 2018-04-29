import Settings as Set
import Initialize as Init
import Main
import csv
import time

__author__ = 'Mike'

t0 = time.time()

area_size_miles = [25.0]
area_size = [x * 5280.0 for x in area_size_miles]

fleet_size = [300, 400, 500]
hold_for = [30, 60]

opt_methods = ["1_FCFS_longestIdle", "2_FCFS_nearestIdle",
               "3_FCFS_smartNN",  "4_FCFS_drop_smartNN", "4a_FCFS_drop_smartNN2",
               "5_match_idleOnly", "6_match_idlePick",
               "7_match_idleDrop", "7_match_idleDrop2",
               "8_match_idlePickDrop"]

relocate_method = "Dandl"

csv_results2 = open('../Results_Rev2/Taxi_Day7Sample_SmallFleet' + '_holds' + str(len(hold_for)) + '_fleet' +
                    str(len(fleet_size)) + '_opt' + str(len(opt_methods)) + '.csv', 'w')

results_writer2 = csv.writer(csv_results2, lineterminator='\n', delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_NONNUMERIC)
results_writer2.writerow(
    ["Runs", "Sim_Length", "Hold Time", "Requests Per Hour",
     "Demand Type", "Area Size", "Opt Method",  "Fleet Size",
     "Mean Wait Pick", "% Empty", "% Reassign", "Fleet Util",
     "#Served", "#inVeh", "#Assgnd", "#Unassgnd"])

for i_run in range(7, 8):
    for j_fleet_size in fleet_size:
        # generate fleet
        Init.generate_fleet(area_size[0], j_fleet_size, Set.veh_capacity)
        for k_hold_for in hold_for:
            for m_opt_method in opt_methods:
                print("run #:", i_run, " demand type:", "Taxis",)
                print("fleet size:", j_fleet_size, " hold for:", k_hold_for, " Opt Method:", m_opt_method)
                # run simulation
                results = Main.main(k_hold_for, Set.t_max, Set.time_step,
                                    m_opt_method, relocate_method, Set.veh_speed, i_run, True)

                print(results)
                results_writer2.writerow(
                    [i_run, Set.t_max,  "Taxi", area_size[0]/5280, m_opt_method,
                    k_hold_for, j_fleet_size, results])
                print(time.time() - t0)
csv_results2.close()
