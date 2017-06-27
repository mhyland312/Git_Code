__author__ = 'Mike'

import Distance
import gurobipy
import Settings as Set
import Vehicle
import sys


#############################################################################################################
def assign_veh(veh_idle_Q, veh_pick_Q, veh_drop_Q, pass_noAssign_Q, pass_noPick_Q, opt_method, t):
    answer = "blank"
    if opt_method == "FCFS_longestIdle":
        answer = FCFS_longestIdle(veh_idle_Q, pass_noAssign_Q)
    elif opt_method == "FCFS_nearestIdle":
        answer = FCFS_nearestIdle(veh_idle_Q, pass_noAssign_Q)
    elif opt_method == "match_idleOnly":
        answer = idleOnly_minDist(veh_idle_Q, pass_noAssign_Q, t)
    elif opt_method == "match_RS":
        answer = idleDrop_RS(veh_idle_Q, veh_drop_Q, pass_noAssign_Q, t)
    #elif opt_method == "match_RS_old":
        #answer = idleDrop_RS_old(veh_idle_Q, veh_drop_Q, pass_noAssign_Q, t)[0]
    elif opt_method == "match_idleDrop":
        answer = idleDrop_minDist(veh_idle_Q, veh_drop_Q, pass_noAssign_Q, t)
    elif opt_method == "match_idlePick":
        answer = idlePick_minDist(veh_idle_Q, veh_pick_Q, pass_noAssign_Q, pass_noPick_Q, t)
    elif opt_method == "match_idlePickDrop":
        answer = idlePickDrop_minDist(veh_idle_Q, veh_pick_Q, veh_drop_Q, pass_noAssign_Q, pass_noPick_Q, t)
    else:
        print("Error: No_assignment_method")
    return answer
#############################################################################################################

#############################################################################################################
def FCFS_longestIdle(veh_idle_Q, pass_noAssign_Q):
    len_veh = len(veh_idle_Q)
    len_pass = len(pass_noAssign_Q)
    Pass_Veh_assign = [[pass_noAssign_Q[n], Vehicle.Vehicle] for n in range(len_pass) ]

    max_match = min(len_pass, len_veh)
    for i_match in range(max_match):
        Pass_Veh_assign[i_match] = [pass_noAssign_Q[i_match], veh_idle_Q[i_match]]

    return (Pass_Veh_assign)

#############################################################################################################


#############################################################################################################
def FCFS_nearestIdle(veh_idle_Q, pass_noAssign_Q):
    len_pass = len(pass_noAssign_Q)
    Pass_Veh_assign = [[pass_noAssign_Q[n], Vehicle.Vehicle] for n in range(len_pass) ]

    used_vehicles = []
    count_p = -1
    for i_person in pass_noAssign_Q:
        count_p += 1
        min_dist = 100000000000
        win_veh_index = -1
        veh_index = -1
        for j_veh in veh_idle_Q:
            veh_index += 1
            dist = Distance.dist_manhat(i_person, j_veh)
            if dist < min_dist and not (j_veh.vehicle_id in used_vehicles): #make sure that two persons aren't assigned to same vehicle
                win_veh_index = veh_index
                min_dist = dist
        if win_veh_index >= 0:
            Win_Vehicle = veh_idle_Q[win_veh_index]
            used_vehicles.append(Win_Vehicle.vehicle_id)
        else:
            Win_Vehicle = Vehicle.Vehicle

        Pass_Veh_assign[count_p] = [i_person, Win_Vehicle]

    return (Pass_Veh_assign)
#############################################################################################################


#############################################################################################################
def idleOnly_minDist(veh_idle_Q, pass_noAssign_Q, t):
    len_veh = len(veh_idle_Q)
    len_pass = len(pass_noAssign_Q)
    Pass_Veh_assign = [[pass_noAssign_Q[n], Vehicle.Vehicle] for n in range(len_pass)]

    distM = [[0 for j in range(len_veh)] for i in range(len_pass)]
    x = [[0 for j in range(len_veh)] for i in range(len_pass)]

    count_pass = -1
    for i_pass in pass_noAssign_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        for j_veh in veh_idle_Q:
            count_veh += 1
            distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait * 50.0

    #Model
    models = gurobipy.Model("idleOnly_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass):
        for j in range(len_veh):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.BINARY, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    #constraints
    if (len_pass <= len_veh):
        for ii in range(len_pass):
            models.addConstr(gurobipy.quicksum(x[ii][j] for j in range(len_veh)) == 1)
        for jj in range(len_veh):
            models.addConstr(gurobipy.quicksum(x[i][jj] for i in range(len_pass)) <= 1)
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
                    Pass_Veh_assign[m_pass] = [pass_noAssign_Q[m_pass], veh_idle_Q[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idleOnly_minDist")

    return (Pass_Veh_assign)
#############################################################################################################



#############################################################################################################
def idleDrop_RS(veh_idle_Q, veh_drop_Q, pass_noAssign_Q, t):
    new_veh_drop_queue = []
    for a_veh in veh_drop_Q:
        if a_veh.next_pickup.person_id < 0:
            new_veh_drop_queue.append(a_veh)    

    len_veh_idle = len(veh_idle_Q)
    veh_idle_n_drop_Q = veh_idle_Q + new_veh_drop_queue
    tot_veh_length = len(veh_idle_n_drop_Q)
    
    len_pass = len(pass_noAssign_Q)
    Pass_Veh_assign = [[pass_noAssign_Q[n], Vehicle.Vehicle] for n in range(len_pass) ]


    distM = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]
    RS_okay = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]

    count_pass = -1
    for i_pass in pass_noAssign_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        dist_idle = [100000000 for j_idle_veh in range(len_veh_idle)]
        for j_veh in veh_idle_n_drop_Q:
            count_veh += 1
            if count_veh < len_veh_idle:
                distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0
                dist_idle[count_veh] = Distance.dist_manhat(i_pass, j_veh)

            #if vehicle state is enroute_dropoff - need to add penalty for going out of way
            else:
                distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) + Set.pen_RS*Set.veh_speed - cur_wait*50.0
                min_dist_idle = min(dist_idle)

                #rideshare must reduce wait distance by 20% relative to nearest idle vehicle
                if (distM[count_pass][count_veh] < Set.min_improve_perc * min_dist_idle):
                    #rideshare must reduce wait distance by 7000 ft
                    if(distM[count_pass][count_veh] -  min_dist_idle < Set.min_improve_ft):
                        #check to make sure the dropoff vehicle has enough capacity for a rideshare group
                        if (j_veh.current_load + i_pass.group_size < j_veh.capacity):
                            dist_RS_dropA = abs(j_veh.position_x - j_veh.current_dest_x)+ abs(j_veh.position_y - j_veh.current_dest_y)
                            dist_RS_pickB = abs(j_veh.position_x - i_pass.pickup_location_x)+ abs(j_veh.position_y - i_pass.pickup_location_y)
                            dist_pickB_dropA = abs(i_pass.pickup_location_x - j_veh.current_dest_x)+ abs(i_pass.pickup_location_y - j_veh.current_dest_y)
                            dist_pickB_dropB = abs(i_pass.pickup_location_x - i_pass.dropoff_location_x)+ abs(i_pass.pickup_location_y - i_pass.dropoff_location_y)
                            dist_dropA_dropB = abs(j_veh.current_dest_x - i_pass.dropoff_location_x)+ abs(j_veh.current_dest_y - i_pass.dropoff_location_y)
                            #check to make sure the rideshare pickup is not in the opposite direction of the original passenger's drop
                            if (dist_pickB_dropA < dist_RS_dropA and (dist_RS_pickB + dist_pickB_dropA) < Set.max_deviate*dist_RS_dropA):
                                #if the original passenger's drop is closer to new passenger's pickup than new passenger's destination
                                if(dist_pickB_dropA < dist_pickB_dropB ):
                                    #check to make sure the original passenger's drop is not in the opposite direction of the new passenger's drop
                                    #check to make sure that the original passengers drop doesn't increase new passenger's distance/time by more than X% compared with a direct ride
                                    if (dist_dropA_dropB < dist_pickB_dropB and (dist_pickB_dropA + dist_dropA_dropB) < Set.max_deviate*dist_pickB_dropB):
                                        RS_okay[count_pass][count_veh] = 1
                                    else:
                                        distM[count_pass][count_veh] = distM[count_pass][count_veh] + Set.inf
                                #if the new passenger's drop is closer to new passenger's pickup than original passenger's destination
                                else:
                                    #check to make sure the new passenger's drop is not in the opposite direction of the original passenger's drop
                                    #check to make sure that the new passengers drop doesn't increase original passenger's distance/time by more than 30%
                                    if (dist_dropA_dropB < dist_pickB_dropA and (dist_pickB_dropB + dist_dropA_dropB) < Set.max_deviate*dist_pickB_dropA):
                                        RS_okay[count_pass][count_veh] = 1
                                    else:
                                        distM[count_pass][count_veh] = distM[count_pass][count_veh] + Set.inf

    #Model
    models = gurobipy.Model("RS_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.BINARY, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
    models.update()

    for iii in range(len_pass):
        for jjj in range(len_veh_idle, tot_veh_length):
            models.addConstr(x[iii][jjj] * (1-RS_okay[iii][jjj]), gurobipy.GRB.EQUAL, 0)

    #constraints
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
                    Pass_Veh_assign[m_pass] = [pass_noAssign_Q[m_pass], veh_idle_n_drop_Q[n_veh]]
                    if n_veh >= len_veh_idle:
                        #print("Rideshare")
                        veh_idle_n_drop_Q[n_veh].next_drop.rideshare = 1
                        pass_noAssign_Q[m_pass].rideshare = 1
                    break
    else:
        sys.exit("No Optimal Solution - idleDrop_RS")


    return (Pass_Veh_assign)
#############################################################################################################


#############################################################################################################
def idleDrop_minDist(veh_idle_Q, veh_drop_Q, pass_noAssign_Q, t):
    #remove vehicles from dropoff queue that already have another pickup after their dropoff
    new_veh_drop_queue = []
    for a_veh in veh_drop_Q:
        if a_veh.next_pickup.person_id < 0:
            new_veh_drop_queue.append(a_veh)

    len_veh_idle = len(veh_idle_Q)
    veh_idle_n_drop_Q = veh_idle_Q + new_veh_drop_queue
    tot_veh_length = len(veh_idle_n_drop_Q)
    
    len_pass = len(pass_noAssign_Q)
    Pass_Veh_assign = [[pass_noAssign_Q[n], Vehicle.Vehicle] for n in range(len_pass) ]

    distM = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_pass)]

    count_pass = -1
    for i_pass in pass_noAssign_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        for j_veh in veh_idle_n_drop_Q:
            count_veh += 1
            #if vehicle state is enroute_dropoff - need to include dropoff distance as well
            if count_veh >= len_veh_idle:
                distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - cur_wait*50.0 + Set.pen_drop_time*Set.veh_speed
            else:
                distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0
            
    #Model
    models = gurobipy.Model("idleDrop_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.BINARY, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
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
                    Pass_Veh_assign[m_pass] = [pass_noAssign_Q[m_pass], veh_idle_n_drop_Q[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idleDrop_minDist")

    return (Pass_Veh_assign)
#############################################################################################################


#############################################################################################################
def idlePick_minDist(veh_idle_Q, veh_pick_Q, pass_noAssign_Q, pass_noPick_Q, t):

    len_veh_idle = len(veh_idle_Q)
    veh_idle_n_pick = veh_idle_Q + veh_pick_Q
    len_veh_idle_n_pick = len(veh_idle_n_pick)
    
    len_pass_noAssign = len(pass_noAssign_Q)
    pass_noAssignPick_Q = pass_noAssign_Q + pass_noPick_Q
    len_pass_noPickAssign = len(pass_noAssignPick_Q)
    
    Pass_Veh_assign = [[pass_noAssignPick_Q[n], Vehicle.Vehicle] for n in range(len_pass_noPickAssign) ]
    
    distM = [[0 for j in range(len_veh_idle_n_pick)] for i in range(len_pass_noPickAssign)]
    x = [[0 for j in range(len_veh_idle_n_pick)] for i in range(len_pass_noPickAssign)]
    prev_assign = [0 for i in range(len_pass_noPickAssign)]

    count_pass = -1
    for i_pass in pass_noAssignPick_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        for j_veh in veh_idle_n_pick:
            count_veh += 1

            if count_pass < len_pass_noAssign:
                if count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0 + Set.veh_speed*20 + j_veh.reassigned*100000

            else:
                prev_assign[count_pass] = 1
                if j_veh.next_pickup == i_pass:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0
                elif count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0 + Set.veh_speed*Set.pen_reassign + i_pass.reassigned*100000
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0 + 2*Set.veh_speed*Set.pen_reassign + j_veh.reassigned*100000 + i_pass.reassigned*100000

    #Model
    models = gurobipy.Model("idlePick_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass_noPickAssign):
        for j in range(len_veh_idle_n_pick):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.BINARY, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
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
                    Pass_Veh_assign[m_pass] = [pass_noAssignPick_Q[m_pass], veh_idle_n_pick[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idlePick_minDist")
    return (Pass_Veh_assign)
#############################################################################################################


#############################################################################################################
def idlePickDrop_minDist(veh_idle_Q, veh_pick_Q, veh_drop_Q, pass_noAssign_Q, pass_noPick_Q, t):

    #new_veh_drop_Q = []
    #for a_veh in veh_drop_Q:
    #    if a_veh.next_pickup.person_id < 0:
    #        new_veh_drop_Q.append(a_veh)

    new_veh_drop_Q = []
    for a_veh in veh_drop_Q:
        new_veh_drop_Q.append(a_veh)

    len_veh_idle = len(veh_idle_Q)
    len_veh_drop = len(veh_drop_Q)

    all_veh = veh_idle_Q  + veh_drop_Q + veh_pick_Q
    tot_veh_length = len(all_veh)

    len_pass_noAssign = len(pass_noAssign_Q)
    len_pass_noPick = len(pass_noPick_Q)
    pass_noAssignPick_Q = pass_noAssign_Q + pass_noPick_Q
    len_pass_noPickAssign = len(pass_noAssignPick_Q)

    Pass_Veh_assign = [[pass_noAssignPick_Q[n], Vehicle.Vehicle] for n in range(len_pass_noPickAssign) ]

    distM = [[0 for j in range(tot_veh_length)] for i in range(len_pass_noPickAssign)]
    x = [[0 for j in range(tot_veh_length)] for i in range(len_pass_noPickAssign)]
    prev_assign = [0 for i in range(len_pass_noPickAssign)]


    count_pass = -1
    for i_pass in pass_noAssignPick_Q:
        count_pass += 1
        count_veh = -1
        cur_wait = t - i_pass.request_time
        for j_veh in all_veh:
            count_veh += 1

            if count_pass < len_pass_noAssign:
                if count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0
                elif count_veh < len_veh_idle + len_veh_drop:
                    distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - cur_wait*50.0 + Set.pen_drop_time*Set.veh_speed
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0 + Set.veh_speed*Set.pen_reassign + j_veh.reassigned*100000

            else:
                prev_assign[count_pass] = 1
                if j_veh.next_pickup == i_pass:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0
                elif count_veh < len_veh_idle:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0 + Set.veh_speed*Set.pen_reassign + i_pass.reassigned*100000
                elif count_veh < len_veh_idle + len_veh_drop:
                    distM[count_pass][count_veh] = Distance.dyn_dist_manhat(i_pass, j_veh) - cur_wait*50.0 + Set.pen_drop_time*Set.veh_speed + Set.veh_speed*Set.pen_reassign + i_pass.reassigned*100000
                else:
                    distM[count_pass][count_veh] = Distance.dist_manhat(i_pass, j_veh) - cur_wait*50.0 + 2*Set.veh_speed*Set.pen_reassign  + j_veh.reassigned*100000 + i_pass.reassigned*100000



    #Model
    models = gurobipy.Model("idlePickDrop_minDist")
    models.setParam( 'OutputFlag', False )

    #Decision Variables
    for i in range(len_pass_noPickAssign):
        for j in range(tot_veh_length):
            x[i][j] = models.addVar(vtype=gurobipy.GRB.BINARY, obj = distM[i][j], name = 'x_%s_%s' % (i,j))
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
                if x[m_pass][n_veh].X == 1:
                    Pass_Veh_assign[m_pass] = [pass_noAssignPick_Q[m_pass], all_veh[n_veh]]
                    break
    else:
        sys.exit("No Optimal Solution - idlePickDrop_minDist")
    return (Pass_Veh_assign)
#############################################################################################################





########################### Old RS##########################################################################
#############################################################################################################
def idleDrop_RS_old(veh_idle_Q, veh_drop_Q, pass_noAssign_Q, t):
    len_pass = len(pass_noAssign_Q)
    Pass_Veh_assign = [[pass_noAssign_Q[n], Vehicle.Vehicle] for n in range(len_pass) ]
    dist = [-1 for n in range(len_pass)]

    answer_idle = []
    dist_idle = []
    idle = idleOnly_minDist(veh_idle_Q, pass_noAssign_Q,t)
    answer_idle.append(idle[0])
    dist_idle.append(idle[1])

    #if len(veh_idle_Q) < 3 * len(pass_noAssign_Q):
    answer_rideshare = []
    dist_rideshare = []
    rideshare = idleOnly_minDist(veh_drop_Q, pass_noAssign_Q, t)
    answer_rideshare.append(rideshare[0])
    dist_rideshare.append(rideshare[1])

    reassign = [] #the first check to see if a potential rideshare exists
    #compare the idle vehicle-passenger distance and the enroute vehicle-passenger
    for i_match in range(len_pass):

        person1 = pass_noAssign_Q[i_match]
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

        Pass_Veh_assign[i_match][0] = person1
        if reassign[i_match] == 1:
            Pass_Veh_assign[i_match][1] = veh_rideshare
            dist[i_match] = dist_idle
        else:
            veh_idle = answer_idle[0][i_match][1]
            Pass_Veh_assign[i_match][1] = veh_idle
            dist[i_match] = dist_rideshare
    return [Pass_Veh_assign, dist]
    #else:
        #return idle
#############################################################################################################