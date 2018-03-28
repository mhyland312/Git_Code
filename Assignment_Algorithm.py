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

    elif opt_method == "match_RS":
        answer = idleDrop_RS(veh_idle_q, veh_drop_q, pass_no_assign_q, t)
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
    temp_veh_idle_q = veh_idle_q[0:len(veh_idle_q)]

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
#Model
    models = gurobipy.Model("idleOnly_minDist")
    models.setParam( 'OutputFlag', False )

#Decision Variables
    for i in range(len_pass):
        for j in range(len_veh):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

#constraints

    #if the number of unassigned travelers is less than the number of idle vehicles
        #then make sure all the unassigned travelers are assigned a vehicle
    if (len_pass <= len_veh):
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_veh)) == 1)
        for jj in range(len_veh):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) <= 1)
    #else if the number of unassigned travelers is greater than the number of idle vehicles
        #then make sure all the idle vehicles are assigned to an unassigned traveler
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
    #print("Vehicles= ", len_veh, "  Passengers= ", len_pass, "  time=", time.time() - t1)
    return pass_veh_assign
#############################################################################################################


#############################################################################################################
def idleDrop_minDist(veh_idle_q, veh_drop_q, pass_no_assign_q, pass_no_pick_q, t):
    #remove vehicles from dropoff queue that already have another pickup after their dropoff
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
            #if vehicle state is enroute_dropoff - need to include dropoff distance as well
            if count_veh >= len_veh_idle:
                distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                               + Set.dropoff_penalty \
                                               + Set.curb_drop_time*Set.veh_speed
            else:
                distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty \
                                               + j_veh.curb_time_remain * Set.veh_speed

    t1 = time.time()
    #Model
    models = gurobipy.Model("idleDrop_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    #constraints
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
    #print("Vehicles= ", tot_veh_length, "  Passengers= ", len_pass, "  time=", time.time() - t1)
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
    #y = [[0 for j in range(len_veh_idle_n_pick)] for i in range(len_pass_noPickAssign)]
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
    #Model
    models = gurobipy.Model("idlePick_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass_noPickAssign):
        for j in range(len_veh_idle_n_pick):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    #constraints

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
    #print("Vehicles= ", len_veh_idle_n_pick, "  Passengers= ", len_pass_noPickAssign, "  time=", time.time() - t1)
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

    #Model
    models = gurobipy.Model("idlePickDrop_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass_noPickAssign):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    #constraints

    #Previously assigned passengers must be assigned a vehicle
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
                    #print (x[m_pass][n_veh].X )
                    pass_veh_assign[m_pass] = [pass_noAssignPick_Q[m_pass], all_veh[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idlePickDrop_minDist")

    #print("Vehicles= ", tot_veh_length, "  Passengers= ", len_pass_noPickAssign, "  time=", time.time()-t1)
    return pass_veh_assign
#############################################################################################################







#############################################################################################################
def idleDrop_RS(veh_idle_q, veh_drop_q, pass_no_assign_q, t):
    # there are some en_route drop-off AVs that already have a next pickup, remove them as possible shared-ride vehicles
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
    RS_okay = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]

    count_pass = -1
    for i_pass in pass_no_assign_q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        trav_wait_penalty = cur_wait * Set.gamma
        dist_idle = [100000000 for j_idle_veh in range(len_veh_idle)]
        for j_veh in veh_idle_n_drop_Q:
            count_veh += 1
            if count_veh < len_veh_idle:
                distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty
                dist_idle[count_veh] = Distance.dist_manhat(i_pass, j_veh)

            # if vehicle state is enroute_dropoff - need to add penalty for going out of way
            else:
                distM[count_pass][count_veh] = Distance.dist_manhat(i_pass,
                                                                    j_veh) + Set.pen_RS * Set.veh_speed - trav_wait_penalty
                min_dist_idle = min(dist_idle)

                # rideshare must reduce wait distance by 20% relative to nearest idle vehicle
                if (distM[count_pass][count_veh] < Set.min_improve_perc * min_dist_idle):
                    # rideshare must reduce wait distance by 7000 ft
                    if (distM[count_pass][count_veh] - min_dist_idle < Set.min_improve_ft):
                        # check to make sure the dropoff vehicle has enough capacity for a rideshare group
                        if (j_veh.current_load + i_pass.group_size < j_veh.capacity):
                            dist_RS_dropA = abs(j_veh.position_x - j_veh.current_dest_x) + abs(
                                j_veh.position_y - j_veh.current_dest_y)
                            dist_RS_pickB = abs(j_veh.position_x - i_pass.pickup_location_x) + abs(
                                j_veh.position_y - i_pass.pickup_location_y)
                            dist_pickB_dropA = abs(i_pass.pickup_location_x - j_veh.current_dest_x) + abs(
                                i_pass.pickup_location_y - j_veh.current_dest_y)
                            dist_pickB_dropB = abs(i_pass.pickup_location_x - i_pass.dropoff_location_x) + abs(
                                i_pass.pickup_location_y - i_pass.dropoff_location_y)
                            dist_dropA_dropB = abs(j_veh.current_dest_x - i_pass.dropoff_location_x) + abs(
                                j_veh.current_dest_y - i_pass.dropoff_location_y)
                            # check to make sure the rideshare pickup is not in the opposite direction of the original passenger's drop
                            if (dist_pickB_dropA < dist_RS_dropA and (
                                dist_RS_pickB + dist_pickB_dropA) < Set.max_deviate * dist_RS_dropA):
                                # if the original passenger's drop is closer to new passenger's pickup than new passenger's destination
                                if (dist_pickB_dropA < dist_pickB_dropB):
                                    # check to make sure the original passenger's drop is not in the opposite direction of the new passenger's drop
                                    # check to make sure that the original passengers drop doesn't increase new passenger's distance/time by more than X% compared with a direct ride
                                    if (dist_dropA_dropB < dist_pickB_dropB and (
                                        dist_pickB_dropA + dist_dropA_dropB) < Set.max_deviate * dist_pickB_dropB):
                                        RS_okay[count_pass][count_veh] = 1
                                    else:
                                        distM[count_pass][count_veh] = distM[count_pass][count_veh] + Set.inf
                                # if the new passenger's drop is closer to new passenger's pickup than original passenger's destination
                                else:
                                    # check to make sure the new passenger's drop is not in the opposite direction of the original passenger's drop
                                    # check to make sure that the new passengers drop doesn't increase original passenger's distance/time by more than 30%
                                    if (dist_dropA_dropB < dist_pickB_dropA and (
                                        dist_pickB_dropB + dist_dropA_dropB) < Set.max_deviate * dist_pickB_dropA):
                                        RS_okay[count_pass][count_veh] = 1
                                    else:
                                        distM[count_pass][count_veh] = distM[count_pass][count_veh] + Set.inf

    # Model
    models = gurobipy.Model("RS_minDist")
    models.setParam('OutputFlag', False)

    # Decision Variables
    for i in range(len_pass):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=distM[i][j], name='x_%s_%s' % (i, j))
    models.update()

    for iii in range(len_pass):
        for jjj in range(len_veh_idle, tot_veh_length):
            models.addConstr(x[iii][jjj] * (1 - RS_okay[iii][jjj]), gurobipy.GRB.EQUAL, 0)

    # constraints
    if (len_pass <= len_veh_idle):
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) == 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) <= 1)

    elif (len_pass <= tot_veh_length):
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) <= 1)
        for jj in range(len_veh_idle):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) == 1)
        for jj in range(len_veh_idle, tot_veh_length):
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
                    if n_veh >= len_veh_idle:
                        # print("Rideshare")
                        veh_idle_n_drop_Q[n_veh].next_drop.rideshare = 1
                        pass_no_assign_q[m_pass].rideshare = 1
                    break
    else:
        sys.exit("No Optimal Solution - idleDrop_RS")

    return pass_veh_assign


#############################################################################################################




########################### Old RS########################################################################################################
#############################################################################################################
def idleDrop_RS_old(veh_idle_q, veh_drop_q, pass_no_assign_q, t):
    len_pass = len(pass_no_assign_q)
    pass_veh_assign = [[pass_no_assign_q[n], Vehicle.Vehicle] for n in range(len_pass) ]
    dist = [-1 for n in range(len_pass)]

    answer_idle = []
    dist_idle = []
    idle = idleOnly_minDist(veh_idle_q, pass_no_assign_q,t)
    answer_idle.append(idle[0])
    dist_idle.append(idle[1])

    #if len(veh_idle_q) < 3 * len(pass_no_assign_q):
    answer_rideshare = []
    dist_rideshare = []
    rideshare = idleOnly_minDist(veh_drop_q, pass_no_assign_q, t)
    answer_rideshare.append(rideshare[0])
    dist_rideshare.append(rideshare[1])

    reassign = [] #the first check to see if a potential rideshare exists
    #compare the idle vehicle-passenger distance and the enroute vehicle-passenger
    for i_match in range(len_pass):

        person1 = pass_no_assign_q[i_match]
        try:
            veh_rideshare = answer_rideshare[0][i_match][1]

            dist_RS_dropA = abs(veh_rideshare.position_x - veh_rideshare.current_dest_x)+ abs(veh_rideshare.position_y - veh_rideshare.current_dest_y)
            dist_RS_pickB = abs(veh_rideshare.position_x - person1.pickup_location_x)+ abs(veh_rideshare.position_y - person1.pickup_location_y)
            dist_pickB_dropA = abs(person1.pickup_location_x - veh_rideshare.current_dest_x)+ abs(person1.pickup_location_y - veh_rideshare.current_dest_y)
            dist_pickB_dropB = abs(person1.pickup_location_x - person1.dropoff_location_x)+ abs(person1.pickup_location_y - person1.dropoff_location_y)
            dist_dropA_dropB = abs(veh_rideshare.current_dest_x - person1.dropoff_location_x)+ abs(veh_rideshare.current_dest_y - person1.dropoff_location_y)

            #if rideshare reduces wait distance by 20% and rideshare reduces wait distance by at least 7000/44ft/s  ft
            if ((dist_rideshare[0][i_match] > 0.8 * dist_idle[0][i_match]) or (dist_idle[0][i_match] - dist_rideshare[0][i_match] > 7000)):
                reassign.append(0)
            #check to make sure the dropoff vehicle has enough capacity for a rideshare group
            elif(veh_rideshare.capacity < veh_rideshare.current_load + person1.group_size):
                reassign.append(0)
            #check to make sure the rideshare pickup is not in the opposite direction of the original passenger's drop
            #check to make sure that the rideshare pickup doesn't increase original passenger's distance/time by more than 30%
            elif (dist_pickB_dropA > dist_RS_dropA or (dist_RS_pickB + dist_pickB_dropA) > Set.max_deviate*dist_RS_dropA):
                    reassign.append(0)
            #if the original passenger's drop is closer to new passenger's pickup than new passenger's destination
            elif(dist_pickB_dropA < dist_pickB_dropB ):
                #check to make sure the original passenger's drop is not in the opposite direction of the new passenger's drop
                #check to make sure that the original passengers drop doesn't increase new passenger's distance/time by more than 30% compared with a direct ride
                if (dist_dropA_dropB > dist_pickB_dropB or (dist_pickB_dropA + dist_dropA_dropB) > Set.max_deviate*dist_pickB_dropB):
                    reassign.append(0)
                else:
                    reassign.append(1)
                    #print("rideshare",person1.person_id, veh_rideshare.next_drop.person_id)
                    person1.rideshare = 1
                    veh_rideshare.next_drop.rideshare = 1
            #if the new passenger's drop is closer the new passengers pickup than the original passenger's drop
            elif (dist_pickB_dropB < dist_pickB_dropA):
                #check to make sure the new passenger's drop is not in the opposite direction of the original passenger's drop
                #check to make sure that the new passengers drop doesn't increase original passenger's distance/time by more than 30%
                if (dist_dropA_dropB > dist_pickB_dropA or (dist_pickB_dropB + dist_dropA_dropB) > Set.max_deviate*dist_pickB_dropA):
                    reassign.append(0)
                else:
                    reassign.append(1)
                    #print("rideshare", person1.person_id, veh_rideshare.next_drop.person_id, "2")
                    person1.rideshare = 1
                    veh_rideshare.next_drop.rideshare = 1

            else:
                reassign.append(1)

        except:
            reassign.append(0)

        pass_veh_assign[i_match][0] = person1
        if reassign[i_match] == 1:
            pass_veh_assign[i_match][1] = veh_rideshare
            dist[i_match] = dist_idle
        else:
            veh_idle = answer_idle[0][i_match][1]
            pass_veh_assign[i_match][1] = veh_idle
            dist[i_match] = dist_rideshare
    return [pass_veh_assign, dist]
    #else:
        #return idle
#############################################################################################################




#############################################################################################################
def idleDrop_RS_new(veh_idle_q, veh_pick_q, veh_drop_q, veh_RS_Q, pass_no_assign_q, pass_no_pick_q, t):

    new_veh_drop_q = []
    for a_veh in veh_drop_q:
        if a_veh.next_pickup.person_id < 0:
            new_veh_drop_q.append(a_veh)

    len_veh_idle = len(veh_idle_q)
    len_veh_drop = len(new_veh_drop_q)
    len_veh_pick = len(veh_pick_q)

    all_veh = veh_idle_q + new_veh_drop_q + veh_pick_q + veh_RS_Q
    tot_veh_length = len(all_veh)

    len_pass_noAssign = len(pass_no_assign_q)
    len_pass_noPick = len(pass_no_pick_q)
    pass_noAssignPick_Q = pass_no_assign_q + pass_no_pick_q
    len_pass_noPickAssign = len(pass_noAssignPick_Q)

    pass_veh_assign = [[pass_noAssignPick_Q[n], Vehicle.Vehicle] for n in range(len_pass_noPickAssign) ]

    distM = [[0 for j in range(tot_veh_length)] for i in range(len_pass_noPickAssign)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_pass_noPickAssign)]
    prev_assign = [0 for i in range(len_pass_noPickAssign)]
    RS_okay = [[0 for j in range(tot_veh_length)] for i in range(len_pass_noPickAssign)]

    count_pass = -1
    for i_pass in pass_noAssignPick_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        trav_wait_penalty = cur_wait * Set.gamma
        dist_idle = [Set.inf for qwe in range(len_veh_idle)]
        for j_veh in all_veh:
            count_veh += 1

            if count_veh < len_veh_idle:
                dist_idle[count_veh] = Distance.dist_manhat(i_pass, j_veh)


            #unassigned travelers
            if count_pass < len_pass_noAssign:
                if count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty
                elif count_veh < len_veh_idle + len_veh_drop:
                    distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - trav_wait_penalty + Set.dropoff_penalty
                elif count_veh < len_veh_idle + len_veh_drop + len_veh_pick:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty + Set.reassign_penalty  #+ j_veh.reassigned*100000
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty + Set.shared_ride_penalty

            #########Check for RS#################
                    # check to make sure the dropoff vehicle has enough capacity for a rideshare group
                    if (j_veh.current_load + i_pass.group_size < j_veh.capacity):

                        dist_RS_dropA = abs(j_veh.position_x - j_veh.current_dest_x) + abs(
                            j_veh.position_y - j_veh.current_dest_y)
                        dist_RS_pickB = abs(j_veh.position_x - i_pass.pickup_location_x) + abs(
                            j_veh.position_y - i_pass.pickup_location_y)
                        dist_pickB_dropA = abs(i_pass.pickup_location_x - j_veh.current_dest_x) + abs(
                            i_pass.pickup_location_y - j_veh.current_dest_y)
                        dist_pickB_dropB = abs(i_pass.pickup_location_x - i_pass.dropoff_location_x) + abs(
                            i_pass.pickup_location_y - i_pass.dropoff_location_y)
                        dist_dropA_dropB = abs(j_veh.current_dest_x - i_pass.dropoff_location_x) + abs(
                            j_veh.current_dest_y - i_pass.dropoff_location_y)

                        # check to make sure the rideshare pickup is not in the opposite direction of the original passenger's drop
                        if dist_pickB_dropA < dist_RS_dropA:

                            # do not increase inVeh traveler distance by more than X%
                            if dist_RS_pickB + dist_pickB_dropA < Set.max_deviate * dist_RS_dropA:

                                # if the original passenger's drop is closer to new passenger's pickup than new passenger's destination
                                if (dist_pickB_dropA < dist_pickB_dropB):

                                    # check to make sure the original passenger's drop is not in the opposite direction of the new passenger's drop
                                    if dist_dropA_dropB < dist_pickB_dropB:

                                        # check to make sure that the original passengers drop doesn't increase new passenger's distance/time by more than X% compared with a direct ride
                                        if dist_pickB_dropA + dist_dropA_dropB < Set.max_deviate * dist_pickB_dropB:
                                            RS_okay[count_pass][count_veh] = 1

                                # if the new passenger's drop is closer to new passenger's pickup than original passenger's destination
                                else:
                                    # check to make sure the new passenger's drop is not in the opposite direction of the original passenger's drop
                                    # check to make sure that the new passengers drop doesn't increase original passenger's distance/time by more than 30%
                                    if dist_dropA_dropB < dist_pickB_dropA:
                                        if dist_pickB_dropB + dist_dropA_dropB < Set.max_deviate * dist_pickB_dropA:
                                            RS_okay[count_pass][count_veh] = 1
                ####################

            #assigned, no-pickup travelers
            else:
                prev_assign[count_pass] = 1
                if j_veh.next_pickup == i_pass:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty
                elif count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty + Set.reassign_penalty
                elif count_veh < len_veh_idle + len_veh_drop:
                    distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - trav_wait_penalty + Set.dropoff_penalty + Set.reassign_penalty
                elif count_veh < len_veh_idle + len_veh_drop + len_veh_pick:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty + 2*Set.reassign_penalty #+ j_veh.reassigned*100000
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - trav_wait_penalty + Set.shared_ride_penalty




    # Model
    models = gurobipy.Model("RS_minDist")
    models.setParam('OutputFlag', False)

    # Decision Variables
    for i in range(len_pass_noPickAssign):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.CONTINUOUS, obj=distM[i][j], name='x_%s_%s' % (i, j))
    models.update()


    # constraints

    start_RS = len_veh_idle + len_veh_drop + len_veh_pick
    for iii in range(len_pass_noPickAssign):
        for jjj in range(start_RS, tot_veh_length):
            models.addConstr(x[iii][jjj] * (1 - RS_okay[iii][jjj]), gurobipy.GRB.EQUAL, 0)

    # constraints
    if (len_pass_noPickAssign <= len_veh_idle):
        for ii in range(len_pass_noPickAssign):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) == 1)
        for jj in range(tot_veh_length):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass_noPickAssign)) <= 1)

    elif (len_pass_noPickAssign <= tot_veh_length):
        for ii in range(len_pass_noPickAssign):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(tot_veh_length)) <= 1)
        for jj in range(len_veh_idle):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass_noPickAssign)) == 1)
        for jj in range(len_veh_idle, tot_veh_length):
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
                if x[m_pass][n_veh].X == 1:
                    pass_veh_assign[m_pass] = [pass_no_assign_q[m_pass], all_veh[n_veh]]
                    if n_veh >= len_veh_idle:
                        print("Rideshare")
                        all_veh[n_veh].next_drop.rideshare = 1
                        pass_no_assign_q[m_pass].rideshare = 1
                    break
    else:
        sys.exit("No Optimal Solution - idleDrop_RS")

    return pass_veh_assign
    #############################################################################################################