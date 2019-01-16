# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:35:08 2018

@author: Kuan
"""
import math
import copy
import datetime

##%%
#import pyodbc 
#import pandas as pd
##import main_fun_v2
#server = 'DESKTOP-C7FFVPQ' 
#database = 'CarSharing_VRP' 
#username = 'jameschu' 
#password = 'jameschu' 
#cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
#cursor = cnxn.cursor()
#
##print 
#print "---sql_resource---"
#
#cursor.execute('SELECT * from VRP_CAR_USEABLE')
#colList = []
#for colInfo in cursor.description:
#    colList.append(colInfo[0])
#rowList = []
#while True:
#    try:
#        row = cursor.fetchone()
#        if row:
#            rowList.append(list(row))
#        else:
#            break
#    except:   
#        continue;
#sql_resource = pd.DataFrame(rowList)
#sql_resource.columns = colList 
#
#
#print (sql_resource)
##%%
#print
#print ("---sql_cost---")
#print
#cursor.execute('SELECT * from VRP_TRAVEL_MATRIX_DATA')
#colList = []
#for colInfo in cursor.description:
#    colList.append(colInfo[0])
#rowList = []
#while True:
#    try:
#        row = cursor.fetchone()
#        if row:
#            rowList.append(list(row))
#        else:
#            break
#    except:   
#        continue;
#sql_cost = pd.DataFrame(rowList)
#sql_cost.columns = colList 
##print (sql_cost)
#
##print
##print ("---sql_request---")
##print
#cursor.execute('SELECT * from VRP_PRE_ORDER')
#colList = []
#for colInfo in cursor.description:
#    colList.append(colInfo[0])
#rowList = []
#while True:
#    try:
#        row = cursor.fetchone()
#        if row:
#            rowList.append(list(row))
#        else:
#            break
#    except:   
#        continue;
#sql_request = pd.DataFrame(rowList)
##sql_request.columns = colList 
#print (sql_request)
#request,cost,resource = sql_request,sql_cost,sql_resource
#%% All information 
def main_fun(request,cost,resource): 
    request_info = {}
    village_key = []
    Day_request_info = {}
    for i in range(request.shape[0]):
        temp_one = []
        for j in range(request.shape[1]):
            temp_value = request.loc[[i]].values[0][j]
            if j == 0 :
                temp_value_to_str =  str(temp_value[0:])
            elif j == 3:
                SENDORDER = temp_value
                continue
            elif j == 1 or j == 4 or j == 5 or j == 6 :
                temp_value_to_str = temp_value
            elif j == 7 :
                temp_value_to_str = int(temp_value)
            elif j == 8 or j == 9 or j == 10 or j == 11 :
    #                print temp_value,type(temp_value)
    #            print datetime.datetime.strptime(str(temp_value),"%Y-%m-%d:%H:%M")
                temp_value_to_str =  str(temp_value)
    #            temp_value_to_str = temp_value
    #            print temp_value_to_str[0],temp_value_to_str[10],temp_value_to_str[11],temp_value_to_str[12],temp_value_to_str[13],temp_value_to_str[14],temp_value_to_str[15]
                temp_value_to_str = int(temp_value_to_str[11])*10*60+int(temp_value_to_str[12])*60+int(temp_value_to_str[14])*10+int(temp_value_to_str[15])
            elif j == 2:
    #                print "---NOT YET---",type(temp_value), i
                continue
    
            temp_one.append(temp_value_to_str)
    #        print SENDORDER
    #    SENDORDER_date = SENDORDER[0:8]
        SENDORDER_date = "20180000"
        SENDORDER_date = str(SENDORDER_date[:4])+"/"+str(SENDORDER_date[4:6])+"/"+str(SENDORDER_date[6:])
    #    SENDORDER_ID = str(SENDORDER[8:])
        SENDORDER_ID = str(SENDORDER)
    
        for j in SENDORDER_ID:
            if int(j) !=0:
                SENDORDER_ID = int(SENDORDER_ID[SENDORDER_ID.index(j):])
                break
    #        print temp_one
        request_info[SENDORDER_ID] = [SENDORDER_date]+temp_one[0:2]+[SENDORDER_ID]+temp_one[2:10]
    #        print request_info[SENDORDER_ID]
        request_info_now = request_info[SENDORDER_ID]
        if request_info_now[2] not in village_key:
            village_key.append(request_info_now[2])
            Day_request_info[request_info_now[2]] = {}
        if request_info_now[0] not in Day_request_info[request_info_now[2]].keys():
            Day_request_info[request_info_now[2]][request_info_now[0]] = {}
            Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
        else:
            if request_info_now[1] not in Day_request_info[request_info_now[2]][request_info_now[0]].keys():
                Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]] = []
                Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
            else:
                Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]].append(request_info_now[3])
    unroute_request_info = request_info.keys()
    #%% 
    cost_info = {}
    temp_cost_list = []
    
    for i in range(cost.shape[0]):
        temp_cost = []
        for j in range(cost.shape[1]):
    
            temp_value = cost.loc[[i]].values[0][j]
            if j == 4:
                temp_value = int(temp_value)
            temp_cost.append(temp_value)
        cost_info[temp_cost[2],temp_cost[3]] = temp_cost[4]
        cost_info[temp_cost[2],temp_cost[2]] = 0
        temp_cost_list.append(temp_cost)
    #%% 
    resource_info = {}
    unuse_resource_info = {}
    useed_resource_info = {}
    
    for i in range(resource.shape[0]):
        temp_resource = []
        temp_resource.append(i+1)
        for j in range(resource.shape[1]):
            temp_value = resource.loc[[i]].values[0][j]
            if j == 6 or j == 7:
                temp_value = temp_value.strftime("%H:%M")
                temp_value = int(temp_value[0:temp_value.find(':')])*60+int(temp_value[temp_value.find(':')+1:])
            elif j == 2:
                temp_value = temp_value.strftime('%Y/%m/%d')
            elif j == 8:
                temp_value = int(temp_value) 
            temp_resource.append(temp_value)
        temp_carnumber = temp_resource[4]
        temp_village = temp_resource[3]
        temp_date = temp_resource[0]
        if temp_carnumber not in unuse_resource_info.keys():
            unuse_resource_info[temp_carnumber] = {}
            useed_resource_info[temp_carnumber] = {}
        if  temp_village not in unuse_resource_info[temp_carnumber].keys():
            unuse_resource_info[temp_carnumber][temp_village] = [temp_date]
            useed_resource_info[temp_carnumber][temp_village] = {}
        else:
            unuse_resource_info[temp_carnumber][temp_village].append(temp_date)
        resource_info[temp_date] = temp_resource
    t= copy.copy(cost_info)
    new_tw = 10
    Day_order = {}
    for i in unroute_request_info :
        Pp = request_info[i][5]
        Dp = request_info[i][6]
        EPT = request_info[i][10]-2*t[Pp,Dp]+new_tw/2
        EDT = request_info[i][11]-t[Pp,Dp]-new_tw/2
        LPT = request_info[i][10]+new_tw/2
        LDt = request_info[i][11]-new_tw/2
        n_C = request_info[i][7]
        Day_order[i] = [i]+[Pp,EPT,EDT,n_C,Dp,LPT,LDt]
        Day_order[-i] = [i]+[Dp,LPT,LDt,n_C]
    #%%
    Large_cost = 99999
    unservable_requests = {}
    #%%
    def route_seed_initialer2(uroute_list,village,Day):
    #    print "uroute_list,village,Day",uroute_list,village,Day
        now_uroute_list = []
        for i in uroute_list:
            now_uroute_list.append(Day_order[i])
        sort_now_uroute_list = sorted(now_uroute_list, key = lambda x : (x[2]))
        sort_uroute_list = []
        for i in sort_now_uroute_list:
            sort_uroute_list.append(i[0])
        seed_list = copy.copy(sort_uroute_list)
        new_uroute_list = []
        for i in range(len(sort_uroute_list)-1):
            req_i = sort_uroute_list[i]
            req_i_1 = sort_uroute_list[i+1]
            LDTk = Day_order[req_i][7]
            TTDkPk_1 = t[Day_order[req_i][5],Day_order[req_i_1][1]]
            EPTk_1 = Day_order[req_i_1][2]
            if LDTk+TTDkPk_1<=EPTk_1:
                seed_list.remove(req_i_1)
                new_uroute_list.append(req_i_1)
    #    print "seed_list",seed_list
        for i in unuse_resource_info[village][Day]:
            unservable_time = 0
            for j in seed_list: 
                current_routeA = [j,-j]
                if check_feasible_route(current_routeA,i) == 0:
    #                print " It is feasible"
                    useed_resource_info[village][Day][i] = [j,-j]
                    seed_list.remove(j)
                    break                  
                else:
                    unservable_time += 1
        for i in useed_resource_info[village][Day].keys():
            if i in unuse_resource_info[village][Day]:
                unuse_resource_info[village][Day].remove(i)
        return new_uroute_list+seed_list
    #%% Check feasibility
    def check_feasible_route(feasible_route,car_number):
        debug_time = Day_order[feasible_route[0]][2]
        starttime = resource_info[car_number][-7]
        endtime = resource_info[car_number][-6]
        debug_route_cap = resource_info[car_number][-5]
        debug1 = 0
        debug2 = 0    
        debug_route_time = []
        debug_real_time = []
        ######################################################
        if debug_time<starttime:
            debug2 += 10
        debug3 = 0 
        debug4 = 0    
        for x in feasible_route:
            if x > 0 :
                debug3 += Day_order[x][4] 
            elif x <0:
                debug3 -= Day_order[x][4]
            if debug3 > debug_route_cap:
                debug4 = 100
                break
    
        if debug4 == 0:
            for i in range(len(feasible_route)):
                pre_node = Day_order[feasible_route[i-1]][1]            
                now_node = Day_order[feasible_route[i]][1]
    
                e_time = Day_order[feasible_route[i]][2]
                l_time = Day_order[feasible_route[i]][3]
    
                if i == 0:
                    debug_route_time.append(debug_time)
                    debug_real_time.append(debug_time)
                elif i == len(feasible_route)-1:    
                    debug_time = debug_time+t[pre_node,now_node]
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                elif i > 0:
                    debug_time = max([debug_time+t[pre_node,now_node],e_time])
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                    debug_time += 10
            for i,j in zip(debug_route_time,debug_real_time):
                if  i > j:
                    debug1 = 1
            if debug_time > endtime:
                debug2 = 10
    
        debug5 = 0
        debug_signal = debug1 + debug2 + debug4 + debug5
    
        return debug_signal
    
    #%% regret_insert
    def regret_insert(unroute_list,village,Day):
    #    print unroute_list
        while len(unroute_list) > 0:
            current_list = useed_resource_info[village][Day].values()
            car_keys = useed_resource_info[village][Day].keys()        
            temp_route = copy.copy(current_list)
    #        print "temp_route:",temp_route
            c2_value = []
            c2_route = []
            c2_place = []
            c2_customer = []
            for customer in unroute_list:
                min_c1_route = []
                min_c1_value = []
                min_c1_place = []
                customer_p = customer
                customer_d = -customer_p
                for o_route in temp_route: 
                    car_number = car_keys[current_list.index(o_route)]
                    o_route_tt_dist = 0
                    for test_c in range(len(o_route)-1):
                        o_route_tt_dist += t[Day_order[o_route[test_c]][1],Day_order[o_route[test_c+1]][1]]                      
                    c1_value = []
                    c1_place = []
                    for p_place in range(len(o_route)+1):         
                        test_p_route =  copy.copy(o_route)
                        test_p_route.insert(p_place,customer_p)
                        feasibility1 = check_feasible_route(test_p_route,car_number)
                        if feasibility1 == 0:
                            for d_place in range(p_place+1,len(test_p_route)+1):
                                #print d_place,"----"
                                test_d_route = copy.copy(test_p_route)
                                test_d_route.insert(d_place,customer_d)
                                feasibility2 = check_feasible_route(test_d_route,car_number)
                                if feasibility2 == 0:###############
                                    ##################################################################
                                    tt_dist = 0
                                    for test_c in range(len(test_d_route)-1):
                                        tt_dist += t[Day_order[test_d_route[test_c]][1],Day_order[test_d_route[test_c+1]][1]]
                                    c1 = tt_dist-o_route_tt_dist
                                    ##################################################################
                                    c1_value.append(c1)
                                    c1_place.append([p_place,d_place])
                                
                    min_c1_route.append(o_route)       
                    if len(c1_value) > 0:
                        min_value = min(c1_value)
                        min_place = c1_place[c1_value.index(min_value)]                           
                        min_c1_value.append(min_value)
                        min_c1_place.append(min_place)
                    else:                
                        min_c1_value.append(Large_cost)
                        min_c1_place.append([-Large_cost,-Large_cost])     
    #            print "min_c1_value",min_c1_value
                min_min_c1_value = min(min_c1_value)
                min_c1_index = min_c1_value.index(min_min_c1_value)
                min_min_c1_place = min_c1_place[min_c1_index]
                min_min_c1_route = min_c1_route[min_c1_index]
                c2_customer.append([customer,-customer])
                c2 = 0
                if min_c1_value.count(Large_cost) != len(min_c1_value):
                    
                    for mmc in range(len(min_c1_value)):
                        if min_c1_route[mmc] != min_min_c1_route:
                            c2 += min_c1_value[mmc] - min_min_c1_value
                c2_value.append(c2)
                c2_route.append(min_min_c1_route)
                c2_place.append(min_min_c1_place)  
            if c2_value.count(0) != len(c2_value):
                max_c2_value = max(c2_value)
                max_c2_index = c2_value.index(max_c2_value)
                max_c2_route = c2_route[max_c2_index]
                max_c2_place = c2_place[max_c2_index]
                max_c2_customer = c2_customer[max_c2_index]
                max_c2_index = current_list.index(max_c2_route)        
                for insert_p,insert_c in zip(max_c2_place,max_c2_customer):
                    max_c2_route.insert(insert_p,insert_c)
                current_list[max_c2_index] = max_c2_route
                unroute_list.remove(max_c2_customer[0])         
            else:
                unservable_requests[Day] = unroute_list
                break
        return current_list
    
    #%% time window reduce
    def tw_reducer(feasible_route,car_number):  
        debug_time = Day_order[feasible_route[0]][2]
        endtime = resource_info[car_number][-2]
        debug_route_time = []
        debug_real_time = []
        for i in range(len(feasible_route)):          
            pre_node = Day_order[feasible_route[i-1]][1]            
            now_node = Day_order[feasible_route[i]][1]
            e_time = Day_order[feasible_route[i]][2]
            l_time = Day_order[feasible_route[i]][3]
            if i == 0:
                debug_route_time.append(debug_time)
                debug_real_time.append(debug_time)
            elif i == len(feasible_route)-1:
                debug_time = debug_time+t[pre_node,now_node]
                debug_route_time.append(debug_time)
                debug_real_time.append(endtime)
            elif i > 0:
                debug_time = max([debug_time+t[pre_node,now_node],e_time])
                debug_route_time.append(debug_time)
                debug_real_time.append(l_time)    
        for i,j in zip(feasible_route,debug_route_time):
            if i != 0 and Day_order[i][3]-Day_order[i][2] > new_tw:
                if i > 0:
        
                    Day_order[i][2] = math.floor(j - new_tw/2)
                    Day_order[i][3] = math.floor(j + new_tw/2)
                elif i < 0:
        
                    Day_order[-i][6] = math.floor(j - new_tw/2)
                    Day_order[-i][7] = math.floor(j + new_tw/2)
                    Day_order[i][2] = math.floor(j - new_tw/2)
                    Day_order[i][3] = math.floor(j + new_tw/2)
    #%%
    def tt_cost(feasible_route):
        o_route_tt_dist = 0
        for test_c in range(len(feasible_route)-1):
            o_route_tt_dist += t[Day_order[feasible_route[test_c]][1],Day_order[feasible_route[test_c+1]][1]]  
        
        return o_route_tt_dist
    #print tt_cost([10118, -10118, 10129, -10129, 10122, -10122])
    Day_request = copy.copy(Day_request_info)
    #%% Real Day program
    reserve_Plan = {}
    for village in village_key:
        Day_keys = sorted(Day_request[village].keys())
        reserve_Plan[village] = {}
        for day in Day_keys:
            reserve_Plan[village][day] = {}
            reser_Day_keys = sorted(Day_request[village][day].keys())
            for reser_Day in reser_Day_keys[:1]:
    #        for reser_Day in reser_Day_keys:
                unroute_Day_requests = copy.copy(Day_request[village][day][reser_Day])
                reserve_Plan_key = reserve_Plan[village][day].keys()
                if reser_Day not in reserve_Plan_key:
                    unroute_Day_requests = route_seed_initialer2(unroute_Day_requests,village,reser_Day)
                    final_route = regret_insert(unroute_Day_requests,village,reser_Day)
                    reserve_Plan[village][day][reser_Day] = final_route
                else:
                    final_route = regret_insert(unroute_Day_requests,village,reser_Day)
                    reserve_Plan[village][day][reser_Day] = final_route
    #            for i in final_route:
    #                print i,"-"
    #            print useed_resource_info[village][reser_Day]
    #            plan_cost = 0
    #            for i in useed_resource_info[village][reser_Day].values():
    #                print i
    #                plan_cost += tt_cost(i)
    #            print plan_cost
    #            
    #            ###Trip insertion
    #            o_useed_resource = copy.deepcopy(useed_resource_info[village][reser_Day])
    #            print "before",o_useed_resource
    #            for i in o_useed_resource:
    #                print o_useed_resource[i]
    #                cana_trip = []
    #                for j in  o_useed_resource[i]:
    #                    if j >0:
    #                        cana_trip.append(j)
    #                print cana_trip
    #                other_route = o_useed_resource.keys()
    #                other_route.remove(i)
    #                print "other_route",other_route
    #                
    #                for k in cana_trip:
    #                    print "k",k
    #                    now_plan = copy.deepcopy(o_useed_resource)
    #                    now_plan[i].remove(k)
    #                    now_plan[i].remove(-k)
    #                    print "now_plan",now_plan
    #                    
    #                    for l in other_route: 
    #                        for m in range(len(now_plan[l])+1):
    #                            for n in range(m+1,len(now_plan[l])+2):
    #                                insert_plan = copy.deepcopy(now_plan)
    #                                insert_plan[l].insert(m,k)
    #                                insert_plan[l].insert(n,-k)
    #                                temp_tt = 0
    #                                for o in insert_plan.values():
    #                                    temp_tt += tt_cost(o)
    #                                print "m",m,"n",n,insert_plan[l],check_feasible_route(insert_plan[l],l),l,temp_tt
    #            print "after",o_useed_resource       
        #        ##########reduce the window###########
                for i in useed_resource_info: ####
                    for j in  sorted(useed_resource_info[i]):
                        for k in useed_resource_info[i][j]:
                            tw_reducer(useed_resource_info[i][j][k],k)
    #%%
    result = []
    for i in useed_resource_info.keys():   
        for  j in sorted(useed_resource_info[i].keys()):
            for k in useed_resource_info[i][j]:
                temp_req_list = []
                
                for m in range(len(useed_resource_info[i][j][k])):
                    if useed_resource_info[i][j][k][m] > 0:
                        temp_req_list.append(useed_resource_info[i][j][k][m])
    #            print temp_req_list
                for l in range(len(temp_req_list)):
                    sin_req = temp_req_list[l]
    #                print sin_req,l
                    if sin_req > 0:
                        EPT = str(int(Day_order[sin_req][2]//60))+":"+str(int(Day_order[sin_req][2]%60))
                        EDT = str(int(Day_order[sin_req][3]//60))+":"+str(int(Day_order[sin_req][3]%60))
                        LPT = str(int(Day_order[sin_req][6]//60))+":"+str(int(Day_order[sin_req][6]%60))
                        LDt = str(int(Day_order[sin_req][7]//60))+":"+str(int(Day_order[sin_req][7]%60))
                        TAKE_TIME = str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2//60))+":"+str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2%60))
                        AVR_TIME = str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2//60))+":"+str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2%60))
                        TAKE_DATE = j[0:4]+"-"+j[5:7]+"-"+j[8:]
                        TAKE_DATE = datetime.datetime.strptime(TAKE_DATE, "%Y-%m-%d")
                        TAKE_TIME = datetime.datetime.strptime(TAKE_TIME, "%H:%M")
                        AVR_TIME = datetime.datetime.strptime(AVR_TIME, "%H:%M")
                        temp_result = [TAKE_DATE,i,sin_req,Day_order[sin_req][1],Day_order[sin_req][5],k,"Vrp",l+1,resource_info[k][5],resource_info[k][6],TAKE_TIME,AVR_TIME]
    #                    print "temp_result",temp_result[7]
                        result.append(temp_result)
    #print useed_resource_info
    #print  result[0][0],result[0][1],result[0][2],result[0][3],result[0][4],result[0][5],result[0][6]
    return useed_resource_info,result
    #print  result
