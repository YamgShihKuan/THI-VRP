# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:35:08 2018

@author: Kuan
"""
import math
import copy
import datetime
import pandas as pd
import pyodbc 
import time
#%% Input
server = 'DESKTOP-C7FFVPQ' 
database = 'CarSharing_VRP' 
username = 'jameschu' 
password = 'jameschu'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

Max_mile = 15
severce_time = 10
#%%
def datafit(data,form):
    colList = []
    for colInfo in data.description:
        colList.append(colInfo[0])
    rowList = []
    while True:
        try:
            row = data.fetchone()
            if row:
                rowList.append(list(row))
#                print list(row)
            else:
                break
        except:   
            continue;
    if form == "pandas":
        sql_data = pd.DataFrame(rowList) 
        sql_data.columns = colList 
    elif form == "list":
        sql_data = rowList
    return sql_data
#%%
sql_start_time = time.time()
cursor = cnxn.cursor()
#cursor.execute('delete from VRP_HAS_MATCHED') 
#cnxn.commit()
#print 
#print "---sql_resource---"
#print 
cursor.execute('SELECT * from VRP_CAR_USEABLE')
sql_resource = datafit(cursor,"list") 
#print (sql_resource)
#%%
#print
#print ("---sql_cost---")
#print
cursor.execute('SELECT * from VRP_TRAVEL_MATRIX_DATA')
sql_cost = datafit(cursor,"list")
#print (sql_cost)
#%%
#print
#print ("---sql_request---")
#print
cursor.execute('SELECT * from VRP_PRE_ORDER')
sql_request = datafit(cursor,"list")
#print len(sql_request)
#request,cost,resource = sql_request,sql_cost,sql_resource
#useed_resource,result = main_fun_v2.main_fun(sql_request,sql_cost,sql_resource)
sql_end_time = time.time()
#print
#print "sql_time",sql_end_time-sql_start_time
#cursor.execute('DELETE FROM VRP_HAS_MATCHED')
#cnxn.commit()
#print (sql_request)
#%% All information 
#print
def main_fun(request,cost,resource): 
    def time_form(intime):
        str_intime =  str(intime)
        int_intime = int(str_intime[11])*10*60+int(str_intime[12])*60+int(str_intime[14])*10+int(str_intime[15])
        return int_intime
    #%% sql cost
    sql_cost_start_time = time.time()
    cost_info = {}
    dist_info = {}   
    for temp_cost in cost:
        cost_info[temp_cost[2],temp_cost[3]] = temp_cost[4]
        cost_info[temp_cost[3],temp_cost[2]] = temp_cost[4]
        cost_info[temp_cost[2],temp_cost[2]] = 0
        cost_info[temp_cost[3],temp_cost[3]] = 0
        dist_info[temp_cost[2],temp_cost[3]] = temp_cost[5]
        dist_info[temp_cost[3],temp_cost[2]] = temp_cost[5]
        dist_info[temp_cost[2],temp_cost[2]] = 0
        dist_info[temp_cost[3],temp_cost[3]] = 0
    sql_cost_end_time = time.time()   
#    print "sql_cost_time",sql_cost_end_time-sql_cost_start_time

    data_start_time = time.time()
    
    tnd_copy_start_time = time.time()   
    t = copy.deepcopy(cost_info)
    d = copy.deepcopy(dist_info)
    tnd_copy_end_time = time.time()   
#    print "tnd_copy_time",tnd_copy_end_time-tnd_copy_start_time

    #%% sql request
    sql_request_start_time = time.time()
    request_info = {}
    village_key = []
    Day_request_info = {}
    
    new_tw = 10
    Day_order = {}
    
    for i in request:
        
        SENDORDER = i[3]
        
        if i[8] == None and i[9] == None:
            Pp,Dp,n_C= i[5],i[6],i[7]
            
            EPT = time_form(i[10])-3*t[Pp,Dp]+new_tw/2
            EDT = time_form(i[11])-t[Pp,Dp]-new_tw/2            
            
            LPT = time_form(i[10])+new_tw/2-15
            LDt = time_form(i[11])-new_tw/2+15 

            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDt]
            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDt,n_C]            
            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDt]
        elif i[10] == None or i[11] == None:
            Pp,Dp,n_C= i[5],i[6],i[7]
            
            EPT = time_form(i[8])+new_tw/2-15
            EDT = time_form(i[9])-new_tw/2+15       
            
            LPT = time_form(i[8])+t[Pp,Dp]-new_tw/2   
            LDt = time_form(i[9])+3*t[Pp,Dp]+new_tw/2   

            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDt]
            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDt,n_C]            
            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDt]            
        else:
            Pp,Dp,n_C= i[5],i[6],i[7]
            
            EPT = time_form(i[8])+new_tw/2-15
            EDT = time_form(i[9])-new_tw/2+15            
            
            LPT = time_form(i[10])+new_tw/2-15
            LDt = time_form(i[11])-new_tw/2+15 
            
            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDt]
            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDt,n_C]             
            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDt]

        SENDORDER_date = "19000000"
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
#    unroute_request_info = request_info.keys()
    sql_request_end_time = time.time()
#    print "sql_request_time",sql_request_end_time-sql_request_start_time
#    print request_info[325]
    
    #%% 
#    print
    sql_resource_start_time = time.time()
    resource_info = {}
    unuse_resource_info = {}
    useed_resource_info = {}
    
    for i in resource:
#        print i 
        temp_resource = [resource.index(i)+1,i[0],i[1],i[2].strftime('%Y/%m/%d'),i[3],i[4],i[5],time_form(i[6]),time_form(i[7]),i[8]]
#        print temp_resource
#        temp_resource.append(i+1)
#        for j in range(resource.shape[1]):
#            temp_value = resource.loc[[i]].values[0][j]
#            if j == 6 or j == 7:
#                temp_value = temp_value.strftime("%H:%M")
#                temp_value = int(temp_value[0:temp_value.find(':')])*60+int(temp_value[temp_value.find(':')+1:])
#            elif j == 2:
#                temp_value = temp_value.strftime('%Y/%m/%d')
#            elif j == 8:
#                temp_value = int(temp_value) 
#            temp_resource.append(temp_value)
        temp_carnumber = temp_resource[4]
        temp_village = temp_resource[3]
        temp_date = temp_resource[0]
    #    print temp_date,temp_village,temp_carnumber
        if temp_carnumber not in unuse_resource_info.keys():
            unuse_resource_info[temp_carnumber] = {}
            useed_resource_info[temp_carnumber] = {}
        if  temp_village not in unuse_resource_info[temp_carnumber].keys():
            unuse_resource_info[temp_carnumber][temp_village] = [temp_date]
            useed_resource_info[temp_carnumber][temp_village] = {}
        else:
            unuse_resource_info[temp_carnumber][temp_village].append(temp_date)
        resource_info[temp_date] = temp_resource
    sql_resource_end_time = time.time()  
#    print "sql_resource_time",sql_resource_end_time-sql_resource_start_time
#    print resource_info
#    print unuse_resource_info
#    print useed_resource_info
    #%%
    Large_cost = 99999
    unservable_requests = {}
    def total_time(route):
        tt_time = 0
        for c in range(len(route)-1):
            tt_time += t[Day_order[route[c]][1],Day_order[route[c+1]][1]]          
        return tt_time
    def total_distant(route):
        tt_dist = 0
        for c in range(len(route)-1):
            tt_dist += d[Day_order[route[c]][1],Day_order[route[c+1]][1]]          
        return tt_dist
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
#        print "seed_list",seed_list
        for i in unuse_resource_info[village][Day]:
            unservable_time = 0
            for j in seed_list: 
                current_routeA = [j,-j]
#                print current_routeA,i,check_feasible_route(current_routeA,i),resource_info[i]
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
    #    print
        debug_time = Day_order[feasible_route[0]][2]
        starttime = resource_info[car_number][-3]
        endtime = resource_info[car_number][-2]
        debug_route_cap = resource_info[car_number][-1]
        debug1 = 0
        debug2 = 0    
        debug_route_time = []
        debug_real_time = []
        ################################################
        #check start time
        if debug_time<starttime:
            debug2 += 10
#        print debug_time,starttime
        debug3 = 0 
        debug4 = 0 
        ################################################
        #check 12Km
#        print
#        print "check 12Km"

        debug5 = 0        
        temp_store_list = [] 
        cal_sign = 0
        cal_anchor = 0
        
        for i in feasible_route :
            temp_store_list.append(i)
            if i not in temp_store_list or -i not in temp_store_list:
                
                cal_sign += 1
            elif i < 0 and -i in temp_store_list:
#                print '*********'
                cal_sign -= 1
#            print i,temp_store_list,cal_sign
            if cal_sign == 0:
#                print "     ---",temp_store_list[cal_anchor:feasible_route.index(i)+1]
                cal_route = temp_store_list[cal_anchor:feasible_route.index(i)+1]
#                print check_feasible_route(temp_store_list[cal_anchor:feasible_route.index(i)+1],car_number)
#                print "     ",cal_route
                o_dist = 0
                for test_c in range(len(cal_route)-1):
#                    print Day_order[cal_route[test_c]][1]
#                    print Day_order[cal_route[test_c+1]][1]
#                    print d[Day_order[cal_route[test_c]][1],Day_order[cal_route[test_c+1]][1]]

                    o_dist += d[Day_order[cal_route[test_c]][1],Day_order[cal_route[test_c+1]][1]]  
        #            print feasible_route[test_c],feasible_route[test_c+1],d[Day_order[feasible_route[test_c]][1],Day_order[feasible_route[test_c+1]][1]]  
#                if (316 in cal_route and 318 in cal_route) or (317 in cal_route and 318 in cal_route):

                if o_dist > Max_mile:
                    debug5 += 10000 
#                    print "~~~~~~~~~~~~~~~~~"
                    
                cal_anchor = feasible_route.index(i)+1 
                
        ################################################
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
                    next_node = Day_order[feasible_route[i+1]][1]
                    if now_node == next_node:
                        continue
                    else:
                        debug_time += severce_time                    
                elif i == len(feasible_route)-1:    
                    debug_time = debug_time+t[pre_node,now_node]
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                elif i > 0:
                    debug_time = max([debug_time+t[pre_node,now_node],e_time])
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                    next_node = Day_order[feasible_route[i+1]][1]
                    if now_node == next_node:
                        continue
                    else:
                        debug_time += severce_time
            for i,j in zip(debug_route_time,debug_real_time):
                if  i > j:
                    debug1 = 1
            if debug_time > endtime:
                debug2 = 10
#        print "    debug_route_time",debug_route_time
#        print "    debug_real_time",debug_real_time
#        print debug_time , endtime
    
    #    debug5 = 0
        debug_signal = debug1 + debug2 + debug4 + debug5
    #    print feasible_route,o_dist,debug_signal
        return debug_signal
    #%%
#    unuse_resource_info = {u'\u5ef6\u5e73\u9109': {'2018/11/19': [1, 2, 3, 4, 5, 6, 7]}}
#    useed_resource_info = {u'\u5ef6\u5e73\u9109': {'2018/11/19': {}}}

    def route_seed_initialer(unroute_list,village,Day):
#        print "route_seed_initialer unroute_list",unroute_list
#        print useed_resource_info[village][Day]
        now_uroute_list = []
        for i in unroute_list:
            now_uroute_list.append(Day_order[i])
        sort_now_uroute_list = sorted(now_uroute_list, key = lambda x : (x[2]))
        sort_uroute_list = []
        for i in sort_now_uroute_list:
            sort_uroute_list.append(i[0])   
#        print sort_uroute_list
        all_car_key_info = []
#        print all_car_key_info
        for i in unuse_resource_info[village][Day]:
            all_car_key_info.append(resource_info[i])

#        print
        sort_all_car_key_info = sorted(all_car_key_info, key = lambda x : (x[-7]))
        sort_all_car_key = []
        for i in sort_all_car_key_info:
            sort_all_car_key.append(i[0])   
    
#            print i
#        print "sort_all_car_key",sort_all_car_key
        new_uroute_list = copy.copy(sort_uroute_list)
#        print "new_uroute_list",new_uroute_list
#        print "unuse_resource_info",unuse_resource_info[village][Day]
        for j in sort_uroute_list:
#            print "----"
            unservable_time = 0
            break_sign = 0
            for i in sort_all_car_key:
                current_routeA = [j,-j]
#                print "  repeat time",len(sort_all_car_key[sort_all_car_key.index(i):])
#                print "current_routeA",current_routeA,i,check_feasible_route(current_routeA,i)#,resource_info[i]
                if check_feasible_route(current_routeA,i) == 0:
#                    print "here"
#                    print " It is feasible",current_routeA,i,j
                    break_sign += 1
                    useed_resource_info[village][Day][i] = [j,-j]
                    
                    new_uroute_list.remove(j)
                    unuse_resource_info[village][Day].remove(i)
                    break
                else:
                    unservable_time += 1

                    len(sort_all_car_key[sort_all_car_key.index(i):])
            if unservable_time == len(sort_all_car_key):
#                print "j",j
#                print "unservable_requests",unservable_requests
                if Day not in unservable_requests.keys():
                    unservable_requests[Day] = []
                    unservable_requests[Day].append(j)
                else:
                    unservable_requests[Day].append(j)
                new_uroute_list.remove(j)
            if break_sign>0:
                break
#        print "useed_resource_info",useed_resource_info[village][Day]
#        print "new_uroute_list",new_uroute_list
        return new_uroute_list
#    unroute_list,village,Day = [316, 317, 318, 319, 320, 321, 322, 323, 324],u'\u5ef6\u5e73\u9109','2018/11/19'
    
#    print route_seed_initialer(unroute_list,village,Day)    
    #%% regret_insert
    def regret_insert(unroute_list,village,Day):
#        print "unroute_list",unroute_list
#        for fadfad in range(10):
        while len(unroute_list) > 0:
#            print "unroute_list",unroute_list
            current_list = useed_resource_info[village][Day].values()
#            print useed_resource_info
#            print "current_list",current_list
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
                        o_route_tt_dist += d[Day_order[o_route[test_c]][1],Day_order[o_route[test_c+1]][1]]                      
                    c1_value = []
                    c1_place = []
                    for p_place in range(len(o_route)+1):         
                        test_p_route =  copy.copy(o_route)
                        test_p_route.insert(p_place,customer_p)
#                        print
#                        print "test_p_route-----------",test_p_route                        
#                        feasibility1 = check_feasible_route(test_p_route,car_number)
#                        print "-----------feasibility1",feasibility1
                        feasibility1 = 0
                        if feasibility1 == 0:
                            for d_place in range(p_place+1,len(test_p_route)+1):
                                #print d_place,"----"
                                test_d_route = copy.copy(test_p_route)
                                test_d_route.insert(d_place,customer_d)
#                                print"--"                                
                                feasibility2 = check_feasible_route(test_d_route,car_number)
#                                if (316 in test_d_route and 318 in test_d_route) or (317 in test_d_route and 318 in test_d_route):
#                                    print test_d_route,feasibility2
#                                    print "--"
#                                print"--"
                                if feasibility2 == 0:###############
                                    ##################################################################
                                    tt_dist = 0
                                    for test_c in range(len(test_d_route)-1):
                                        tt_dist += d[Day_order[test_d_route[test_c]][1],Day_order[test_d_route[test_c+1]][1]]
#                                    c1 = tt_dist-o_route_tt_dist
                                    c1 = tt_dist
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
#                print "----"
#                unservable_requests[Day] = unroute_list ##route2
#                break
                unroute_list = route_seed_initialer(unroute_list,village,Day)
                
        return current_list
    
    #%% time window reduce
    def tw_reducer(feasible_route,car_number):
#        print feasible_route
#        if True:
#            for i in feasible_route:
#                print Day_order[i][2],Day_order[i][3]
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
                next_node = Day_order[feasible_route[i+1]][1]
                if now_node == next_node:
                    continue
                else:
                    debug_time += severce_time                
            elif i == len(feasible_route)-1:
                debug_time = debug_time+t[pre_node,now_node]
                debug_route_time.append(debug_time)
                debug_real_time.append(endtime)
            elif i > 0:
                debug_time = max([debug_time+t[pre_node,now_node],e_time])
                debug_route_time.append(debug_time)
                debug_real_time.append(l_time)   
                next_node = Day_order[feasible_route[i+1]][1]
                if now_node == next_node:
                    continue
                else:
                    debug_time += severce_time                
        for i,j in zip(feasible_route,debug_route_time):

            if i > 0:
    
                Day_order[i][2] = math.floor(j - new_tw/2)
                Day_order[i][3] = math.floor(j + new_tw/2)
            elif i < 0:
    
                Day_order[-i][6] = math.floor(j - new_tw/2)
                Day_order[-i][7] = math.floor(j + new_tw/2)
                Day_order[i][2] = math.floor(j - new_tw/2)
                Day_order[i][3] = math.floor(j + new_tw/2)
#        if 329 in feasible_route:
#        if True:
#                
#            print "debug_route_time",debug_route_time
#            print "debug_route_time",debug_real_time                    
#            for i in feasible_route:
#                print Day_order[i][2],Day_order[i][3]  
#        print                  
    #%%
    start_time =	time.time()
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
    #        for reser_Day in reser_Day_keys[:1]:
            for reser_Day in reser_Day_keys:
                unroute_Day_requests = copy.copy(Day_request[village][day][reser_Day])
#                print unroute_Day_requests
                reserve_Plan_key = reserve_Plan[village][day].keys()
                if reser_Day not in reserve_Plan_key:
                    unroute_Day_requests = route_seed_initialer(unroute_Day_requests,village,reser_Day)
#                    print "unroute_Day_requests",unroute_Day_requests
                    final_route = regret_insert(unroute_Day_requests,village,reser_Day)
#                    print final_route
                    reserve_Plan[village][day][reser_Day] = final_route
                else:
                    final_route = regret_insert(unroute_Day_requests,village,reser_Day)
                    reserve_Plan[village][day][reser_Day] = final_route
#                for i in final_route:
#                    print i,"-"
#                print useed_resource_info[village][reser_Day]
#                plan_cost = 0
#                for i in useed_resource_info[village][reser_Day].values():
#                    print i
#                    plan_cost += tt_cost(i)
#                print plan_cost
                
                ###Trip insertion
#                o_useed_resource = copy.deepcopy(useed_resource_info[village][reser_Day])
#                print "before",o_useed_resource
#                for i in o_useed_resource:
#                    print o_useed_resource[i]
#                    cana_trip = []
#                    for j in  o_useed_resource[i]:
#                        if j >0:
#                            cana_trip.append(j)
#                    print cana_trip
#                    other_route = o_useed_resource.keys()
#                    other_route.remove(i)
#                    print "other_route",other_route
#                    
#                    for k in cana_trip:
#                        print "k",k
#                        now_plan = copy.deepcopy(o_useed_resource)
#                        now_plan[i].remove(k)
#                        now_plan[i].remove(-k)
#                        print "now_plan",now_plan
#                        
#                        for l in other_route: 
#                            for m in range(len(now_plan[l])+1):
#                                for n in range(m+1,len(now_plan[l])+2):
#                                    insert_plan = copy.deepcopy(now_plan)
#                                    insert_plan[l].insert(m,k)
#                                    insert_plan[l].insert(n,-k)
#                                    temp_tt = 0
#                                    for o in insert_plan.values():
#                                        temp_tt += tt_cost(o)
#                                    print "m",m,"n",n,insert_plan[l],check_feasible_route(insert_plan[l],l),l,temp_tt
#                print "after",o_useed_resource       
                ##########reduce the window###########
                for i in useed_resource_info: ####
                    for j in  sorted(useed_resource_info[i]):
                        for k in useed_resource_info[i][j]:
                            tw_reducer(useed_resource_info[i][j][k],k)
    end_time = time.time()
#    print "program_time",end_time-start_time            

    #%%
    result_start_time = time.time()
    result = []
    trip_number = 0
    for i in useed_resource_info.keys(): 
        for j in sorted(useed_resource_info[i].keys()):          
            for k in useed_resource_info[i][j]:
                #######################
#                print "###############",useed_resource_info[i][j][k]
                test_route = useed_resource_info[i][j][k]        
                temp_store_list = [] 
                cal_sign = 0
                cal_anchor = 0
                trip_list = []
                trip_dict ={}
                for cus in test_route :
                    temp_store_list.append(cus)
                    if cus not in temp_store_list or -cus not in temp_store_list:
                        cal_sign += 1
                    elif cus < 0 and -cus in temp_store_list:
                        cal_sign -= 1
                    if cal_sign == 0:
        #                print "     ---",temp_store_list[cal_anchor:feasible_route.index(i)+1]
                        cal_route = temp_store_list[cal_anchor:test_route.index(cus)+1]
                        trip_list.append(cal_route)
                        cal_anchor = test_route.index(cus)+1 
#                print trip_list
                run_sign = True
                start_sign = 0
                while run_sign == True:
                    if len(trip_list)>1:
                        test_trip = trip_list[start_sign] + trip_list[start_sign+1]
#                        print "test_trip",test_trip,total_distant(test_trip)
                        if total_distant(test_trip) > Max_mile:
                            start_sign += 1
                        else:
                            trip_list[start_sign] = test_trip
                            trip_list.remove(trip_list[start_sign+1])
                        if start_sign == len(trip_list)-1:
                            run_sign = False

                    else:
                        run_sign = False
#                        print trip_list,start_sign
  
                p_new_trip = []
                for m in trip_list:
                    temp_p_new_trip = []
                    for l in m:
                        if l > 0:
                            temp_p_new_trip.append(l)
                    p_new_trip.append(temp_p_new_trip)
#                print p_new_trip
                for m in range(len(p_new_trip)):
                    trip_number += 1
                    for l in range(len(p_new_trip[m])):
                        if p_new_trip[m][l] > 0:
                            trip_dict[p_new_trip[m][l]] = trip_number
                            sin_req = p_new_trip[m][l]
                            ID_VRP = l+1
#                            print sin_req,trip_number,ID_VRP
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
                            temp_result = [TAKE_DATE,i,sin_req,Day_order[sin_req][1],Day_order[sin_req][5],trip_number,"Vrp",ID_VRP,resource_info[k][6],resource_info[k][5],TAKE_TIME,AVR_TIME]
#                            print "temp_result",temp_result
                            result.append(temp_result)    
#                            print result[l]
                #######################                  
#                temp_req_list = []
#                
#                for m in range(len(useed_resource_info[i][j][k])):
#                    if useed_resource_info[i][j][k][m] > 0:
#                        temp_req_list.append(useed_resource_info[i][j][k][m])
#    #            print temp_req_list
#                for l in range(len(temp_req_list)):
#                    sin_req = temp_req_list[l]
#                    print "sin_req,l",sin_req,l
#                    if sin_req > 0:
#                        EPT = str(int(Day_order[sin_req][2]//60))+":"+str(int(Day_order[sin_req][2]%60))
#                        EDT = str(int(Day_order[sin_req][3]//60))+":"+str(int(Day_order[sin_req][3]%60))
#                        LPT = str(int(Day_order[sin_req][6]//60))+":"+str(int(Day_order[sin_req][6]%60))
#                        LDt = str(int(Day_order[sin_req][7]//60))+":"+str(int(Day_order[sin_req][7]%60))
#                        TAKE_TIME = str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2//60))+":"+str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2%60))
#                        AVR_TIME = str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2//60))+":"+str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2%60))
#                        TAKE_DATE = j[0:4]+"-"+j[5:7]+"-"+j[8:]
#                        TAKE_DATE = datetime.datetime.strptime(TAKE_DATE, "%Y-%m-%d")
#                        TAKE_TIME = datetime.datetime.strptime(TAKE_TIME, "%H:%M")
#                        AVR_TIME = datetime.datetime.strptime(AVR_TIME, "%H:%M")
#                        temp_result = [TAKE_DATE,i,sin_req,Day_order[sin_req][1],Day_order[sin_req][5],k,"Vrp",l+1,resource_info[k][6],resource_info[k][5],TAKE_TIME,AVR_TIME]
#    #                    print "temp_result",temp_result[7]
#                        result.append(temp_result)
    result_end_time = time.time()    
#    print "result_time",result_end_time-result_start_time   
#    print result         
#    print  result[0][0],result[0][1],result[0][2],result[0][3],result[0][4],result[0][5],result[0][6]
#    for i in  useed_resource_info[u'\u5ef6\u5e73\u9109']['2018/11/19'].values():
#    print
#    print
#    print useed_resource_info
#    print unservable_requests
#    if len(unservable_requests)>0:
#        print "unservable_requests",unservable_requests['2018/11/19']
    return useed_resource_info,result
    #print  result
#    print useed_resource_info

#%%
useed_resource,result = main_fun(sql_request,sql_cost,sql_resource)
#print result[0][0],result[0][1],result[0][2],result[0][3],result[0][4],result[0][5],result[0][6],result[0][7],result[0][8],result[0][9],result[0][10],result[0][11]
#for i in range(len(result)):
#    print result[i][2]
#for i in useed_resource.keys():
#    print i    
#    for  j in sorted(useed_resource[i].keys()):
#    #    print useed_resource_info[i]
#        print "----",j
#        for k in useed_resource[i][j]:
#            print i,j,useed_resource[i][j][k],",",k#,check_feasible_route(useed_resource_info[i][j][k],k)
#%%
for i in range(len(result)):
    cursor.execute("""INSERT INTO VRP_HAS_MATCHED (ENTERPRISEID,
                                               TAKE_DATE, 
                                                 GROUP_NAME, 
                                                 PASSENGER_ORDER_ID, 
                                                 START_PLACE, 
                                                 END_PLACE, 
                                                 SENDORDER_ID_VRP, 
                                                 TYPE, 
                                                 UP_ORDER, 
                                                 DRIVER_NAME, 
                                                 CAR_NUMBER, 
                                                 TAKE_TIME, 
                                                 AVR_TIME)
                                                 
                                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""","None",result[i][0],result[i][1],result[i][2],result[i][3],result[i][4],result[i][5],result[i][6],result[i][7],result[i][8],result[i][9],result[i][10],result[i][11])

cursor.execute('SELECT * from VRP_HAS_MATCHED')
#VRP_HAS_MATCHED = datafit(cursor,"pandas") 
#print VRP_HAS_MATCHED
cnxn.commit()
