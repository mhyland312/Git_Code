import Distance
import gurobipy
import Settings as Set
import Vehicle
import Regions
import Person
import sys
import time

__author__ = 'Mike'


#############################################################################################################
def assign_veh_fcfs(av_fleet, customers, opt_method, t):
    if opt_method == "1_FCFS_longestIdle":
        fcfs_longest_idle(av_fleet, customers, t)
    elif opt_method == "2_FCFS_nearestIdle":
        fcfs_nearest_idle(av_fleet, customers, t)
    elif opt_method == "3_FCFS_smartNN":
        fcfs_smart_nn(av_fleet, customers, t)
    elif opt_method == "4_FCFS_drop_smartNN":
        fcfs_drop_smart_nn(av_fleet, customers, t)
    elif opt_method == "4a_FCFS_drop_smartNN2":
        fcfs_drop_smart_nn2(av_fleet, customers, t)
    else:
        print("Error: No_FCFS_assignment_method")
    return
#############################################################################################################


#############################################################################################################
def assign_veh_opt(av_fleet, customers, opt_method, t):
    if opt_method == "5_match_idleOnly":
        opt_idle(av_fleet, customers, t)
    elif opt_method == "6_match_idlePick":
        opt_idle_pick(av_fleet, customers, t)
    elif opt_method == "7_match_idleDrop":
        opt_idle_drop(av_fleet, customers, t)
    elif opt_method == "7_match_idleDrop2":
        opt_idle_drop2(av_fleet, customers, t)
    elif opt_method == "8_match_idlePickDrop":
        opt_idle_pick_drop(av_fleet, customers, t)
    else:
        print("Error: No_assignment_method")
    return
#############################################################################################################


# Dandl
# This just checks what relocating method we are using, and then sends information to specific relocation algorithm
# comment FD:
# 1) i advise to give the whole area class as input parameter
# 2) the forecast will need to know which weekday it is
# 3) might be necessary to pass more parameters for my algorithm:
# - length of time horizon
# - minimal imbalance


#############################################################################################################
def relocate_veh(av_fleet, area, relocate_method, t, weekday):
    answer = "blank"
    if relocate_method == "Dandl":
        answer = relocate_dandl(av_fleet, area, t, weekday)   # <-- this function is at bottom of file
    # elif relocate_method == "Hyland":
    #     answer = relocate_hyland(av_fleet, area, t, weekday)
    else:
        print("Error: No_assignment_method")
    return answer
#############################################################################################################



#############################################################################################################
def fcfs_longest_idle(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    len_avs = len(idle_avs)
    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    len_custs = len(unassign_cust)

    most_match_count = min(len_custs, len_avs)
    for z_match in range(most_match_count):
        min_request_time = min(list(i.request_time for i in unassign_cust))
        max_wait_cust = list(i for i in unassign_cust if i.request_time == min_request_time)[0]
        min_last_drop_time = min(list(j.last_drop_time for j in idle_avs))
        long_wait_av = list(j for j in idle_avs if j.last_drop_time == min_last_drop_time)[0]

        temp_veh_status = "base_assign"
        Vehicle.update_vehicle(t, max_wait_cust, long_wait_av, Regions.SubArea, temp_veh_status)
        Person.update_person(t, max_wait_cust, long_wait_av)
    return
#############################################################################################################


#############################################################################################################
def fcfs_nearest_idle(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")

    used_vehicles = []
    count_p = -1
    for i_cust in unassign_cust:
        count_p += 1
        min_dist = Set.inf
        win_veh_index = -1
        veh_index = -1
        for j_av in idle_avs:
            veh_index += 1
            dist = Distance.dist_manhat_pick(i_cust, j_av)
            # make sure that two persons aren't assigned to same vehicle
            if dist < min_dist and not (j_av.vehicle_id in used_vehicles):
                win_veh_index = veh_index
                min_dist = dist
        if win_veh_index >= 0:
            win_vehicle = idle_avs[win_veh_index]
            used_vehicles.append(win_vehicle.vehicle_id)

            temp_veh_status = "base_assign"
            Vehicle.update_vehicle(t, i_cust, win_vehicle, Regions.SubArea, temp_veh_status)
            Person.update_person(t, i_cust, win_vehicle)
    return
#############################################################################################################


#############################################################################################################
def fcfs_smart_nn(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    len_avs = len(idle_avs)
    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    len_custs = len(unassign_cust)

    if len_avs >= len_custs:
        used_vehicles = []
        for i_cust in unassign_cust:
            win_vehicle = Vehicle.Vehicle
            min_dist = Set.inf
            for j_av in idle_avs:
                dist = Distance.dist_manhat_pick(i_cust, j_av)
                # make sure that two persons aren't assigned to same vehicle
                if dist < min_dist and j_av not in used_vehicles:
                    win_vehicle = j_av
                    min_dist = dist
            if win_vehicle.vehicle_id >= 0:
                used_vehicles.append(win_vehicle)

                temp_veh_status = "base_assign"
                Vehicle.update_vehicle(t, i_cust, win_vehicle, Regions.SubArea, temp_veh_status)
                Person.update_person(t, i_cust, win_vehicle)
    else:
        win_cust_list = []
        for j_av in idle_avs:
            min_dist = Set.inf
            win_cust = Person.Person
            for i_cust in unassign_cust:
                dist = Distance.dist_manhat_pick(i_cust, j_av)
                if dist < min_dist and i_cust not in win_cust_list:
                    win_cust = i_cust
                    min_dist = dist
            if win_cust.person_id >= 0:
                win_cust_list.append(win_cust)

                temp_veh_status = "base_assign"
                Vehicle.update_vehicle(t, win_cust, j_av, Regions.SubArea, temp_veh_status)
                Person.update_person(t, win_cust, j_av)
    return
#############################################################################################################


############################################################################################################
def fcfs_drop_smart_nn(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    drop_avs = list(k_av for k_av in av_fleet if k_av.status == "enroute_dropoff" and k_av.next_pickup.person_id < 0)

    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    len_custs = len(unassign_cust)

    idle_n_drop_avs = idle_avs + drop_avs
    tot_veh_length = len(idle_n_drop_avs)

    if tot_veh_length >= len_custs:
        used_vehicles = []
        for i_cust in unassign_cust:
            min_dist = Set.inf
            win_av = Vehicle.Vehicle
            for j_av in idle_n_drop_avs:
                if j_av.status == "enroute_dropoff":
                    dist = Distance.dist_manhat_drop_pick(i_cust, j_av)
                else:
                    dist = Distance.dist_manhat_pick(i_cust, j_av)
                # make sure that two persons aren't assigned to same vehicle
                if dist < min_dist and j_av not in used_vehicles:
                    win_av = j_av
                    min_dist = dist
            if win_av.vehicle_id >= 0:
                used_vehicles.append(win_av)

                if win_av.status == "enroute_dropoff":
                    temp_veh_status = "new_assign"
                elif win_av.status == "idle":
                    temp_veh_status = "base_assign"
                else:
                    temp_veh_status = "wrong"

                Vehicle.update_vehicle(t, i_cust, win_av, Regions.SubArea, temp_veh_status)
                Person.update_person(t, i_cust, win_av)
    else:
        win_cust_list = []
        for j_av in idle_n_drop_avs:
            min_dist = Set.inf
            win_cust = Person.Person
            for i_cust in unassign_cust:
                if j_av.status == "enroute_dropoff":
                    dist = Distance.dist_manhat_drop_pick(i_cust, j_av)
                else:
                    dist = Distance.dist_manhat_pick(i_cust, j_av)

                if dist < min_dist and i_cust not in win_cust_list:
                    win_cust = i_cust
                    min_dist = dist

            if win_cust.person_id >= 0:
                win_cust_list.append(win_cust)

                if j_av.status == "enroute_dropoff":
                    temp_veh_status = "new_assign"
                elif j_av.status == "idle":
                    temp_veh_status = "base_assign"
                else:
                    temp_veh_status = "wrong"

                Vehicle.update_vehicle(t, win_cust, j_av, Regions.SubArea, temp_veh_status)
                Person.update_person(t, win_cust, j_av)
    return
#############################################################################################################


# changed one if condition
############################################################################################################
def fcfs_drop_smart_nn2(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    len_idle_avs = len(idle_avs)
    drop_avs = list(k_av for k_av in av_fleet if k_av.status == "enroute_dropoff" and k_av.next_pickup.person_id < 0)

    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    len_custs = len(unassign_cust)

    idle_n_drop_avs = idle_avs + drop_avs

    if len_idle_avs >= len_custs:
        used_vehicles = []
        for i_cust in unassign_cust:
            min_dist = Set.inf
            win_av = Vehicle.Vehicle
            for j_av in idle_n_drop_avs:
                if j_av.status == "enroute_dropoff":
                    dist = Distance.dist_manhat_drop_pick(i_cust, j_av)
                else:
                    dist = Distance.dist_manhat_pick(i_cust, j_av)
                # make sure that two persons aren't assigned to same vehicle
                if dist < min_dist and j_av not in used_vehicles:
                    win_av = j_av
                    min_dist = dist
            if win_av.vehicle_id >= 0:
                used_vehicles.append(win_av)

                if win_av.status == "enroute_dropoff":
                    temp_veh_status = "new_assign"
                elif win_av.status == "idle":
                    temp_veh_status = "base_assign"
                else:
                    temp_veh_status = "wrong"

                Vehicle.update_vehicle(t, i_cust, win_av, Regions.SubArea, temp_veh_status)
                Person.update_person(t, i_cust, win_av)
    else:
        win_cust_list = []
        for j_av in idle_n_drop_avs:
            min_dist = Set.inf
            win_cust = Person.Person
            for i_cust in unassign_cust:
                if j_av.status == "enroute_dropoff":
                    dist = Distance.dist_manhat_drop_pick(i_cust, j_av)
                else:
                    dist = Distance.dist_manhat_pick(i_cust, j_av)

                if dist < min_dist and i_cust not in win_cust_list:
                    win_cust = i_cust
                    min_dist = dist

            if win_cust.person_id >= 0:
                win_cust_list.append(win_cust)

                if j_av.status == "enroute_dropoff":
                    temp_veh_status = "new_assign"
                elif j_av.status == "idle":
                    temp_veh_status = "base_assign"
                else:
                    temp_veh_status = "wrong"

                Vehicle.update_vehicle(t, win_cust, j_av, Regions.SubArea, temp_veh_status)
                Person.update_person(t, win_cust, j_av)
    return
#############################################################################################################


#############################################################################################################
def opt_idle(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    len_idle_avs = len(idle_avs)

    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    len_custs = len(unassign_cust)

    dist_assgn = [[0 for jj in range(len_idle_avs)] for ii in range(len_custs)]
    x = [[0 for jj in range(len_idle_avs)] for ii in range(len_custs)]

    count_pass = -1
    for i_pass in unassign_cust:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        elapsed_wait_penalty = cur_wait * Set.gamma
        for j_veh in idle_avs:
            count_veh += 1
            av_curb_wait = j_veh.curb_time_remain * Set.veh_speed
            dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - \
                                                elapsed_wait_penalty + av_curb_wait

    t1 = time.time()
# Model
    models = gurobipy.Model("idleOnly_minDist")
    models.setParam('OutputFlag', False)

# Decision Variables
    for i in range(len_custs):
        for j in range(len_idle_avs):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=dist_assgn[i][j], name='x_%s_%s' % (i,j))
    models.update()

# constraints

    # if the number of unassigned travelers is less than the number of idle vehicles
    # then make sure all the unassigned travelers are assigned a vehicle
    if len_custs <= len_idle_avs:
        for ii in range(len_custs):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_idle_avs)) == 1)
        for jj in range(len_idle_avs):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_custs)) <= 1)
    # else if the number of unassigned travelers is greater than the number of idle vehicles
        # then make sure all the idle vehicles are assigned to an unassigned traveler
    else:
        for ii in range(len_custs):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_idle_avs)) <= 1)
        for jj in range(len_idle_avs):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_custs)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_pass in range(len_custs):
            for n_veh in range(len_idle_avs):
                if x[m_pass][n_veh].X == 1:
                    temp_veh_status = "base_assign"
                    win_cust = unassign_cust[m_pass]
                    win_av = idle_avs[n_veh]
                    Vehicle.update_vehicle(t, win_cust, win_av, Regions.SubArea, temp_veh_status)
                    Person.update_person(t, win_cust, win_av)
                    break
    else:
        sys.exit("No Optimal Solution - idleOnly_minDist")
    # print("Vehicles= ", len_veh, "  Passengers= ", len_pass, "  time=", time.time() - t1)
    return
#############################################################################################################


#############################################################################################################
def opt_idle_pick(av_fleet, customers, t):

    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    assign_cust = list(ii_cust for ii_cust in customers if ii_cust.status == "assigned")
    temp_av_fleet = av_fleet[:]

    for j_av in temp_av_fleet:
        i_cust = j_av.next_pickup
        if i_cust.reassigned == 1:
            assign_cust.remove(i_cust)
            temp_av_fleet.remove(j_av)

    idle_avs = list(j_veh for j_veh in temp_av_fleet if j_veh.status == "idle")
    pick_avs = list(j_veh for j_veh in temp_av_fleet if j_veh.status == "enroute_pickup")

    # just want to get avs in the right order
    idle_n_pick_avs = idle_avs + pick_avs
    len_idle_n_pick_av = len(idle_n_pick_avs)

    no_assign_or_pick_cust = unassign_cust + assign_cust
    len_no_assign_or_pick_cust = len(no_assign_or_pick_cust)

    dist_assgn = [[0 for j in range(len_idle_n_pick_av)] for i in range(len_no_assign_or_pick_cust)]
    x = [[0 for j in range(len_idle_n_pick_av)] for i in range(len_no_assign_or_pick_cust)]
    prev_assign = [0 for z in range(len_no_assign_or_pick_cust)]

    count_pass = -1
    for i_pass in no_assign_or_pick_cust:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        elapsed_wait_penalty = cur_wait * Set.gamma
        for j_veh in idle_n_pick_avs:
            count_veh += 1

            if i_pass.status == "unassigned":

                if j_veh.status == "idle":
                    av_curb_wait = j_veh.curb_time_remain * Set.veh_speed
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + av_curb_wait
                elif j_veh.status == "enroute_pickup":
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + Set.reassign_penalty
                else:
                    sys.exit("Something wrong with AV state - idlePick_minDist")

            elif i_pass.status == "assigned":
                prev_assign[count_pass] = 1

                if j_veh.next_pickup == i_pass:
                    if j_veh.status == "enroute_pickup":
                        dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty
                    else:
                        sys.exit("Something wrong with current AV-customer match - idlePick_minDist")

                elif j_veh.status == "idle":
                    av_curb_wait = j_veh.curb_time_remain * Set.veh_speed
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + Set.reassign_penalty + av_curb_wait
                elif j_veh.status == "enroute_pickup":
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + 2*Set.reassign_penalty
                else:
                    sys.exit("Something wrong with AV state - idlePick_minDist")
            else:
                sys.exit("Something wrong with customer state - idlePick_minDist")
    t1 = time.time()

    # Model
    models = gurobipy.Model("idlePick_minDist")
    models.setParam('OutputFlag', False)

    # Decision Variables
    for i in range(len_no_assign_or_pick_cust):
        for j in range(len_idle_n_pick_av):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=dist_assgn[i][j], name='x_%s_%s' % (i,j))
    models.update()

    # constraints

    # Previously assigned passengers must be assigned a vehicle
    for ii in range(len_no_assign_or_pick_cust):
        models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_idle_n_pick_av)) - prev_assign[ii] >= 0)

    if len_no_assign_or_pick_cust <= len_idle_n_pick_av:
        for ii in range(len_no_assign_or_pick_cust):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_idle_n_pick_av)) == 1)
        for jj in range(len_idle_n_pick_av):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_no_assign_or_pick_cust)) <= 1)

    else:
        for ii in range(len_no_assign_or_pick_cust):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_idle_n_pick_av)) <= 1)
        for jj in range(len_idle_n_pick_av):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_no_assign_or_pick_cust)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for n_veh in range(len_idle_n_pick_av):
            found = 0
            for m_pass in range(len_no_assign_or_pick_cust):
                if x[m_pass][n_veh].X == 1:
                    win_cust = no_assign_or_pick_cust[m_pass]
                    win_av = idle_n_pick_avs[n_veh]

                    if win_av.next_pickup != win_cust:

                        if win_cust.status == "unassigned":
                            Person.update_person(t, win_cust, win_av)
                        elif win_cust.status == "assigned":
                            win_cust.status = "reassign"
                            Person.update_person(t, win_cust, win_av)

                        if win_av.status == "idle":
                            temp_veh_status = "base_assign"
                        elif win_av.status == "enroute_pickup":
                            temp_veh_status = "reassign"
                        else:
                            temp_veh_status = "wrong"

                        Vehicle.update_vehicle(t, win_cust, win_av, Regions.SubArea, temp_veh_status)

                    found = 1
                    break

            if found == 0:
                no_win_av = idle_n_pick_avs[n_veh]
                if no_win_av.status == "enroute_pickup":
                    temp_veh_status = "unassign"
                    Vehicle.update_vehicle(t, Person.Person, no_win_av, Regions.SubArea, temp_veh_status)
    else:
        sys.exit("No Optimal Solution - idlePick_minDist")
    # print("Vehicles= ", tot_veh_length, "  Passengers= ", len_no_assign_or_pick_cust, "  time=", time.time()-t1)
    return
#############################################################################################################


#############################################################################################################
def opt_idle_drop(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    len_idle_avs = len(idle_avs)
    drop_avs = list(k_av for k_av in av_fleet if k_av.status == "enroute_dropoff" and k_av.next_pickup.person_id < 0)

    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    len_custs = len(unassign_cust)

    idle_n_drop_avs = idle_avs + drop_avs
    tot_veh_length = len(idle_n_drop_avs)

    dist_assgn = [[0 for j in range(tot_veh_length)] for i in range(len_custs)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_custs)]

    count_pass = -1
    for i_pass in unassign_cust:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        elapsed_wait_penalty = cur_wait * Set.gamma
        for j_veh in idle_n_drop_avs:
            count_veh += 1

            # if vehicle state is enroute_dropoff - need to include dropoff distance as well
            if count_veh >= len_idle_avs:
                av_curb_wait = Set.curb_drop_time * Set.veh_speed
                dist_assgn[count_pass][count_veh] = Distance.dist_manhat_drop_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                               + Set.dropoff_penalty + av_curb_wait
            else:
                av_curb_wait = j_veh.curb_time_remain * Set.veh_speed
                dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty + av_curb_wait

    t1 = time.time()
    # Model
    models = gurobipy.Model("idleDrop_minDist")
    models.setParam('OutputFlag', False)

    # Decision Variables
    for i in range(len_custs):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=dist_assgn[i][j], name='x_%s_%s' % (i, j))
    models.update()

    # constraints
    if len_custs <= tot_veh_length:
        for ii in range(len_custs):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) == 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_custs)) <= 1)

    else:
        for ii in range(len_custs):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) <= 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_custs)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_pass in range(len_custs):
            for n_veh in range(tot_veh_length):
                if x[m_pass][n_veh].X == 1:
                    win_cust = unassign_cust[m_pass]
                    win_av = idle_n_drop_avs[n_veh]

                    if win_av.status == "idle":
                        temp_veh_status = "base_assign"
                    elif win_av.status == "enroute_dropoff":
                        temp_veh_status = "new_assign"
                    else:
                        temp_veh_status = "wrong"

                    Vehicle.update_vehicle(t, win_cust, win_av, Regions.SubArea, temp_veh_status)
                    Person.update_person(t, win_cust, win_av)
                    break
    else:
        sys.exit("No Optimal Solution - idleDrop_minDist")
    # print("Vehicles= ", tot_veh_length, "  Passengers= ", len_pass, "  time=", time.time() - t1)
    return
#############################################################################################################


# changed one if condition and one set of constraints
#############################################################################################################
def opt_idle_drop2(av_fleet, customers, t):
    idle_avs = list(j_veh for j_veh in av_fleet if j_veh.status == "idle")
    len_idle_avs = len(idle_avs)
    drop_avs = list(k_av for k_av in av_fleet if k_av.status == "enroute_dropoff" and k_av.next_pickup.person_id < 0)

    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    len_custs = len(unassign_cust)

    idle_n_drop_avs = idle_avs + drop_avs
    tot_veh_length = len(idle_n_drop_avs)

    dist_assgn = [[0 for j in range(tot_veh_length)] for i in range(len_custs)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_custs)]

    count_pass = -1
    for i_pass in unassign_cust:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        elapsed_wait_penalty = cur_wait * Set.gamma
        for j_veh in idle_n_drop_avs:
            count_veh += 1

            # if vehicle state is enroute_dropoff - need to include dropoff distance as well
            if count_veh >= len_idle_avs:
                av_curb_wait = Set.curb_drop_time * Set.veh_speed
                dist_assgn[count_pass][count_veh] = Distance.dist_manhat_drop_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                               + Set.dropoff_penalty + av_curb_wait
            else:
                av_curb_wait = j_veh.curb_time_remain * Set.veh_speed
                dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty + av_curb_wait

    t1 = time.time()
    # Model
    models = gurobipy.Model("idleDrop_minDist")
    models.setParam('OutputFlag', False)

    # Decision Variables
    for i in range(len_custs):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=dist_assgn[i][j], name='x_%s_%s' % (i, j))
    models.update()

    # constraints
    if len_custs <= len_idle_avs:
        for ii in range(len_custs):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) == 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_custs)) <= 1)

    # if # open requests > # idle AVs;
    else:
        # then, make sure the total number of assigned customers at least number of idle AVs
        models.addConstr(
            gurobipy.quicksum(x[iii][jjj] for iii in range(len_custs) for jjj in range(tot_veh_length)) >= len_idle_avs)
        # then, assign passenger to at most one AV
        for ii in range(len_custs):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) <= 1)
        # then, assign AV to at most one passenger
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_custs)) <= 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_pass in range(len_custs):
            for n_veh in range(tot_veh_length):
                if x[m_pass][n_veh].X == 1:
                    win_cust = unassign_cust[m_pass]
                    win_av = idle_n_drop_avs[n_veh]

                    if win_av.status == "idle":
                        temp_veh_status = "base_assign"
                    elif win_av.status == "enroute_dropoff":
                        temp_veh_status = "new_assign"
                    else:
                        temp_veh_status = "wrong"

                    Vehicle.update_vehicle(t, win_cust, win_av, Regions.SubArea, temp_veh_status)
                    Person.update_person(t, win_cust, win_av)
                    break
    else:
        sys.exit("No Optimal Solution - idleDrop_minDist")
    # print("Vehicles= ", tot_veh_length, "  Passengers= ", len_pass, "  time=", time.time() - t1)
    return
#############################################################################################################


#############################################################################################################
def opt_idle_pick_drop(av_fleet, customers, t):

    unassign_cust = list(i_cust for i_cust in customers if i_cust.status == "unassigned")
    assign_cust = list(ii_cust for ii_cust in customers if ii_cust.status == "assigned")
    temp_av_fleet = av_fleet[:]

    for j_av in temp_av_fleet:
        i_cust = j_av.next_pickup
        if i_cust.reassigned == 1:
            assign_cust.remove(i_cust)
            temp_av_fleet.remove(j_av)

    idle_avs = list(j_veh for j_veh in temp_av_fleet if j_veh.status == "idle")
    drop_avs = list(j_veh for j_veh in temp_av_fleet if j_veh.status == "enroute_dropoff")
    pick_avs = list(j_veh for j_veh in temp_av_fleet if j_veh.status == "enroute_pickup")

    # just want to get avs in the right order
    all_avs = idle_avs + drop_avs + pick_avs
    tot_veh_length = len(all_avs)

    no_assign_or_pick_cust = unassign_cust + assign_cust
    len_no_assign_or_pick_cust = len(no_assign_or_pick_cust)

    dist_assgn = [[0 for j in range(tot_veh_length)] for i in range(len_no_assign_or_pick_cust)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_no_assign_or_pick_cust)]
    prev_assign = [0 for z in range(len_no_assign_or_pick_cust)]

    count_pass = -1
    for i_pass in no_assign_or_pick_cust:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        elapsed_wait_penalty = cur_wait * Set.gamma
        for j_veh in all_avs:
            count_veh += 1

            if i_pass.status == "unassigned":

                if j_veh.status == "idle":
                    av_curb_wait = j_veh.curb_time_remain * Set.veh_speed
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + av_curb_wait
                elif j_veh.status == "enroute_dropoff":
                    av_curb_wait = Set.curb_drop_time * Set.veh_speed
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_drop_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + Set.dropoff_penalty + av_curb_wait
                elif j_veh.status == "enroute_pickup":
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + Set.reassign_penalty
                else:
                    sys.exit("Something wrong with AV state - idlePickDrop_minDist")

            elif i_pass.status == "assigned":
                prev_assign[count_pass] = 1

                if j_veh.next_pickup == i_pass:
                    if j_veh.status == "enroute_pickup":
                        dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty
                    elif j_veh.status == "enroute_dropoff":
                        av_curb_wait = Set.curb_drop_time * Set.veh_speed
                        dist_assgn[count_pass][count_veh] = Distance.dist_manhat_drop_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + Set.dropoff_penalty + av_curb_wait
                    else:
                        sys.exit("Something wrong with current AV-customer match - idlePickDrop_minDist")

                elif j_veh.status == "idle":
                    av_curb_wait = j_veh.curb_time_remain * Set.veh_speed
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + Set.reassign_penalty + av_curb_wait
                elif j_veh.status == "enroute_dropoff":
                    av_curb_wait = Set.curb_drop_time * Set.veh_speed
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_drop_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + Set.dropoff_penalty + Set.reassign_penalty + av_curb_wait
                elif j_veh.status == "enroute_pickup":
                    dist_assgn[count_pass][count_veh] = Distance.dist_manhat_pick(i_pass, j_veh) - elapsed_wait_penalty \
                                                   + 2*Set.reassign_penalty
                else:
                    sys.exit("Something wrong with AV state - idlePickDrop_minDist")
            else:
                sys.exit("Something wrong with customer state - idlePickDrop_minDist")
    t1 = time.time()

    # Model
    models = gurobipy.Model("idlePickDrop_minDist")
    models.setParam( 'OutputFlag', False )

    # Decision Variables
    for i in range(len_no_assign_or_pick_cust):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=dist_assgn[i][j], name='x_%s_%s' % (i,j))
    models.update()

    # constraints

    # Previously assigned passengers must be assigned a vehicle
    for ii in range(len_no_assign_or_pick_cust):
        models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) - prev_assign[ii] >= 0)

    if len_no_assign_or_pick_cust <= tot_veh_length:
        for ii in range(len_no_assign_or_pick_cust):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) == 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_no_assign_or_pick_cust)) <= 1)

    else:
        for ii in range(len_no_assign_or_pick_cust):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) <= 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_no_assign_or_pick_cust)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for n_veh in range(tot_veh_length):
            found = 0
            for m_pass in range(len_no_assign_or_pick_cust):
                if x[m_pass][n_veh].X == 1:
                    win_cust = no_assign_or_pick_cust[m_pass]
                    win_av = all_avs[n_veh]

                    if win_av.next_pickup != win_cust:

                        if win_cust.status == "unassigned":
                            Person.update_person(t, win_cust, win_av)
                        elif win_cust.status == "assigned":
                            win_cust.status = "reassign"
                            Person.update_person(t, win_cust, win_av)

                        if win_av.status == "idle":
                            temp_veh_status = "base_assign"
                        elif win_av.status == "enroute_dropoff":
                            temp_veh_status = "new_assign"
                        elif win_av.status == "enroute_pickup":
                            temp_veh_status = "reassign"
                        else:
                            temp_veh_status = "wrong"
                        Vehicle.update_vehicle(t, win_cust, win_av, Regions.SubArea, temp_veh_status)
                    found = 1
                    break
            if found == 0:
                no_win_av = all_avs[n_veh]
                if no_win_av.status in["enroute_pickup", "enroute_dropoff"]:
                    temp_veh_status = "unassign"
                    Vehicle.update_vehicle(t, Person.Person, no_win_av, Regions.SubArea, temp_veh_status)
    else:
        sys.exit("No Optimal Solution - idlePickDrop_minDist")
    # print("Vehicles= ", tot_veh_length, "  Passengers= ", len_no_assign_or_pick_cust, "  time=", time.time()-t1)
    return
#############################################################################################################



# Dandl
# Code relocation algorithm in this function
# Input: complete information about all vehicles and all sub_areas, as well as the current time
# Output: I can basically work with anything, but possibly, a list of AVs to relocate, and their relocating subAreas
#

#############################################################################################################
#def relocate_dandl(av_fleet, area, t, weekday, time_horizon, min_imbalance):
def relocate_dandl(av_fleet, area, t, weekday):

    # Comment FD:
    # changed input sub_areas to the whole area class
    # it might be necessary to add two more parameters -> it might be interesting to see how they influence results
    time_horizon = 30 * 60  # rolling horizon in seconds
    min_imbalance = 3  # below this imbalance, operator should not act
    penalty_remaining_imbalance = time_horizon / 2  # penalty for remaining single imbalance unit of a subArea



    # approach:
    # ---------
    # 1) create vehicle availability list
    # 2) loop over subAreas:
    #    + read demand forecast
    #    + count availability until 't + time_horizon'
    #    + compute imbalance = forecast - availability count
    #    + if imbalance <= -1 * min_imbalance:
    #        -> create list of currently available vehicles for relocations
    #    + elif imbalance >= min_imbalance:
    #        -> create single vehicle deficiencies according to number of deficiencies per subArea:
    #            1st: penalty factor 1 | 2nd: penalty factor 2 | 3rd: penalty factor 3 | ...
    #            idea: it is more important to decrease large imbalances than to have many short
    #                  trips between nearby areas with small imbalances
    # 3) compute distance matrix between currently available vehicles and single vehicle deficiencies
    #        (only one computation per subArea) and "remove" combination if v*distance > time_horizon
    #        by artificially increasing the costs
    # 4) create and solve optimization problem
    #
    # either deficiency in an area is assigned to a vehicle or a penalty term is added to
    # total objective function
    # min_{x_lj} sum_l (P_l chi_l + sum_j co_lj xo_lj)
    # s.t. chi_l + sum_j xo_lj = 1
    #      sum_l xo_lj <= 1
    #
    # -> define chi_l as additional variables with c_lj = P_l for l=len(veh) + j
    # min_{x_lj} sum_{l,j} c_lj x_lj
    # s.t. sum_j x_lj = 1
    #      sum_l x_lj <= 1
    #
    # 5) output in following format: list of [(j_veh, l_sub_area), ...]
    #
    # 1)
    # veh_av_dict = {}          # subArea -> list of (veh_counter, av_time)
    veh_av_dict = area.getVehicleAvailabilitiesPerArea(av_fleet)
    # 2)
    veh_av_for_relocation = []  # list of veh_obj
    sub_area_deficiency = []    # list of (subArea_obj, penalty_factor)
    all_def_id = 0

    ####################################################
    # Help FD!
    for sa_key, c_subArea in area.sub_areas.items():
        # Issue 1: getDemandPredictionsPerArea is an attribute of Area not SubArea
        fc_val = c_subArea.getDemandPredictionsPerArea(weekday, t, time_horizon)
        av_veh_info_list = veh_av_dict[sa_key]
        # Issue 2: av_veh_val is never defined. I think it could be defined as  av_veh_val = av_veh_info_list[0]?
        imbalance = fc_val - av_veh_val

    # Help FD!
    ####################################################

        if imbalance <= -1* min_imbalance:
            region_idle_counter = 0
            for entry in av_veh_info_list:
                (veh_counter, av_time) = entry
                if av_time == t and region_idle_counter <= -1*imbalance:
                    veh_av_for_relocation.append(av_fleet[veh_counter])
                    region_idle_counter += 1
        elif imbalance >= min_imbalance:
            region_penalty_factor = 1
            for i in range(imbalance):
                sub_area_deficiency.append((c_subArea, region_penalty_factor))
                all_def_id += 1
                region_penalty_factor += 1
    len_sd = len(sub_area_deficiency)
    len_veh = len(veh_av_for_relocation)
    # 3)
    # timeDistM = [[0 for j in range(len(veh_av_for_relocation))] for l in range(len(sorted_deficiencies))] add eye matrix for penalty terms
    # timeDistM = [[0 for j in range(len(veh_av_for_relocation)+len(sorted_deficiencies))] for l in range(len(sorted_deficiencies))]
    # Comment MH: Changed sorted_deficiencies to sub_area_deficiency
    # and added initialization of x array
    timeDistM = [[0 for j in range(len(veh_av_for_relocation)+len(sub_area_deficiency))] for l in range(len(sub_area_deficiency))]
    x = [[0 for j in range(len(veh_av_for_relocation))] for l in range(len(sub_area_deficiency))]

    count_sad = -1
    for entry in sub_area_deficiency:
        count_sad += 1
        (c_subArea, region_penalty_factor) = entry
        count_veh = -1
        for j_veh in veh_av_for_relocation:
            count_veh += 1
#               dist_veh_subArea = Distance.dist_manhat_region(j_veh, c_subArea) - trav_wait_penalty \
#                                            + j_veh.curb_time_remain * Set.veh_speed
            dist_veh_subArea = Distance.dist_manhat_region(j_veh, c_subArea)
            # Comment FD: correct units of following line?
            # Response MH: veh_speed now 5.0 m/s
            # remind me to make sure that the entire set of code is in meters not feet or miles
            time_veh_subArea = 1.0 * dist_veh_subArea / Set.veh_speed
            if time_veh_subArea < time_horizon:
                timeDistM[count_sad][count_veh] = time_veh_subArea
            else:
                timeDistM[count_sad][count_veh] = 1000 * time_veh_subArea # any large factor will do
        # penalty term
        timeDistM[count_sad][len(veh_av_for_relocation) + count_sad] = region_penalty_factor
    # 4)
    t1 = time.time()
    # Model
    models = gurobipy.Model("relocate_dandl")
    models.setParam( 'OutputFlag', False )

    # Decision Variables
    for l in range(len_sd):
        for j in range(len_veh):
            x[l][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=timeDistM[l][j], name='x_%s_%s' % (l,j))
    models.update()

    # constraints
    # deficiency either assigned to vehicle or to penalty term
    for ll in range(len_sd):
        models.addConstr(gurobipy.quicksum(x[ll][j] for j in range(len_veh + len_sd)) == 1)
    # vehicle possibly assigned
    for jj in range(len_veh):
        models.addConstr(gurobipy.quicksum(x[l][jj] for l in range(len_sd)) <= 1)


    models.optimize()

    # 5)
    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_sd in range(len_sd):
            for n_veh in range(len_veh):
                if x[m_sd][n_veh].X == 1:
                    temp_veh_status = "relocating"
                    win_av = veh_av_for_relocation[n_veh]
                    l_subarea = sub_area_deficiency[m_sd]
                    Vehicle.update_vehicle(t, Person.Person, win_av, l_subarea, temp_veh_status)
                    break
    else:
        sys.exit("No Optimal Solution - relocate_dandl")
    # print("Vehicles= ", len_veh, "  Passengers= ", len_pass, "  time=", time.time() - t1)
    return
#############################################################################################################