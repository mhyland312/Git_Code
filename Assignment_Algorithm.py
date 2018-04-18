import Distance
import gurobipy
import Settings as Set
import Vehicle
import sys
import time

__author__ = 'Mike'

#############################################################################################################
def assign_veh_fcfs(veh_idle_q, veh_drop_q, pass_no_assign_q, opt_method):
    answer = "blank"
    if opt_method == "FCFS_longestIdle":
        answer = fcfs_longest_idle(veh_idle_q, pass_no_assign_q)
    elif opt_method == "FCFS_nearestIdle":
        answer = fcfs_nearest_idle(veh_idle_q, pass_no_assign_q)
    elif opt_method == "FCFS_smartNN":
        answer = FCFS_smartNN(veh_idle_q, pass_no_assign_q)
    elif opt_method == "FCFS_drop_smartNN":
        answer = FCFS_drop_smartNN(veh_idle_q, veh_drop_q, pass_no_assign_q)
    elif opt_method == "FCFS_drop_smartNN2":
        answer = FCFS_drop_smartNN(veh_idle_q, veh_drop_q, pass_no_assign_q)
    else:
        print("Error: No_FCFS_assignment_method")
    return answer
#############################################################################################################

#############################################################################################################
def assign_veh_opt(veh_idle_q, veh_pick_q, veh_drop_q, pass_no_assign_q, pass_no_pick_q, opt_method, t):
    answer = "blank"
    if opt_method == "match_idleOnly":
        answer = idleOnly_minDist(veh_idle_q, pass_no_assign_q, t)
    elif opt_method == "match_idlePick":
        answer = idlePick_minDist(veh_idle_q, veh_pick_q, pass_no_assign_q, pass_no_pick_q, t)
    elif opt_method == "match_idleDrop":
        answer = idleDrop_minDist(veh_idle_q, veh_drop_q, pass_no_assign_q, pass_no_pick_q, t)
    elif opt_method == "match_idlePickDrop":
        answer = idlePickDrop_minDist(veh_idle_q, veh_pick_q, veh_drop_q, pass_no_assign_q, pass_no_pick_q, t)
    else:
        print("Error: No_assignment_method")
    return answer
#############################################################################################################


#############################################################################################################
def fcfs_longest_idle(veh_idle_q, pass_no_assign_q):
    len_veh = len(veh_idle_q)
    len_pass = len(pass_no_assign_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass)]

    max_match = min(len_pass, len_veh)
    for i_match in range(max_match):
        pass_veh_assign[i_match] = [pass_no_assign_q[i_match], veh_idle_q[i_match]]

    return pass_veh_assign
#############################################################################################################


#############################################################################################################
def fcfs_nearest_idle(veh_idle_q, pass_no_assign_q):
    len_pass = len(pass_no_assign_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass)]

    used_vehicles = []
    count_p = -1
    for i_person in pass_no_assign_q:
        count_p += 1
        min_dist = Set.inf
        win_veh_index = -1
        veh_index = -1
        for j_veh in veh_idle_q:
            veh_index += 1
            dist = Distance.dist_manhat(i_person, j_veh)
            # make sure that two persons aren't assigned to same vehicle
            if dist < min_dist and not (j_veh.vehicle_id in used_vehicles):
                win_veh_index = veh_index
                min_dist = dist
        if win_veh_index >= 0:
            win_vehicle = veh_idle_q[win_veh_index]
            used_vehicles.append(win_vehicle.vehicle_id)
        else:
            win_vehicle = Vehicle.Vehicle
        pass_veh_assign[count_p] = [i_person, win_vehicle]

    return pass_veh_assign
#############################################################################################################


#############################################################################################################
def FCFS_smartNN(veh_idle_q, pass_no_assign_q):
    len_pass = len(pass_no_assign_q)
    len_veh = len(veh_idle_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass)]

    temp_pass_no_assign_q = pass_no_assign_q[0:len(pass_no_assign_q)]

    if len_veh >= len_pass:
        used_vehicles = []
        count_p = -1
        for i_person in pass_no_assign_q:
            count_p += 1
            min_dist = Set.inf
            win_veh_index = -1
            veh_index = -1
            for j_veh in veh_idle_q:
                veh_index += 1
                dist = Distance.dist_manhat(i_person, j_veh)
                # make sure that two persons aren't assigned to same vehicle
                if dist < min_dist and not (j_veh.vehicle_id in used_vehicles):
                    win_veh_index = veh_index
                    min_dist = dist
            if win_veh_index >= 0:
                win_vehicle = veh_idle_q[win_veh_index]
                used_vehicles.append(win_vehicle.vehicle_id)
            else:
                win_vehicle = Vehicle.Vehicle
            pass_veh_assign[count_p] = [i_person, win_vehicle]

    else:
        for j_veh in veh_idle_q:
            min_dist = Set.inf
            win_pass_index = -1
            pass_index = -1
            for i_person in temp_pass_no_assign_q:
                pass_index += 1
                dist = Distance.dist_manhat(i_person, j_veh)
                if dist < min_dist:
                    win_pass_index = pass_index
                    min_dist = dist
            if win_pass_index >= 0:
                win_pass = temp_pass_no_assign_q[win_pass_index]
                temp_pass_no_assign_q.remove(win_pass)

                temp_index = pass_no_assign_q.index(win_pass)
                pass_veh_assign[temp_index] = [win_pass, j_veh]

    return pass_veh_assign
#############################################################################################################



############################################################################################################
def FCFS_drop_smartNN(veh_idle_q, veh_drop_q, pass_no_assign_q):
    # remove vehicles from dropoff queue that already have another pickup after their dropoff
    new_veh_drop_queue = []
    for a_veh in veh_drop_q:
        if a_veh.next_pickup.person_id < 0:
            new_veh_drop_queue.append(a_veh)

    len_veh_idle = len(veh_idle_q)
    veh_idle_n_drop_Q = veh_idle_q + new_veh_drop_queue
    tot_veh_length = len(veh_idle_n_drop_Q)

    len_pass = len(pass_no_assign_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass)]

    temp_pass_no_assign_q = pass_no_assign_q[0:len(pass_no_assign_q)]

    if tot_veh_length >= len_pass:  #Flo wants to possible consider this
        used_vehicles = []
        count_p = -1
        for i_person in pass_no_assign_q:
            count_p += 1
            min_dist = Set.inf
            win_veh_index = -1
            veh_index = -1
            for j_veh in veh_idle_n_drop_Q:
                veh_index += 1
                if veh_index >= len_veh_idle:
                    dist = Distance.dyn_dist_manhat(i_person, j_veh)
                else:
                    dist = Distance.dist_manhat(i_person, j_veh)
                # make sure that two persons aren't assigned to same vehicle
                if dist < min_dist and not (j_veh.vehicle_id in used_vehicles):
                    win_veh_index = veh_index
                    min_dist = dist
            if win_veh_index >= 0:
                win_vehicle = veh_idle_n_drop_Q[win_veh_index]
                used_vehicles.append(win_vehicle.vehicle_id)
            else:
                win_vehicle = Vehicle.Vehicle
            pass_veh_assign[count_p] = [i_person, win_vehicle]

    else:
        for j_veh in veh_idle_n_drop_Q:
            min_dist = Set.inf
            win_pass_index = -1
            pass_index = -1
            for i_person in temp_pass_no_assign_q:
                pass_index += 1
                if j_veh.next_drop.person_id >= 0:
                    dist = Distance.dyn_dist_manhat(i_person, j_veh)
                else:
                    dist = Distance.dist_manhat(i_person, j_veh)
                if dist < min_dist:
                    win_pass_index = pass_index
                    min_dist = dist
            if win_pass_index >= 0:
                win_pass = temp_pass_no_assign_q[win_pass_index]
                temp_pass_no_assign_q.remove(win_pass)

                temp_index = pass_no_assign_q.index(win_pass)
                pass_veh_assign[temp_index] = [win_pass, j_veh]

    return pass_veh_assign
#############################################################################################################



############################################################################################################
def FCFS_drop_smartNN2(veh_idle_q, veh_drop_q, pass_no_assign_q):
    # remove vehicles from dropoff queue that already have another pickup after their dropoff
    new_veh_drop_queue = []
    for a_veh in veh_drop_q:
        if a_veh.next_pickup.person_id < 0:
            new_veh_drop_queue.append(a_veh)

    len_veh_idle = len(veh_idle_q)
    veh_idle_n_drop_Q = veh_idle_q + new_veh_drop_queue
    tot_veh_length = len(veh_idle_n_drop_Q)

    len_pass = len(pass_no_assign_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass)]

    temp_pass_no_assign_q = pass_no_assign_q[0:len(pass_no_assign_q)]

    if len_veh_idle >= len_pass:  #Flo wants to possible consider this
        used_vehicles = []
        count_p = -1
        for i_person in pass_no_assign_q:
            count_p += 1
            min_dist = Set.inf
            win_veh_index = -1
            veh_index = -1
            for j_veh in veh_idle_n_drop_Q:
                veh_index += 1
                if veh_index >= len_veh_idle:
                    dist = Distance.dyn_dist_manhat(i_person, j_veh)
                else:
                    dist = Distance.dist_manhat(i_person, j_veh)
                # make sure that two persons aren't assigned to same vehicle
                if dist < min_dist and not (j_veh.vehicle_id in used_vehicles):
                    win_veh_index = veh_index
                    min_dist = dist
            if win_veh_index >= 0:
                win_vehicle = veh_idle_n_drop_Q[win_veh_index]
                used_vehicles.append(win_vehicle.vehicle_id)
            else:
                win_vehicle = Vehicle.Vehicle
            pass_veh_assign[count_p] = [i_person, win_vehicle]

    else:
        for j_veh in veh_idle_n_drop_Q:
            min_dist = Set.inf
            win_pass_index = -1
            pass_index = -1
            for i_person in temp_pass_no_assign_q:
                pass_index += 1
                if j_veh.next_drop.person_id >= 0:
                    dist = Distance.dyn_dist_manhat(i_person, j_veh)
                else:
                    dist = Distance.dist_manhat(i_person, j_veh)
                if dist < min_dist:
                    win_pass_index = pass_index
                    min_dist = dist
            if win_pass_index >= 0:
                win_pass = temp_pass_no_assign_q[win_pass_index]
                temp_pass_no_assign_q.remove(win_pass)

                temp_index = pass_no_assign_q.index(win_pass)
                pass_veh_assign[temp_index] = [win_pass, j_veh]

    return pass_veh_assign
#############################################################################################################



#############################################################################################################
def idleOnly_minDist(veh_idle_q, pass_no_assign_q, t):

    len_veh = len(veh_idle_q)
    len_pass = len(pass_no_assign_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass)]

    distM = [[0 for j in range(len_veh)] for i in range(len_pass)]
    x = [[0 for j in range(len_veh)] for i in range(len_pass)]

    count_pass = -1
    for i_pass in pass_no_assign_q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        trav_wait_penalty = cur_wait * Set.gamma
        for j_veh in veh_idle_q:
            count_veh += 1
            distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                           + j_veh.curb_time_remain * Set.veh_speed
    t1 = time.time()
# Model
    models = gurobipy.Model("idleOnly_minDist")
    models.setParam( 'OutputFlag', False )

# Decision Variables
    for i in range(len_pass):
        for j in range(len_veh):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

# constraints

    # if the number of unassigned travelers is less than the number of idle vehicles
        # then make sure all the unassigned travelers are assigned a vehicle
    if (len_pass <= len_veh):
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_veh)) == 1)
        for jj in range(len_veh):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) <= 1)
    # else if the number of unassigned travelers is greater than the number of idle vehicles
        # then make sure all the idle vehicles are assigned to an unassigned traveler
    else:
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_veh)) <= 1)
        for jj in range(len_veh):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_pass in range(len_pass):
            for n_veh in range(len_veh):
                if x[m_pass][n_veh].X == 1:
                    pass_veh_assign[m_pass] = [pass_no_assign_q[m_pass], veh_idle_q[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idleOnly_minDist")
    # print("Vehicles= ", len_veh, "  Passengers= ", len_pass, "  time=", time.time() - t1)
    return pass_veh_assign
#############################################################################################################


#############################################################################################################
def idleDrop_minDist(veh_idle_q, veh_drop_q, pass_no_assign_q, pass_no_pick_q, t):
    # remove vehicles from dropoff queue that already have another pickup after their dropoff
    new_veh_drop_queue = []
    for a_veh in veh_drop_q:
        if a_veh.next_pickup.person_id < 0:
            new_veh_drop_queue.append(a_veh)

    len_veh_idle = len(veh_idle_q)
    veh_idle_n_drop_Q = veh_idle_q + new_veh_drop_queue
    tot_veh_length = len(veh_idle_n_drop_Q)
    
    len_pass = len(pass_no_assign_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass)]

    distM = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]


    count_pass = -1
    for i_pass in pass_no_assign_q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        trav_wait_penalty = cur_wait*Set.gamma
        for j_veh in veh_idle_n_drop_Q:
            count_veh += 1
            # if vehicle state is enroute_dropoff - need to include dropoff distance as well
            if count_veh >= len_veh_idle:
                distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                               + Set.dropoff_penalty \
                                               + Set.curb_drop_time*Set.veh_speed
            else:
                distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                               + j_veh.curb_time_remain * Set.veh_speed

    t1 = time.time()
    # Model
    models = gurobipy.Model("idleDrop_minDist")
    models.setParam( 'OutputFlag', False )

    # Decision Variables
    for i in range(len_pass):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    # constraints
    if (len_pass <= tot_veh_length):
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) == 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) <= 1)

    else:
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) <= 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_pass in range(len_pass):
            for n_veh in range(tot_veh_length):
                if x[m_pass][n_veh].X == 1:
                    pass_veh_assign[m_pass] = [pass_no_assign_q[m_pass], veh_idle_n_drop_Q[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idleDrop_minDist")
    # print("Vehicles= ", tot_veh_length, "  Passengers= ", len_pass, "  time=", time.time() - t1)
    return pass_veh_assign
#############################################################################################################


#############################################################################################################
def idlePick_minDist(veh_idle_q, veh_pick_q, pass_no_assign_q, pass_no_pick_q, t):

    len_veh_idle = len(veh_idle_q)
    veh_idle_n_pick = veh_idle_q + veh_pick_q
    len_veh_idle_n_pick = len(veh_idle_n_pick)
    
    len_pass_noAssign = len(pass_no_assign_q)
    pass_noAssignPick_Q = pass_no_assign_q + pass_no_pick_q
    len_pass_noPickAssign = len(pass_noAssignPick_Q)
    
    pass_veh_assign = [[pass_noAssignPick_Q[n], Vehicle.Vehicle] for n in range(len_pass_noPickAssign) ]

    distM = [[0 for j in range(len_veh_idle_n_pick)] for i in range(len_pass_noPickAssign)]
    x = [[0 for j in range(len_veh_idle_n_pick)] for i in range(len_pass_noPickAssign)]
    # y = [[0 for j in range(len_veh_idle_n_pick)] for i in range(len_pass_noPickAssign)]
    prev_assign = [0 for i in range(len_pass_noPickAssign)]

    count_pass = -1
    for i_pass in pass_noAssignPick_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        trav_wait_penalty = cur_wait * Set.gamma
        for j_veh in veh_idle_n_pick:
            count_veh += 1

            if count_pass < len_pass_noAssign:
                if count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + j_veh.curb_time_remain * Set.veh_speed
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + Set.reassign_penalty \

            else:
                prev_assign[count_pass] = 1
                if j_veh.next_pickup == i_pass:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty
                elif count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + Set.reassign_penalty \
                                                   + j_veh.curb_time_remain * Set.veh_speed
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + 2*Set.reassign_penalty
    t1 = time.time()
    # Model
    models = gurobipy.Model("idlePick_minDist")
    models.setParam( 'OutputFlag', False )

    # Decision Variables
    for i in range(len_pass_noPickAssign):
        for j in range(len_veh_idle_n_pick):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    # constraints

    #Previously assigned passengers must be assigned a vehicle
    for ii in range(len_pass_noPickAssign):
        models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_veh_idle_n_pick)) - prev_assign[ii] >= 0)

    if (len_pass_noPickAssign <= len_veh_idle_n_pick):
        for ii in range(len_pass_noPickAssign):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_veh_idle_n_pick)) == 1)
        for jj in range(len_veh_idle_n_pick):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass_noPickAssign)) <= 1)

    else:
        for ii in range(len_pass_noPickAssign):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_veh_idle_n_pick)) <= 1)
        for jj in range(len_veh_idle_n_pick):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass_noPickAssign)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_pass in range(len_pass_noPickAssign):
            for n_veh in range(len_veh_idle_n_pick):
                if x[m_pass][n_veh].X == 1:
                    pass_veh_assign[m_pass] = [pass_noAssignPick_Q[m_pass], veh_idle_n_pick[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idlePick_minDist")
    # print("Vehicles= ", len_veh_idle_n_pick, "  Passengers= ", len_pass_noPickAssign, "  time=", time.time() - t1)
    return pass_veh_assign
#############################################################################################################


#############################################################################################################
def idlePickDrop_minDist(veh_idle_q, veh_pick_q, veh_drop_q, pass_no_assign_q, pass_no_pick_q, t):

    len_veh_idle = len(veh_idle_q)
    len_veh_drop = len(veh_drop_q)

    all_veh = veh_idle_q  + veh_drop_q + veh_pick_q
    tot_veh_length = len(all_veh)

    len_pass_noAssign = len(pass_no_assign_q)
    len_pass_noPick = len(pass_no_pick_q)
    pass_noAssignPick_Q = pass_no_assign_q + pass_no_pick_q
    len_pass_noPickAssign = len(pass_noAssignPick_Q)

    pass_veh_assign = [[pass_noAssignPick_Q[n], Vehicle.Vehicle] for n in range(len_pass_noPickAssign) ]

    distM = [[0 for j in range(tot_veh_length)] for i in range(len_pass_noPickAssign)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_pass_noPickAssign)]
    prev_assign = [0 for i in range(len_pass_noPickAssign)]

    count_pass = -1
    for i_pass in pass_noAssignPick_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        trav_wait_penalty = cur_wait * Set.gamma
        for j_veh in all_veh:
            count_veh += 1

            if count_pass < len_pass_noAssign:
                if count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + j_veh.curb_time_remain * Set.veh_speed
                elif count_veh < len_veh_idle + len_veh_drop:
                    distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + Set.dropoff_penalty \
                                                   + Set.curb_drop_time * Set.veh_speed
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + Set.reassign_penalty

            else:
                prev_assign[count_pass] = 1
                if j_veh.next_pickup == i_pass:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty
                elif count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + Set.reassign_penalty \
                                                   + j_veh.curb_time_remain * Set.veh_speed
                elif count_veh < len_veh_idle + len_veh_drop:
                    distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + Set.dropoff_penalty \
                                                   + Set.reassign_penalty \
                                                   + Set.curb_drop_time * Set.veh_speed
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                                   + 2*Set.reassign_penalty
    t1 = time.time()

    # Model
    models = gurobipy.Model("idlePickDrop_minDist")
    models.setParam( 'OutputFlag', False )

    # Decision Variables
    for i in range(len_pass_noPickAssign):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    # constraints

    # Previously assigned passengers must be assigned a vehicle
    for ii in range(len_pass_noPickAssign):
        models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) - prev_assign[ii] >= 0)

    if (len_pass_noPickAssign <= tot_veh_length):
        for ii in range(len_pass_noPickAssign):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) == 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass_noPickAssign)) <= 1)

    else:
        for ii in range(len_pass_noPickAssign):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) <= 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass_noPickAssign)) == 1)

    models.optimize()

    if models.status == gurobipy.GRB.Status.OPTIMAL:
        for m_pass in range(len_pass_noPickAssign):
            for n_veh in range(tot_veh_length):
                if x[m_pass][n_veh].X > 0 and x[m_pass][n_veh].X < 1:
                    sys.exit("Non Binary Variable- idlePickDrop_minDist")
                if x[m_pass][n_veh].X == 1:
                    # print (x[m_pass][n_veh].X )
                    pass_veh_assign[m_pass] = [pass_noAssignPick_Q[m_pass], all_veh[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idlePickDrop_minDist")

    # print("Vehicles= ", tot_veh_length, "  Passengers= ", len_pass_noPickAssign, "  time=", time.time()-t1)
    return pass_veh_assign
#############################################################################################################




