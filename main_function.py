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
#import pprint
#%% sql sever setting
#server = '' 
#database = '' 
#username = '' 
#password = '' 
#cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

server = '' 
database = '' 
username = '' 
password = ''
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
#%% parameter setting
Max_mile = 20 # upper limit for a ride
service_time = 5 # service time when  arrive locstion 
down_service_time = 1
time_window = 30 # aditional time windows
constant_a = 3
constant_b = 5
Max_trip_interval = 15 #minutes
new_tw = 5
Large_cost = 99999
#%% input three sql data sheet

## a funtion to transfer the form of data
## transfer into pandas or list 
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


## delete the data has been create and recalculate 
cursor = cnxn.cursor()
cursor.execute('delete from VRP_HAS_MATCHED') 
cnxn.commit()
 
#print "---sql_resource---"
cursor.execute("SELECT * from VRP_CAR_USEABLE ")
sql_resource = datafit(cursor,"list") 

#print ("---sql_cost---")
cursor.execute("SELECT * from VRP_TRAVEL_MATRIX_DATA ")
sql_cost = datafit(cursor,"list")

#print ("---sql_request---")
cursor.execute("SELECT * from VRP_PRE_ORDER")
sql_request = datafit(cursor,"list")

## if you want the data in a specific day
#cursor.execute("SELECT * from VRP_CAR_USEABLE where take_date ='2019/01/14'")
#cursor.execute("SELECT * from VRP_TRAVEL_MATRIX_DATA where take_date ='2019/01/14'")
#cursor.execute("SELECT * from VRP_PRE_ORDER where take_date ='2019/01/14'")

## if you want the data in a specific period
#cursor.execute("SELECT * from VRP_CAR_USEABLE where take_date between '2019/01/14' and '2019/01/18'")
#cursor.execute("SELECT * from VRP_TRAVEL_MATRIX_DATA where take_date between '2019/01/14' and '2019/01/18'")
#cursor.execute("SELECT * from VRP_PRE_ORDER where take_date between '2019/01/14' and '2019/01/18'")

#%% Main procedure 
def main_funtion(request,cost,resource): 
      
    ## a funtion to transfer the time format
    def time_form(intime):
        str_intime = str(intime)
        int_intime = int(str_intime[11])*10*60+int(str_intime[12])*60+int(str_intime[14])*10+int(str_intime[15])
        return int_intime 
    
    ## calculate the route time
    def total_time(route):
        tt_time = 0
        for c in range(len(route)-1):
            tt_time += t[Day_order[route[c]][1],Day_order[route[c+1]][1]]          
        return tt_time
    
    ## calculate the route distant
    def total_distant(route):
        tt_dist = 0
        for c in range(len(route)-1):
            tt_dist += d[Day_order[route[c]][1],Day_order[route[c+1]][1]]          
        return tt_dist
    
    ## give the route a start customer
    ## 
    def route_seed_initialer(unroute_list,village,Day):
        ## sort the unroute customers acordding to the pick up time
        now_unroute_list = []
        for i in unroute_list:
            now_unroute_list.append(Day_order[i])
        sort_now_unroute_list = sorted(now_unroute_list, key = lambda x : (x[2]))
        sort_unroute_list = []
        for i in sort_now_unroute_list:
            sort_unroute_list.append(i[0]) 
        ## sort the car drivers acordding to the starting service time    
        all_car_key_info = []
        for i in unuse_resource_info[village][Day]:
            all_car_key_info.append(resource_info[i])
        sort_all_car_key_info = sorted(all_car_key_info, key = lambda x : (x[-7]))
        sort_all_car_key = []
        for i in sort_all_car_key_info:
            sort_all_car_key.append(i[0])  
        ## give the route a start customer
        ## return the unroute list without the customerhave been matched
        new_unroute_list = copy.copy(sort_unroute_list)
        for j in sort_unroute_list:
            unservable_time = 0
            break_sign = 0
            for i in sort_all_car_key: #i就是車號
                current_routeA = [i,j,-j,i]
                if check_feasible_route(current_routeA,i) == 0: #輸入路徑與車號
                    break_sign += 1
                    useed_resource_info[village][Day][i] = [i,j,-j,i]   
                    new_unroute_list.remove(j)
                    unuse_resource_info[village][Day].remove(i)
                    break
                else:
                    unservable_time += 1
                    len(sort_all_car_key[sort_all_car_key.index(i):])
            if unservable_time == len(sort_all_car_key):
                if Day not in unservable_requests.keys():
                    unservable_requests[Day] = []
                    unservable_requests[Day].append(j)
                else:
                    unservable_requests[Day].append(j)
                new_unroute_list.remove(j)
            if break_sign>0:
                break
            #只要有一個人可以放進一台車就可以
#        print "in ",useed_resource_info[village][Day]
        return new_unroute_list    
    
    def route_seed_initialer2(unroute_list,village,Day):
#        print unroute_list,village,Day
        now_unroute_list = []
        for i in unroute_list:
            now_unroute_list.append(Day_order[i])
        sort_now_unroute_list = sorted(now_unroute_list, key = lambda x : (x[2]))
        sort_unroute_list = []
        for i in sort_now_unroute_list:
            sort_unroute_list.append(i[0])
        seed_list = copy.copy(sort_unroute_list)
        new_unroute_list = []
        for i in range(len(sort_unroute_list)-1):
            req_i = sort_unroute_list[i]
            req_i_1 = sort_unroute_list[i+1]
            LDTk = Day_order[req_i][7]
            TTDkPk_1 = t[Day_order[req_i][5],Day_order[req_i_1][1]]
            EPTk_1 = Day_order[req_i_1][2]
            if LDTk+TTDkPk_1<=EPTk_1:
                seed_list.remove(req_i_1)
                new_unroute_list.append(req_i_1)
        for i in unuse_resource_info[village][Day]:
            unservable_time = 0
            for j in seed_list: 
                current_routeA = [i,j,-j,i]
                if check_feasible_route(current_routeA,i) == 0:
                    useed_resource_info[village][Day][i] = [i,j,-j,i]
                    seed_list.remove(j)
                    break                  
                else:
                    unservable_time += 1
        for i in useed_resource_info[village][Day].keys():
            if i in unuse_resource_info[village][Day]:
                unuse_resource_info[village][Day].remove(i)
#        print "in ",useed_resource_info[village][Day]
        return new_unroute_list+seed_list  
   
    def check_feasible_route(feasible_route,car_number):
#        print feasible_route,car_number
        debug_time = Day_order[feasible_route[0]][2] ## first customer pick time 
        max_car_capacity = resource_info[car_number][-1] ## car capacity
  
        route_feasible_or_not = True
        ## check if the trip exceeds the max trip miles
        if route_feasible_or_not == True:
            temp_store_list = [] 
            cal_sign = 0
            cal_anchor = 0
            
            for i in feasible_route :
                if type(i) ==  int:
                    temp_store_list.append(i)
                    if i not in temp_store_list or -i not in temp_store_list:        
                        cal_sign += 1
                    elif i < 0 and -i in temp_store_list:
                        cal_sign -= 1
                    if cal_sign == 0:
                        cal_route = temp_store_list[cal_anchor:feasible_route.index(i)+1]
#                        print cal_anchor,feasible_route.index(i)+1
                        o_dist = total_distant(cal_route)
#                        for test_c in range(len(cal_route)-1):
#                            o_dist += d[Day_order[cal_route[test_c]][1],Day_order[cal_route[test_c+1]][1]]         
                        
                        if o_dist >= Max_mile:
                            route_feasible_or_not = False 
#                        else:
#                            print cal_route,car_number,total_distant(cal_route)
                            
                        cal_anchor = feasible_route.index(i)+1 
        ## check if the capacity exceeds the car limit               
        passenger_in_car = 0 
        if route_feasible_or_not == True: 
            for x in feasible_route:
                if x > 0 :
                    passenger_in_car += Day_order[x][4] 
                elif x <0:
                    passenger_in_car -= Day_order[x][4]
                if passenger_in_car > max_car_capacity:

                    route_feasible_or_not = False
                    break
                
        ## check the route time window  
        debug_route_time = []
        debug_real_time = []    
        if route_feasible_or_not == True: 
            for i in range(len(feasible_route)):
                pre_node = Day_order[feasible_route[i-1]][1]            
                now_node = Day_order[feasible_route[i]][1]
    
                e_time = Day_order[feasible_route[i]][2] #early最早上車
                l_time = Day_order[feasible_route[i]][3] #latest 最晚上車
    
                if i == 0:
                    debug_route_time.append(debug_time)
                    debug_real_time.append(debug_time)
                    next_node = Day_order[feasible_route[i+1]][1]
                    if now_node == next_node:
                        continue
                    else:
                        if feasible_route[i] < 0:
#                            print feasible_route[i-1]
                            debug_time += down_service_time
#                            debug_time += service_time 
                        else:    
                            debug_time += service_time                   
                elif i == len(feasible_route)-1:    
                    debug_time = debug_time+t[pre_node,now_node]
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                elif i > 0:
#                    print pre_node,now_node
                    debug_time = max([debug_time+t[pre_node,now_node],e_time])
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                    next_node = Day_order[feasible_route[i+1]][1]
                    if now_node == next_node:
                        continue
                    else:
                        if feasible_route[i] < 0:
                            debug_time += down_service_time   
                        else:    
                            debug_time += service_time
            for i,j in zip(debug_route_time,debug_real_time):
                if  i > j:
#                    print i,j
#                    debug1 = 1
                    route_feasible_or_not = False                    

        if route_feasible_or_not == True:  
            debug_signal = 0
        else:
            debug_signal = 1
#        if 14410 in feasible_route:
#            print feasible_route,car_number,route_feasible_or_not
           
        return debug_signal

    def regret_insert(unroute_list,village,Day):
#        print "unroute_list",unroute_list,village,Day
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
#            print "----"
            for customer in unroute_list:
#                print customer
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
                    for p_place in range(1,len(o_route)+1):         
                        test_p_route =  copy.copy(o_route)
                        test_p_route.insert(p_place,customer_p)
#                        print
#                        print "test_p_route-----------",test_p_route                        
#                        feasibility1 = check_feasible_route(test_p_route,car_number)
#                        print "-----------feasibility1",feasibility1
                        feasibility1 = 0
                        if feasibility1 == 0:
                            for d_place in range(p_place+1,len(test_p_route)):
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
#                                    tt_dist = total_distant(test_d_route)
#                                    print test_d_route
#                                    for test_c in range(len(test_d_route)-1):
##                                        print test_d_route[test_c],test_d_route[test_c+1],d[Day_order[test_d_route[test_c]][1],Day_order[test_d_route[test_c+1]][1]]
#                                        tt_dist += d[Day_order[test_d_route[test_c]][1],Day_order[test_d_route[test_c+1]][1]]
#                                    c1 = tt_dist-o_route_tt_dist
                                    c1 = total_distant(test_d_route)
#                                    print test_d_route,c1
                                    ##################################################################
                                    c1_value.append(c1)
                                    c1_place.append([p_place,d_place])
                                
                    min_c1_route.append(o_route)  
#                    print c1_value
                    if len(c1_value) > 0:
                        min_value = min(c1_value)
                        min_place = c1_place[c1_value.index(min_value)]                           
                        min_c1_value.append(min_value)
                        min_c1_place.append(min_place)
                    else:                
                        min_c1_value.append(Large_cost)
                        min_c1_place.append([-Large_cost,-Large_cost])     
#                print "min_c1_value",min_c1_value
                min_min_c1_value = min(min_c1_value)
                min_c1_index = min_c1_value.index(min_min_c1_value)
                min_min_c1_place = min_c1_place[min_c1_index]
                min_min_c1_route = min_c1_route[min_c1_index]
                c2_customer.append([customer,-customer])
#                print c2_customer
                c2 = 0
                if min_c1_value.count(Large_cost) != len(min_c1_value):
#                    print min_c1_value
                    for mmc in range(len(min_c1_value)):
#                        print min_c1_route[mmc],min_min_c1_route
#                        if min_c1_route[mmc] != min_min_c1_route:
                            
                        c2 += min_c1_value[mmc] - min_min_c1_value
#                        print "------------",c2
                else:
                    c2 = -Large_cost
                c2_value.append(c2)
                c2_route.append(min_min_c1_route)
                c2_place.append(min_min_c1_place)  
#                print c2_value,c2_route,c2_place
#            print c2_value  
            if c2_value.count(-Large_cost) != len(c2_value):
#                print "1111111111111"
                max_c2_value = max(c2_value)
#                print max_c2_value
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
#                print "----",Day,unroute_list
#                unservable_requests[Day] = unroute_list ##route2
#                break
                unroute_list = route_seed_initialer(unroute_list,village,Day)
                
        return current_list
    
#    def tw_reducer(feasible_route,car_number):
##        print feasible_route
##        if True:
##            for i in feasible_route:
##                print Day_order[i][2],Day_order[i][3]
#        debug_time = Day_order[feasible_route[0]][2]
#        endtime = resource_info[car_number][-2]
#        debug_route_time = []
#        debug_real_time = []
#        for i in range(len(feasible_route)):          
#            pre_node = Day_order[feasible_route[i-1]][1]            
#            now_node = Day_order[feasible_route[i]][1]
#            e_time = Day_order[feasible_route[i]][2]
#            l_time = Day_order[feasible_route[i]][3]
#            if i == 0:
#                debug_route_time.append(debug_time)
#                debug_real_time.append(debug_time)
#                next_node = Day_order[feasible_route[i+1]][1]
#                if now_node == next_node:
#                    continue
#                else:
#                    if feasible_route[i] < 0:
##                            print feasible_route[i-1]
#                        debug_time += down_service_time
##                            debug_time += service_time
#                        
#                    else:    
#                        debug_time += service_time              
#            elif i == len(feasible_route)-1:
#                debug_time = debug_time+t[pre_node,now_node]
#                debug_route_time.append(debug_time)
#                debug_real_time.append(endtime)
#            elif i > 0:
#                debug_time = max([debug_time+t[pre_node,now_node],e_time])
#                debug_route_time.append(debug_time)
#                debug_real_time.append(l_time)   
#                next_node = Day_order[feasible_route[i+1]][1]
#                if now_node == next_node:
#                    continue
#                else:
#                    if feasible_route[i] < 0:
##                            print feasible_route[i-1]
#                        debug_time += down_service_time
##                            debug_time += service_time
#                        
#                    else:    
#                        debug_time += service_time                 
#        for i,j in zip(feasible_route,debug_route_time):
#
#            if i > 0:
#    
#                Day_order[i][2] = math.floor(j - new_tw/2)
#                Day_order[i][3] = math.floor(j + new_tw/2)
#            elif i < 0:
#    
#                Day_order[-i][6] = math.floor(j - new_tw/2)
#                Day_order[-i][7] = math.floor(j + new_tw/2)
#                Day_order[i][2] = math.floor(j - new_tw/2)
#                Day_order[i][3] = math.floor(j + new_tw/2)


    def relocation_operator(original_plan):
        all_reinsert_info = {}
        for i in original_plan:
            for j in original_plan[i]:
                if j > 0 :
                    all_reinsert_info[j] = i 
        all_route = original_plan.keys()
        
        relocation_for_remove_time = 0
        relocation_for_insert_time = 0
        for relocate_time in range(1):
            for i in all_reinsert_info:
                
                relocation_for_remove_start_time = time.time()
                car_c = all_reinsert_info[i]
                remoeve_route_c = original_plan[car_c][:]
                if type(i) == int:
                    remoeve_route_c.remove(i)
                    remoeve_route_c.remove(-i)
                    relocation_for_remove_end_time = time.time()
                    relocation_for_remove_time += (relocation_for_remove_end_time-relocation_for_remove_start_time)
                    for l in all_route:
                        if l != car_c:
                            for m in range(1,len(original_plan[l])+1):
                                for n in range(m+1,len(original_plan[l])+1):
                                    if i in original_plan[car_c]:  
                                        relocation_for_insert_start_time = time.time()
                                        insert__route_c = original_plan[l][:]
                                        insert__route_c.insert(m,i)
                                        insert__route_c.insert(n,-i)
                                        relocation_for_insert_end_time = time.time()
                                        relocation_for_insert_time += (relocation_for_insert_end_time-relocation_for_insert_start_time)
        #                                print insert__route_c,check_feasible_route(insert__route_c,l)
                                        if check_feasible_route(insert__route_c,l) == 0:
        #                                    print insert__route_c,check_feasible_route(insert__route_c,l)
                                            if total_distant(original_plan[car_c])+total_distant(original_plan[l])-total_distant(remoeve_route_c)-total_distant(insert__route_c) > 0:
#                                                print total_distant(original_plan[car_c])+total_distant(original_plan[l])-total_distant(remoeve_route_c)-total_distant(insert__route_c) 
                                                original_plan[car_c] = remoeve_route_c
                                                original_plan[l] = insert__route_c
                                                all_reinsert_info[i] = l   
                                            if len(remoeve_route_c) == 0 or len(insert__route_c) == 0 :
                                                print "need to cut car"                                            
                                    else:
                                        break 
        return original_plan
    def exchange_operator(original_plan):
        all_reinsert_info = {}
        for i in original_plan:
#            print i,original_plan[i]
            for j in original_plan[i]:
#                print j
                if j > 0 and type(j) == int:
                    all_reinsert_info[j] = i
        exchange_first_insert = 0
        exchange_second_insert = 0
    #    exchange_start_time = time.time()
        for exchange_time in range(1):
            for i in all_reinsert_info:
                for j in all_reinsert_info:
                    car_r = all_reinsert_info[i]
                    car_s = all_reinsert_info[j]
                    if i != j and car_r != car_s:
            #            print 
            #            print Day_order[i],Day_order[j]
                        EPTi = Day_order[i][2]
                        LPTi = Day_order[i][3]
                        EDTi = Day_order[i][6]
                        LDTi = Day_order[i][7]       
                        EPTj = Day_order[j][2]
                        LPTj = Day_order[j][3]
                        EDTj = Day_order[j][6]
                        LDTj = Day_order[j][7]           
                        if (EPTi <= LPTj and EPTj <= LPTi) or (EDTi <= LDTj and EDTj <= LDTi):                    
       
                            remoeve_route_r = original_plan[car_r][:]
                            remoeve_route_r.remove(i)
                            remoeve_route_r.remove(-i)
                            
                            best_insert_route_r = []
                            exchange_first_start_insert = time.time()
                            for m in range(1,len(remoeve_route_r)+1):
                                for n in range(m+1,len(remoeve_route_r)+1):
    #                                print m,n
                                    insert_route_r = remoeve_route_r[:]
    #                                insert_route_r = copy.deepcopy(remoeve_route_r)
                                    insert_route_r.insert(m,j)
                                    insert_route_r.insert(n,-j)
    #                                print insert_route_r,check_feasible_route(insert_route_r,car_r)
                                    if check_feasible_route(insert_route_r,car_r) == 0:
                                        if len(best_insert_route_r) == 0:
                                            best_insert_route_r = insert_route_r
                                        else:
                                            if total_distant(insert_route_r) < total_distant(best_insert_route_r):
                                                best_insert_route_r = insert_route_r
            
                            exchange_first_end_insert = time.time()            
                            exchange_first_insert += (exchange_first_end_insert-exchange_first_start_insert)    
                            if len(best_insert_route_r) > 0 :        
                                remoeve_route_s = original_plan[car_s][:]
                                remoeve_route_s.remove(j)
                                remoeve_route_s.remove(-j) 
                                exchange_second_start_insert = time.time()
                                best_insert_route_s = []
                                for m in range(1,len(remoeve_route_s)+1):
                                    for n in range(m+1,len(remoeve_route_s)+1):
                                        insert_route_s = remoeve_route_s[:]
                                        insert_route_s.insert(m,i)
                                        insert_route_s.insert(n,-i)                
                                        if check_feasible_route(insert_route_s,car_s) == 0:
                #                            print "-------------------"
                                            if len(best_insert_route_s) == 0:
                                                best_insert_route_s = insert_route_s
                                            else:
                                                if total_distant(insert_route_s) < total_distant(best_insert_route_s):
                                                    best_insert_route_s = insert_route_s
                                exchange_second_end_insert = time.time()
                                exchange_second_insert += (exchange_second_end_insert-exchange_second_start_insert)
                                if len(best_insert_route_s) > 0:
                                    if (total_distant(original_plan[car_r])+total_distant(original_plan[car_s]))-(total_distant(best_insert_route_r)+total_distant(best_insert_route_s))>0:
#                                        print (total_distant(original_plan[car_r])+total_distant(original_plan[car_s]))-(total_distant(best_insert_route_r)+total_distant(best_insert_route_s))
                                        original_plan[car_r] = best_insert_route_r                 
                                        original_plan[car_s] = best_insert_route_s
                                        all_reinsert_info[i] = car_s
                                        all_reinsert_info[j] = car_r  
                                        if len(best_insert_route_r) == 0 or len(best_insert_route_s) == 0 :
                                            print "need to cut car"
        return original_plan   


    def check_service_time(feasible_route,out_type = None):
#        print feasible_route
        debug_time = Day_order[feasible_route[0]][2]
#        print debug_time
        debug_service_time = []   
        for i in range(len(feasible_route)):
            pre_node = Day_order[feasible_route[i-1]][1]            
            now_node = Day_order[feasible_route[i]][1]

            e_time = Day_order[feasible_route[i]][2]
#            l_time = Day_order[feasible_route[i]][3]
            if i == 0:
                debug_service_time.append(debug_time)
            elif i == len(feasible_route)-1:        
                debug_time = debug_time+t[pre_node,now_node]
                debug_service_time.append(debug_time)
            else:
                debug_time = max([debug_time+t[pre_node,now_node],e_time])
                debug_service_time.append(debug_time)
                if now_node > 0:
                    debug_time += service_time
#                print "afterser:",debug_time
        ri_time = 0
        test_n = 0                    
        for i in range(len(feasible_route)):
    #        print i,test[i],test[i+1],t[Day_order[test[i]][1],Day_order[test[i+1]][1]]
            if type(feasible_route[i]) == int:
                test_n += feasible_route[i]
                if feasible_route[i] > 0:
                    test_target = feasible_route.index(-feasible_route[i])
                    
                    ride_time =  debug_service_time[test_target] - debug_service_time[i]   
                    ri_time += ride_time
        if out_type == "list":
            return debug_service_time
        else:
            return ri_time         

    def check_arrive_time(feasible_route,out_type = None):
#        print feasible_route
        debug_time = Day_order[feasible_route[0]][2]
#        print debug_time
        debug_arrive_time = []   
        for i in range(len(feasible_route)):
            pre_node = Day_order[feasible_route[i-1]][1]            
            now_node = Day_order[feasible_route[i]][1]

            e_time = Day_order[feasible_route[i]][2]
#            l_time = Day_order[feasible_route[i]][3]
            if i == 0:
                debug_arrive_time.append(debug_time)
            elif i == len(feasible_route)-1:        
                debug_time = debug_time+t[pre_node,now_node]
                debug_arrive_time.append(debug_time)
            else:
                debug_arrive_time.append(debug_time+t[pre_node,now_node])
                debug_time = max([debug_time+t[pre_node,now_node],e_time])
                
                if now_node > 0:
                    debug_time += service_time
#                print "afterser:",debug_time
        ri_time = 0
        test_n = 0  
                          
        for i in range(len(feasible_route)):
    #        print i,test[i],test[i+1],t[Day_order[test[i]][1],Day_order[test[i+1]][1]]
            if type(feasible_route[i]) == int:
                test_n += feasible_route[i]
                if feasible_route[i] > 0:
                    test_target = feasible_route.index(-feasible_route[i])
                    ride_time =  debug_arrive_time[test_target] - debug_arrive_time[i]   
                    ri_time += ride_time
#        print debug_arrive_time                
        if out_type == "list":
            return debug_arrive_time
        else:
            return ri_time                     
    def ride_counter(feasible_route,out_type = None):
#        print "    ",feasible_route
#        print "debug_time",debug_time
        node_service_time = check_service_time(feasible_route,"list")
        node_arrive_time = check_arrive_time(feasible_route,"list")
        ##########################
        test = feasible_route
        
        e_time_list = [Day_order[i][2] for i in feasible_route]
        l_time_list = [Day_order[i][3] for i in feasible_route]
#        print len(l_time_list)
        cuttime_list = []
        for i,j in zip(node_service_time,node_arrive_time):
            if j < i:
                cuttime_list.append(i-j)
            else:
                cuttime_list.append(0)
#        print cuttime_list                
#        print len(cuttime_list)
        ri_time = 0
#        route_arrive_time = check_service_time(test)
        test_n = 0
        test_ancher = 0
        if test[0] == 0:
            for i in range(len(test)-1):
                test_n += test[i]
                if test_n == 0:
                    if test[i] != 0:

                        for j in range(test_ancher,i+1):
                            
                            if cuttime_list[j] > 0:
                                if j == test_ancher:
                                    node_arrive_time[test_ancher] = e_time_list[test_ancher] 
                                else:
                                    
                                    change_new_timesign = 0
#                                    print "1   ",change_new_timesign
                                    for l in range(test_ancher,j):
                                        new_service_time = node_service_time[l] + cuttime_list[j]
                                        
                                        if new_service_time >= e_time_list[l] and new_service_time <= l_time_list[l]:
                                            continue
                                        else:
                                            change_new_timesign += 1
#                                    print "2   ",change_new_timesign
                                            
                                    if change_new_timesign == 0:
#                                        print test_ancher,j
                                        for l in range(test_ancher,j):
                                            node_service_time[l] = node_service_time[l] + cuttime_list[j]   
                                            node_arrive_time[l] = node_arrive_time[l] + cuttime_list[j]   
                                            
                                        node_arrive_time[j] = e_time_list[j] 
                                    else:
#                                        print "NOOOO",test[j],cuttime_list[j]   
                                        left_time_list = [l_time_list[l]-node_arrive_time[l]for l in range(test_ancher,j)]
                                     
                                        min_left_time = min(left_time_list)
                                        for l in range(test_ancher,j):
#                                            print test[l],left_time_list[l-test_ancher]
                                            node_service_time[l] = node_service_time[l] + min_left_time
                                            node_arrive_time[l] = node_arrive_time[l] + min_left_time
                                        node_arrive_time[j] = node_arrive_time[j] + min_left_time                                               
                        
                    test_ancher = i+1
#        print "    ",node_service_time            
#        print "    ",node_arrive_time 
        cuttime_list = []
        for i,j in zip(node_service_time,node_arrive_time):
            if j < i:
                cuttime_list.append(i-j)
            else:
                cuttime_list.append(0)    
#        print cuttime_list                
        for i in range(len(test)):
    #        print i,test[i],test[i+1],t[Day_order[test[i]][1],Day_order[test[i+1]][1]]
            if type(test[i]) == int:
                test_n += test[i]
                if test[i] > 0:
                    test_target = test.index(-test[i])
    #                print test[i],-test[i]
                    ride_time =  node_service_time[test_target] - node_service_time[i]   
                    ri_time += ride_time
#        print node_service_time
        if out_type == "list":
            return node_service_time
        elif out_type == "arrive":
            return node_arrive_time
        else:
            return ri_time               
#%% sql cost
    ## make the time & distant cost matrix
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
    ## time cost matrix
    t = copy.deepcopy(cost_info)
    ## distant cost matrix
    d = copy.deepcopy(dist_info)
#%% sql request
    
    request_info = {} 
    unservable_requests = {}
    village_key = [request[0][1]]

    ## the dictionary includes every request in a day 
    Day_request_info = {}   
    Day_request_info[village_key[0]] = {}
    ## the dictionary of the information of every request 
    ## Day_order = {request_number:[request number,pick place, EPT, LPT, passenger number, deliver place, EDT, LDT]}
    ## Day_order[request_number] = [request number,pick place, EPT, LPT, passenger number, deliver place, EDT, LDT]
    Day_order = {}
    
    ## frame the time window
    for i in request:
        SENDORDER = i[3]
        ## if there are no pick windows        
#        if i[8] == None or i[9] == None:
        if True:
            Pp,Dp,n_C= i[5],i[6],i[7]
            
            LT = (time_form(i[10])+time_form(i[11]))/2.0
            
            EPT = LT - constant_a*t[Pp,Dp] - constant_b  
            EDT = LT -            t[Pp,Dp] - constant_b         
            LPT = time_form(i[10])
            LDT = time_form(i[11])
            
            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDT]
            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDT,n_C]            
            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDT]
#        ## if there are no deliver windows 
#        elif i[10] == None or i[11] == None:
#            
#            Pp,Dp,n_C= i[5],i[6],i[7]
#
#            EPT = time_form(i[8])
#            EDT = time_form(i[9])
#            LPT = EPT +            t[Pp,Dp] + constant_b
#            LDT = EPT + constant_a*t[Pp,Dp] + constant_b
#
#            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDT]
#            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDT,n_C]            
#            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDT]   
#        ## if both windows exist 
#        else:
#            Pp,Dp,n_C= i[5],i[6],i[7]
# 
#            EPT = time_form(i[8])
#            EDT = time_form(i[9])          
#            LPT = time_form(i[10])
#            LDT = time_form(i[11]) 
#            
#            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDT]
#            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDT,n_C]             
#            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDT]

        SENDORDER_date = "19000000"
        SENDORDER_date = str(SENDORDER_date[:4])+"/"+str(SENDORDER_date[4:6])+"/"+str(SENDORDER_date[6:])
        SENDORDER_ID = str(SENDORDER)
    
        for j in SENDORDER_ID:
            if int(j) !=0:
                SENDORDER_ID = int(SENDORDER_ID[SENDORDER_ID.index(j):])
                break
        ## build the day request dictionary 
        ## let us know which requests should be matched in the specific day
        request_info[SENDORDER_ID] = [SENDORDER_date]+temp_one[0:2]+[SENDORDER_ID]+temp_one[2:10]
        request_info_now = request_info[SENDORDER_ID]
#        if request_info_now[2] not in village_key:
#            village_key.append(request_info_now[2])
        
        if request_info_now[0] not in Day_request_info[village_key[0]].keys():
            Day_request_info[village_key[0]][request_info_now[0]] = {}
            Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
        else:
            if request_info_now[1] not in Day_request_info[request_info_now[2]][request_info_now[0]].keys():
                Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]] = []
                Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
            else:
                Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]].append(request_info_now[3])
#        print Day_request_info
#%% sql resource              
    resource_info = {}
    
    ## the dictionary of the car did not be used 
    unuse_resource_info = {}
    ## the dictionary of the car have been used 
    useed_resource_info = {}
    
    for i in resource:
        car_code = i[4]+'-'+str(resource.index(i)+1)
        start_time = time_form(i[6])
        close_time = time_form(i[7])   
        temp_resource = [car_code,i[0],i[1],i[2].strftime('%Y/%m/%d'),i[3],i[4],i[5],time_form(i[6]),time_form(i[7]),i[8]]
        ## pretend the driver's location as a day order 
        ## but it does not include in day request
        Day_order[car_code] = [car_code,i[9],start_time,close_time,0]
#        temp_carnumber = temp_resource[4]
#        
#        temp_village = temp_resource[3]
#        
#        temp_date = temp_resource[0]
        
        temp_carnumber = temp_resource[0]
        
#        temp_village = village_key[0]
        temp_village = temp_resource[4]
     
        temp_date = temp_resource[3]
        
        if temp_village not in unuse_resource_info.keys():
            unuse_resource_info[temp_village] = {}
            useed_resource_info[temp_village] = {}
        if  temp_date not in unuse_resource_info[temp_village].keys():
            unuse_resource_info[temp_village][temp_date] = [temp_carnumber]
            useed_resource_info[temp_village][temp_date] = {}
        else:
            unuse_resource_info[temp_village][temp_date].append(temp_carnumber)
        resource_info[temp_carnumber] = temp_resource      
#    print unuse_resource_info
#%% generate the initial route
    Day_request = copy.copy(Day_request_info)
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
#                    reserve_Plan[village][day][reser_Day] = final_route
                else:
                    final_route = regret_insert(unroute_Day_requests,village,reser_Day)
                reserve_Plan[village][day][reser_Day] = final_route
#%% show the initial result               
#    print "------initial result------"
#    for i in useed_resource_info[village][reser_Day]:
#        print useed_resource_info[village][reser_Day][i]                
#%% improvement the initial route            
    improvement = False

    if improvement == True:
#        print "+"
        for village in village_key:
            for reser_Day in useed_resource_info[village].keys(): 
                relocation_sign = True
                exchange_sign = True
                while True:
#                    
                ############## Trip relocation ##############                   
                    if relocation_sign == True:
#                        print "---relocation_operator---"   
                        old_plan = copy.copy(useed_resource_info[village][reser_Day])
                        new_plan = relocation_operator(useed_resource_info[village][reser_Day])
                        if old_plan != new_plan:
                            useed_resource_info[village][reser_Day] = new_plan
                        else:
                            relocation_sign = False   
#                        print "---relocation_operator---"                      
#                    
                ############## Trip exchange ##############                                       
                    if exchange_sign == True:
#                        print "---exchange_operator---"
                        old_plan = copy.copy(useed_resource_info[village][reser_Day])
                        new_plan = exchange_operator(useed_resource_info[village][reser_Day])
                        if old_plan != new_plan:
                            useed_resource_info[village][reser_Day] = new_plan
                        else:
                            exchange_sign = False  
#                        
                    if relocation_sign == False and exchange_sign ==  False:
                        break

#%% show the improved result                
    print "------improved result------"
    total_dist = 0
    for i in useed_resource_info[village][reser_Day]:
        print useed_resource_info[village][reser_Day][i],total_distant(useed_resource_info[village][reser_Day][i])
        total_dist += total_distant(useed_resource_info[village][reser_Day][i])
    print 'Total distance:', total_dist
#%% show the unservable result         
    print "------unservable result------"        
    print unservable_requests        
#%% waiting strategy & Fix TW      
    for village in village_key:
        for reser_Day in useed_resource_info[village].keys():  
            for route in useed_resource_info[village][reser_Day]:
#                    print useed_resource_info[village][reser_Day][route]
                fix_route = useed_resource_info[village][reser_Day][route]
#                if waiting_strategy == "drive_first":
#                    nodeservice_time =  check_service_time(fix_route,"list")     
#                elif waiting_strategy == "wait_first":
                nodeservice_time =  ride_counter(fix_route,"list")
                e_time_list = [Day_order[j][2] for j in fix_route]
                l_time_list = [Day_order[j][3] for j in fix_route] 
#                    print nodeservice_time
#                    print e_time_list
#                    print l_time_list
                for j,k,l,m in zip(e_time_list,nodeservice_time,l_time_list,fix_route):
                    if m != 0:
#                        print
#                        print m,Day_order[m][2],Day_order[m][3]
                        if round(j,2)+service_time/2.0 > round(k,2):
#                                print round(j,2),round(k,2),round(l,2),"up"
                            Day_order[m][3] = j + new_tw
                        elif round(l,2)-service_time/2.0 < round(k,2):
#                                print round(j,2),round(k,2),round(l,2),"down"
                            Day_order[m][2] = l - new_tw
                        else:
#                                print round(j,2),round(k,2),round(l,2),"+5-5"
                            Day_order[m][2] = k - new_tw/2                          
                            Day_order[m][3] = k + new_tw/2
#                        print m,Day_order[m][2],Day_order[m][3]
#%% calculate the trip & format the data 
#    result_start_time = time.time()
    total_num = 0
    for i in useed_resource_info[village][reser_Day]:
#        print useed_resource_info[village][reser_Day][i] 
        total_num += (len(useed_resource_info[village][reser_Day][i])-2)/2.0
#    print total_num                      
    result = []
    trip_number = 0
    trip_dist = dict.fromkeys(useed_resource_info.keys())
    trip_time = dict.fromkeys(useed_resource_info.keys())
#    print useed_resource_info.keys()
    for i in useed_resource_info.keys(): 
        temp_trip_dist = dict.fromkeys(useed_resource_info[i].keys(),[])
        temp_trip_time = dict.fromkeys(useed_resource_info[i].keys(),[])
        for j in sorted(useed_resource_info[i].keys()):    
            temp_trip_dist_list = []
            temp_trip_time_list = []
            for k in useed_resource_info[i][j]:
                
                test_route = useed_resource_info[i][j][k]        
#                temp_store_list = [] 
                
#                customer_sign = 0
                cal_sign = 0
                cal_anchor = 1
                trip_list = []
                trip_dict ={}
#                print test_route
                for cus in test_route :
                    
                    if type(cus) == int:

                        cal_sign += cus
                        if cal_sign == 0:
            #                print "     ---",temp_store_list[cal_anchor:feasible_route.index(i)+1]
                            cal_route = test_route[cal_anchor:test_route.index(cus)+1]
#                            print "cal_route",cal_route
                            trip_list.append(cal_route)
                            cal_anchor = test_route.index(cus)+1 
                run_sign = True
                start_sign = 0
                while run_sign == True:
                    if len(trip_list)>1:
                        take_time = (Day_order[trip_list[start_sign][-1]][3]+Day_order[trip_list[start_sign][-1]][2])/2
                        arive_time = (Day_order[trip_list[start_sign+1][0]][2]+Day_order[trip_list[start_sign+1][0]][3])/2                        
                        if arive_time - take_time > Max_trip_interval:
                            start_sign += 1
                        else:
                            test_trip = trip_list[start_sign] + trip_list[start_sign+1]
                            if total_distant(test_trip) > Max_mile:
                                start_sign += 1
                            else:
                                trip_list[start_sign] = test_trip
                                trip_list.remove(trip_list[start_sign+1])
                        if start_sign == len(trip_list)-1:
                            run_sign = False
                    else:
                        run_sign = False
#                print "---"                        
#                print trip_list      
#                print "---"
                p_new_trip = []
                up_order = {}
                down_order = {}   
                for m in trip_list:
                    
                    temp_trip_dist_list.append(total_distant(m))
                    temp_trip_time_list.append(total_time(m))
                    temp_p_new_trip = []
                    uporder = 0
                    downorder = 0                    
                    for l in m:
                        if l > 0:

                            temp_p_new_trip.append(l)
                            uporder += 1                            
                            up_order[l] = uporder
                        else:
                            downorder += 1                            
                            down_order[l] = downorder                            
                    p_new_trip.append(temp_p_new_trip)
#                print p_new_trip
                for m in range(len(p_new_trip)):
#                    print p_new_trip
                    trip_number += 1
                    for l in range(len(p_new_trip[m])):
#                        if p_new_trip[m][l] > 0:
                        trip_dict[p_new_trip[m][l]] = trip_number
                        sin_req = p_new_trip[m][l]
                        UP_order = up_order[sin_req]
                        DOWN_order = down_order[-sin_req]
                        
                        TAKE_TIME = str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2//60))+":"+str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2%60))
                        AVR_TIME = str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2//60))+":"+str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2%60))

                        TAKE_DATE = j[0:4]+"-"+j[5:7]+"-"+j[8:]
                        TAKE_DATE = datetime.datetime.strptime(TAKE_DATE, "%Y-%m-%d")
                        TAKE_TIME = datetime.datetime.strptime(TAKE_TIME, "%H:%M")
                        AVR_TIME = datetime.datetime.strptime(AVR_TIME, "%H:%M")
                        temp_result = [TAKE_DATE,i,sin_req,Day_order[sin_req][1],Day_order[sin_req][5],trip_number,"Vrp",UP_order,DOWN_order,resource_info[k][6],resource_info[k][5],TAKE_TIME,AVR_TIME]
#                        print "temp_result",temp_result
                        result.append(temp_result)    

            temp_trip_dist[j] = temp_trip_dist_list
            temp_trip_time[j] = temp_trip_time_list
        trip_dist[i] = temp_trip_dist
        trip_time[i] = temp_trip_time

    return useed_resource_info,result


#%% Data Input and Data Ouput
useed_resource,result = main_funtion(sql_request,sql_cost,sql_resource)

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
                                                 DOWN_ORDER,
                                                 DRIVER_NAME, 
                                                 CAR_NUMBER, 
                                                 TAKE_TIME, 
                                                 AVR_TIME)
                                                 
                                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""","None",result[i][0],result[i][1],result[i][2],result[i][3],result[i][4],result[i][5],result[i][6],result[i][7],result[i][8],result[i][9],result[i][10],result[i][11],result[i][12])

cursor.execute('SELECT * from VRP_HAS_MATCHED')
VRP_HAS_MATCHED = datafit(cursor,"pandas") 
cnxn.commit()
=======
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
#import pprint
#%% sql sever setting
#server = '' 
#database = '' 
#username = '' 
#password = '' 
#cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
server = '' 
database = '' 
username = '' 
password = ''
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
#%% parameter setting
Max_mile = 20 # upper limit for a ride
service_time = 5 # service time when  arrive locstion 
down_service_time = 1
time_window = 30 # aditional time windows
constant_a = 3
constant_b = 5
Max_trip_interval = 15 #minutes
new_tw = 5
Large_cost = 99999
#%% input three sql data sheet

## a funtion to transfer the form of data
## transfer into pandas or list 
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


## delete the data has been create and recalculate 
cursor = cnxn.cursor()
cursor.execute('delete from VRP_HAS_MATCHED') 
cnxn.commit()
 
#print "---sql_resource---"
cursor.execute("SELECT * from VRP_CAR_USEABLE ")
sql_resource = datafit(cursor,"list") 

#print ("---sql_cost---")
cursor.execute("SELECT * from VRP_TRAVEL_MATRIX_DATA ")
sql_cost = datafit(cursor,"list")

#print ("---sql_request---")
cursor.execute("SELECT * from VRP_PRE_ORDER")
sql_request = datafit(cursor,"list")

## if you want the data in a specific day
#cursor.execute("SELECT * from VRP_CAR_USEABLE where take_date ='2019/01/14'")
#cursor.execute("SELECT * from VRP_TRAVEL_MATRIX_DATA where take_date ='2019/01/14'")
#cursor.execute("SELECT * from VRP_PRE_ORDER where take_date ='2019/01/14'")

## if you want the data in a specific period
#cursor.execute("SELECT * from VRP_CAR_USEABLE where take_date between '2019/01/14' and '2019/01/18'")
#cursor.execute("SELECT * from VRP_TRAVEL_MATRIX_DATA where take_date between '2019/01/14' and '2019/01/18'")
#cursor.execute("SELECT * from VRP_PRE_ORDER where take_date between '2019/01/14' and '2019/01/18'")

#%% Main procedure 
def main_funtion(request,cost,resource): 
      
    ## a funtion to transfer the time format
    def time_form(intime):
        str_intime = str(intime)
        int_intime = int(str_intime[11])*10*60+int(str_intime[12])*60+int(str_intime[14])*10+int(str_intime[15])
        return int_intime 
    
    ## calculate the route time
    def total_time(route):
        tt_time = 0
        for c in range(len(route)-1):
            tt_time += t[Day_order[route[c]][1],Day_order[route[c+1]][1]]          
        return tt_time
    
    ## calculate the route distant
    def total_distant(route):
        tt_dist = 0
        for c in range(len(route)-1):
            tt_dist += d[Day_order[route[c]][1],Day_order[route[c+1]][1]]          
        return tt_dist
    
    ## give the route a start customer
    ## 
    def route_seed_initialer(unroute_list,village,Day):
        ## sort the unroute customers acordding to the pick up time
        now_unroute_list = []
        for i in unroute_list:
            now_unroute_list.append(Day_order[i])
        sort_now_unroute_list = sorted(now_unroute_list, key = lambda x : (x[2]))
        sort_unroute_list = []
        for i in sort_now_unroute_list:
            sort_unroute_list.append(i[0]) 
        ## sort the car drivers acordding to the starting service time    
        all_car_key_info = []
        for i in unuse_resource_info[village][Day]:
            all_car_key_info.append(resource_info[i])
        sort_all_car_key_info = sorted(all_car_key_info, key = lambda x : (x[-7]))
        sort_all_car_key = []
        for i in sort_all_car_key_info:
            sort_all_car_key.append(i[0])  
        ## give the route a start customer
        ## return the unroute list without the customerhave been matched
        new_unroute_list = copy.copy(sort_unroute_list)
        for j in sort_unroute_list:
            unservable_time = 0
            break_sign = 0
            for i in sort_all_car_key: #i就是車號
                current_routeA = [i,j,-j,i]
                if check_feasible_route(current_routeA,i) == 0: #輸入路徑與車號
                    break_sign += 1
                    useed_resource_info[village][Day][i] = [i,j,-j,i]   
                    new_unroute_list.remove(j)
                    unuse_resource_info[village][Day].remove(i)
                    break
                else:
                    unservable_time += 1
                    len(sort_all_car_key[sort_all_car_key.index(i):])
            if unservable_time == len(sort_all_car_key):
                if Day not in unservable_requests.keys():
                    unservable_requests[Day] = []
                    unservable_requests[Day].append(j)
                else:
                    unservable_requests[Day].append(j)
                new_unroute_list.remove(j)
            if break_sign>0:
                break
            #只要有一個人可以放進一台車就可以
#        print "in ",useed_resource_info[village][Day]
        return new_unroute_list    
    
    def route_seed_initialer2(unroute_list,village,Day):
#        print unroute_list,village,Day
        now_unroute_list = []
        for i in unroute_list:
            now_unroute_list.append(Day_order[i])
        sort_now_unroute_list = sorted(now_unroute_list, key = lambda x : (x[2]))
        sort_unroute_list = []
        for i in sort_now_unroute_list:
            sort_unroute_list.append(i[0])
        seed_list = copy.copy(sort_unroute_list)
        new_unroute_list = []
        for i in range(len(sort_unroute_list)-1):
            req_i = sort_unroute_list[i]
            req_i_1 = sort_unroute_list[i+1]
            LDTk = Day_order[req_i][7]
            TTDkPk_1 = t[Day_order[req_i][5],Day_order[req_i_1][1]]
            EPTk_1 = Day_order[req_i_1][2]
            if LDTk+TTDkPk_1<=EPTk_1:
                seed_list.remove(req_i_1)
                new_unroute_list.append(req_i_1)
        for i in unuse_resource_info[village][Day]:
            unservable_time = 0
            for j in seed_list: 
                current_routeA = [i,j,-j,i]
                if check_feasible_route(current_routeA,i) == 0:
                    useed_resource_info[village][Day][i] = [i,j,-j,i]
                    seed_list.remove(j)
                    break                  
                else:
                    unservable_time += 1
        for i in useed_resource_info[village][Day].keys():
            if i in unuse_resource_info[village][Day]:
                unuse_resource_info[village][Day].remove(i)
#        print "in ",useed_resource_info[village][Day]
        return new_unroute_list+seed_list  
   
    def check_feasible_route(feasible_route,car_number):
#        print feasible_route,car_number
        debug_time = Day_order[feasible_route[0]][2] ## first customer pick time 
        max_car_capacity = resource_info[car_number][-1] ## car capacity
  
        route_feasible_or_not = True
        ## check if the trip exceeds the max trip miles
        if route_feasible_or_not == True:
            temp_store_list = [] 
            cal_sign = 0
            cal_anchor = 0
            
            for i in feasible_route :
                if type(i) ==  int:
                    temp_store_list.append(i)
                    if i not in temp_store_list or -i not in temp_store_list:        
                        cal_sign += 1
                    elif i < 0 and -i in temp_store_list:
                        cal_sign -= 1
                    if cal_sign == 0:
                        cal_route = temp_store_list[cal_anchor:feasible_route.index(i)+1]
#                        print cal_anchor,feasible_route.index(i)+1
                        o_dist = total_distant(cal_route)
#                        for test_c in range(len(cal_route)-1):
#                            o_dist += d[Day_order[cal_route[test_c]][1],Day_order[cal_route[test_c+1]][1]]         
                        
                        if o_dist >= Max_mile:
                            route_feasible_or_not = False 
#                        else:
#                            print cal_route,car_number,total_distant(cal_route)
                            
                        cal_anchor = feasible_route.index(i)+1 
        ## check if the capacity exceeds the car limit               
        passenger_in_car = 0 
        if route_feasible_or_not == True: 
            for x in feasible_route:
                if x > 0 :
                    passenger_in_car += Day_order[x][4] 
                elif x <0:
                    passenger_in_car -= Day_order[x][4]
                if passenger_in_car > max_car_capacity:

                    route_feasible_or_not = False
                    break
                
        ## check the route time window  
        debug_route_time = []
        debug_real_time = []    
        if route_feasible_or_not == True: 
            for i in range(len(feasible_route)):
                pre_node = Day_order[feasible_route[i-1]][1]            
                now_node = Day_order[feasible_route[i]][1]
    
                e_time = Day_order[feasible_route[i]][2] #early最早上車
                l_time = Day_order[feasible_route[i]][3] #latest 最晚上車
    
                if i == 0:
                    debug_route_time.append(debug_time)
                    debug_real_time.append(debug_time)
                    next_node = Day_order[feasible_route[i+1]][1]
                    if now_node == next_node:
                        continue
                    else:
                        if feasible_route[i] < 0:
#                            print feasible_route[i-1]
                            debug_time += down_service_time
#                            debug_time += service_time 
                        else:    
                            debug_time += service_time                   
                elif i == len(feasible_route)-1:    
                    debug_time = debug_time+t[pre_node,now_node]
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                elif i > 0:
#                    print pre_node,now_node
                    debug_time = max([debug_time+t[pre_node,now_node],e_time])
                    debug_route_time.append(debug_time)
                    debug_real_time.append(l_time)
                    next_node = Day_order[feasible_route[i+1]][1]
                    if now_node == next_node:
                        continue
                    else:
                        if feasible_route[i] < 0:
                            debug_time += down_service_time   
                        else:    
                            debug_time += service_time
            for i,j in zip(debug_route_time,debug_real_time):
                if  i > j:
#                    print i,j
#                    debug1 = 1
                    route_feasible_or_not = False                    

        if route_feasible_or_not == True:  
            debug_signal = 0
        else:
            debug_signal = 1
#        if 14410 in feasible_route:
#            print feasible_route,car_number,route_feasible_or_not
           
        return debug_signal

    def regret_insert(unroute_list,village,Day):
#        print "unroute_list",unroute_list,village,Day
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
#            print "----"
            for customer in unroute_list:
#                print customer
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
                    for p_place in range(1,len(o_route)+1):         
                        test_p_route =  copy.copy(o_route)
                        test_p_route.insert(p_place,customer_p)
#                        print
#                        print "test_p_route-----------",test_p_route                        
#                        feasibility1 = check_feasible_route(test_p_route,car_number)
#                        print "-----------feasibility1",feasibility1
                        feasibility1 = 0
                        if feasibility1 == 0:
                            for d_place in range(p_place+1,len(test_p_route)):
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
#                                    tt_dist = total_distant(test_d_route)
#                                    print test_d_route
#                                    for test_c in range(len(test_d_route)-1):
##                                        print test_d_route[test_c],test_d_route[test_c+1],d[Day_order[test_d_route[test_c]][1],Day_order[test_d_route[test_c+1]][1]]
#                                        tt_dist += d[Day_order[test_d_route[test_c]][1],Day_order[test_d_route[test_c+1]][1]]
#                                    c1 = tt_dist-o_route_tt_dist
                                    c1 = total_distant(test_d_route)
#                                    print test_d_route,c1
                                    ##################################################################
                                    c1_value.append(c1)
                                    c1_place.append([p_place,d_place])
                                
                    min_c1_route.append(o_route)  
#                    print c1_value
                    if len(c1_value) > 0:
                        min_value = min(c1_value)
                        min_place = c1_place[c1_value.index(min_value)]                           
                        min_c1_value.append(min_value)
                        min_c1_place.append(min_place)
                    else:                
                        min_c1_value.append(Large_cost)
                        min_c1_place.append([-Large_cost,-Large_cost])     
#                print "min_c1_value",min_c1_value
                min_min_c1_value = min(min_c1_value)
                min_c1_index = min_c1_value.index(min_min_c1_value)
                min_min_c1_place = min_c1_place[min_c1_index]
                min_min_c1_route = min_c1_route[min_c1_index]
                c2_customer.append([customer,-customer])
#                print c2_customer
                c2 = 0
                if min_c1_value.count(Large_cost) != len(min_c1_value):
#                    print min_c1_value
                    for mmc in range(len(min_c1_value)):
#                        print min_c1_route[mmc],min_min_c1_route
#                        if min_c1_route[mmc] != min_min_c1_route:
                            
                        c2 += min_c1_value[mmc] - min_min_c1_value
#                        print "------------",c2
                else:
                    c2 = -Large_cost
                c2_value.append(c2)
                c2_route.append(min_min_c1_route)
                c2_place.append(min_min_c1_place)  
#                print c2_value,c2_route,c2_place
#            print c2_value  
            if c2_value.count(-Large_cost) != len(c2_value):
#                print "1111111111111"
                max_c2_value = max(c2_value)
#                print max_c2_value
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
#                print "----",Day,unroute_list
#                unservable_requests[Day] = unroute_list ##route2
#                break
                unroute_list = route_seed_initialer(unroute_list,village,Day)
                
        return current_list
    
    def relocation_operator(original_plan):
        all_reinsert_info = {}
        for i in original_plan:
            for j in original_plan[i]:
                if j > 0 :
                    all_reinsert_info[j] = i 
        all_route = original_plan.keys()
        
        relocation_for_remove_time = 0
        relocation_for_insert_time = 0
        for relocate_time in range(1):
            for i in all_reinsert_info:
                
                relocation_for_remove_start_time = time.time()
                car_c = all_reinsert_info[i]
                remoeve_route_c = original_plan[car_c][:]
                if type(i) == int:
                    remoeve_route_c.remove(i)
                    remoeve_route_c.remove(-i)
                    relocation_for_remove_end_time = time.time()
                    relocation_for_remove_time += (relocation_for_remove_end_time-relocation_for_remove_start_time)
                    for l in all_route:
                        if l != car_c:
                            for m in range(1,len(original_plan[l])+1):
                                for n in range(m+1,len(original_plan[l])+1):
                                    if i in original_plan[car_c]:  
                                        relocation_for_insert_start_time = time.time()
                                        insert__route_c = original_plan[l][:]
                                        insert__route_c.insert(m,i)
                                        insert__route_c.insert(n,-i)
                                        relocation_for_insert_end_time = time.time()
                                        relocation_for_insert_time += (relocation_for_insert_end_time-relocation_for_insert_start_time)
        #                                print insert__route_c,check_feasible_route(insert__route_c,l)
                                        if check_feasible_route(insert__route_c,l) == 0:
        #                                    print insert__route_c,check_feasible_route(insert__route_c,l)
                                            if total_distant(original_plan[car_c])+total_distant(original_plan[l])-total_distant(remoeve_route_c)-total_distant(insert__route_c) > 0:
#                                                print total_distant(original_plan[car_c])+total_distant(original_plan[l])-total_distant(remoeve_route_c)-total_distant(insert__route_c) 
                                                original_plan[car_c] = remoeve_route_c
                                                original_plan[l] = insert__route_c
                                                all_reinsert_info[i] = l   
                                            if len(remoeve_route_c) == 0 or len(insert__route_c) == 0 :
                                                print "need to cut car"                                            
                                    else:
                                        break 
        return original_plan
    def exchange_operator(original_plan):
        all_reinsert_info = {}
        for i in original_plan:
#            print i,original_plan[i]
            for j in original_plan[i]:
#                print j
                if j > 0 and type(j) == int:
                    all_reinsert_info[j] = i
        exchange_first_insert = 0
        exchange_second_insert = 0
    #    exchange_start_time = time.time()
        for exchange_time in range(1):
            for i in all_reinsert_info:
                for j in all_reinsert_info:
                    car_r = all_reinsert_info[i]
                    car_s = all_reinsert_info[j]
                    if i != j and car_r != car_s:
            #            print 
            #            print Day_order[i],Day_order[j]
                        EPTi = Day_order[i][2]
                        LPTi = Day_order[i][3]
                        EDTi = Day_order[i][6]
                        LDTi = Day_order[i][7]       
                        EPTj = Day_order[j][2]
                        LPTj = Day_order[j][3]
                        EDTj = Day_order[j][6]
                        LDTj = Day_order[j][7]           
                        if (EPTi <= LPTj and EPTj <= LPTi) or (EDTi <= LDTj and EDTj <= LDTi):                    
       
                            remoeve_route_r = original_plan[car_r][:]
                            remoeve_route_r.remove(i)
                            remoeve_route_r.remove(-i)
                            
                            best_insert_route_r = []
                            exchange_first_start_insert = time.time()
                            for m in range(1,len(remoeve_route_r)+1):
                                for n in range(m+1,len(remoeve_route_r)+1):
    #                                print m,n
                                    insert_route_r = remoeve_route_r[:]
    #                                insert_route_r = copy.deepcopy(remoeve_route_r)
                                    insert_route_r.insert(m,j)
                                    insert_route_r.insert(n,-j)
    #                                print insert_route_r,check_feasible_route(insert_route_r,car_r)
                                    if check_feasible_route(insert_route_r,car_r) == 0:
                                        if len(best_insert_route_r) == 0:
                                            best_insert_route_r = insert_route_r
                                        else:
                                            if total_distant(insert_route_r) < total_distant(best_insert_route_r):
                                                best_insert_route_r = insert_route_r
            
                            exchange_first_end_insert = time.time()            
                            exchange_first_insert += (exchange_first_end_insert-exchange_first_start_insert)    
                            if len(best_insert_route_r) > 0 :        
                                remoeve_route_s = original_plan[car_s][:]
                                remoeve_route_s.remove(j)
                                remoeve_route_s.remove(-j) 
                                exchange_second_start_insert = time.time()
                                best_insert_route_s = []
                                for m in range(1,len(remoeve_route_s)+1):
                                    for n in range(m+1,len(remoeve_route_s)+1):
                                        insert_route_s = remoeve_route_s[:]
                                        insert_route_s.insert(m,i)
                                        insert_route_s.insert(n,-i)                
                                        if check_feasible_route(insert_route_s,car_s) == 0:
                #                            print "-------------------"
                                            if len(best_insert_route_s) == 0:
                                                best_insert_route_s = insert_route_s
                                            else:
                                                if total_distant(insert_route_s) < total_distant(best_insert_route_s):
                                                    best_insert_route_s = insert_route_s
                                exchange_second_end_insert = time.time()
                                exchange_second_insert += (exchange_second_end_insert-exchange_second_start_insert)
                                if len(best_insert_route_s) > 0:
                                    if (total_distant(original_plan[car_r])+total_distant(original_plan[car_s]))-(total_distant(best_insert_route_r)+total_distant(best_insert_route_s))>0:
#                                        print (total_distant(original_plan[car_r])+total_distant(original_plan[car_s]))-(total_distant(best_insert_route_r)+total_distant(best_insert_route_s))
                                        original_plan[car_r] = best_insert_route_r                 
                                        original_plan[car_s] = best_insert_route_s
                                        all_reinsert_info[i] = car_s
                                        all_reinsert_info[j] = car_r  
                                        if len(best_insert_route_r) == 0 or len(best_insert_route_s) == 0 :
                                            print "need to cut car"
        return original_plan   


    def check_service_time(feasible_route,out_type = None):
#        print feasible_route
        debug_time = Day_order[feasible_route[0]][2]
#        print debug_time
        debug_service_time = []   
        for i in range(len(feasible_route)):
            pre_node = Day_order[feasible_route[i-1]][1]            
            now_node = Day_order[feasible_route[i]][1]

            e_time = Day_order[feasible_route[i]][2]
#            l_time = Day_order[feasible_route[i]][3]
            if i == 0:
                debug_service_time.append(debug_time)
            elif i == len(feasible_route)-1:        
                debug_time = debug_time+t[pre_node,now_node]
                debug_service_time.append(debug_time)
            else:
                debug_time = max([debug_time+t[pre_node,now_node],e_time])
                debug_service_time.append(debug_time)
                if now_node > 0:
                    debug_time += service_time
#                print "afterser:",debug_time
        ri_time = 0
        test_n = 0                    
        for i in range(len(feasible_route)):
    #        print i,test[i],test[i+1],t[Day_order[test[i]][1],Day_order[test[i+1]][1]]
            if type(feasible_route[i]) == int:
                test_n += feasible_route[i]
                if feasible_route[i] > 0:
                    test_target = feasible_route.index(-feasible_route[i])
                    
                    ride_time =  debug_service_time[test_target] - debug_service_time[i]   
                    ri_time += ride_time
        if out_type == "list":
            return debug_service_time
        else:
            return ri_time         

    def check_arrive_time(feasible_route,out_type = None):
#        print feasible_route
        debug_time = Day_order[feasible_route[0]][2]
#        print debug_time
        debug_arrive_time = []   
        for i in range(len(feasible_route)):
            pre_node = Day_order[feasible_route[i-1]][1]            
            now_node = Day_order[feasible_route[i]][1]

            e_time = Day_order[feasible_route[i]][2]
#            l_time = Day_order[feasible_route[i]][3]
            if i == 0:
                debug_arrive_time.append(debug_time)
            elif i == len(feasible_route)-1:        
                debug_time = debug_time+t[pre_node,now_node]
                debug_arrive_time.append(debug_time)
            else:
                debug_arrive_time.append(debug_time+t[pre_node,now_node])
                debug_time = max([debug_time+t[pre_node,now_node],e_time])
                
                if now_node > 0:
                    debug_time += service_time
#                print "afterser:",debug_time
        ri_time = 0
        test_n = 0  
                          
        for i in range(len(feasible_route)):
    #        print i,test[i],test[i+1],t[Day_order[test[i]][1],Day_order[test[i+1]][1]]
            if type(feasible_route[i]) == int:
                test_n += feasible_route[i]
                if feasible_route[i] > 0:
                    test_target = feasible_route.index(-feasible_route[i])
                    ride_time =  debug_arrive_time[test_target] - debug_arrive_time[i]   
                    ri_time += ride_time
#        print debug_arrive_time                
        if out_type == "list":
            return debug_arrive_time
        else:
            return ri_time                     
    def ride_counter(feasible_route,out_type = None):
#        print "    ",feasible_route
#        print "debug_time",debug_time
        node_service_time = check_service_time(feasible_route,"list")
        node_arrive_time = check_arrive_time(feasible_route,"list")
        ##########################
        test = feasible_route
        
        e_time_list = [Day_order[i][2] for i in feasible_route]
        l_time_list = [Day_order[i][3] for i in feasible_route]
#        print len(l_time_list)
        cuttime_list = []
        for i,j in zip(node_service_time,node_arrive_time):
            if j < i:
                cuttime_list.append(i-j)
            else:
                cuttime_list.append(0)
#        print cuttime_list                
#        print len(cuttime_list)
        ri_time = 0
#        route_arrive_time = check_service_time(test)
        test_n = 0
        test_ancher = 0
        if test[0] == 0:
            for i in range(len(test)-1):
                test_n += test[i]
                if test_n == 0:
                    if test[i] != 0:

                        for j in range(test_ancher,i+1):
                            
                            if cuttime_list[j] > 0:
                                if j == test_ancher:
                                    node_arrive_time[test_ancher] = e_time_list[test_ancher] 
                                else:
                                    
                                    change_new_timesign = 0
#                                    print "1   ",change_new_timesign
                                    for l in range(test_ancher,j):
                                        new_service_time = node_service_time[l] + cuttime_list[j]
                                        
                                        if new_service_time >= e_time_list[l] and new_service_time <= l_time_list[l]:
                                            continue
                                        else:
                                            change_new_timesign += 1
#                                    print "2   ",change_new_timesign
                                            
                                    if change_new_timesign == 0:
#                                        print test_ancher,j
                                        for l in range(test_ancher,j):
                                            node_service_time[l] = node_service_time[l] + cuttime_list[j]   
                                            node_arrive_time[l] = node_arrive_time[l] + cuttime_list[j]   
                                            
                                        node_arrive_time[j] = e_time_list[j] 
                                    else:
#                                        print "NOOOO",test[j],cuttime_list[j]   
                                        left_time_list = [l_time_list[l]-node_arrive_time[l]for l in range(test_ancher,j)]
                                     
                                        min_left_time = min(left_time_list)
                                        for l in range(test_ancher,j):
#                                            print test[l],left_time_list[l-test_ancher]
                                            node_service_time[l] = node_service_time[l] + min_left_time
                                            node_arrive_time[l] = node_arrive_time[l] + min_left_time
                                        node_arrive_time[j] = node_arrive_time[j] + min_left_time                                               
                        
                    test_ancher = i+1
#        print "    ",node_service_time            
#        print "    ",node_arrive_time 
        cuttime_list = []
        for i,j in zip(node_service_time,node_arrive_time):
            if j < i:
                cuttime_list.append(i-j)
            else:
                cuttime_list.append(0)    
#        print cuttime_list                
        for i in range(len(test)):
    #        print i,test[i],test[i+1],t[Day_order[test[i]][1],Day_order[test[i+1]][1]]
            if type(test[i]) == int:
                test_n += test[i]
                if test[i] > 0:
                    test_target = test.index(-test[i])
    #                print test[i],-test[i]
                    ride_time =  node_service_time[test_target] - node_service_time[i]   
                    ri_time += ride_time
#        print node_service_time
        if out_type == "list":
            return node_service_time
        elif out_type == "arrive":
            return node_arrive_time
        else:
            return ri_time               
#%% sql cost
    ## make the time & distant cost matrix
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
    ## time cost matrix
    t = copy.deepcopy(cost_info)
    ## distant cost matrix
    d = copy.deepcopy(dist_info)
#%% sql request
    
    request_info = {} 
    unservable_requests = {}
    village_key = [request[0][1]]

    ## the dictionary includes every request in a day 
    Day_request_info = {}   
    Day_request_info[village_key[0]] = {}
    ## the dictionary of the information of every request 
    ## Day_order = {request_number:[request number,pick place, EPT, LPT, passenger number, deliver place, EDT, LDT]}
    ## Day_order[request_number] = [request number,pick place, EPT, LPT, passenger number, deliver place, EDT, LDT]
    Day_order = {}
    
    ## frame the time window
    for i in request:
        SENDORDER = i[3]
        ## if there are no pick windows        
#        if i[8] == None or i[9] == None:
        if True:
            Pp,Dp,n_C= i[5],i[6],i[7]
            
            LT = (time_form(i[10])+time_form(i[11]))/2.0
            
            EPT = LT - constant_a*t[Pp,Dp] - constant_b  
            EDT = LT -            t[Pp,Dp] - constant_b         
            LPT = time_form(i[10])
            LDT = time_form(i[11])
            
            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDT]
            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDT,n_C]            
            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDT]
#        ## if there are no deliver windows 
#        elif i[10] == None or i[11] == None:
#            
#            Pp,Dp,n_C= i[5],i[6],i[7]
#
#            EPT = time_form(i[8])
#            EDT = time_form(i[9])
#            LPT = EPT +            t[Pp,Dp] + constant_b
#            LDT = EPT + constant_a*t[Pp,Dp] + constant_b
#
#            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDT]
#            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDT,n_C]            
#            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDT]   
#        ## if both windows exist 
#        else:
#            Pp,Dp,n_C= i[5],i[6],i[7]
# 
#            EPT = time_form(i[8])
#            EDT = time_form(i[9])          
#            LPT = time_form(i[10])
#            LDT = time_form(i[11]) 
#            
#            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDT]
#            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDT,n_C]             
#            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDT]

        SENDORDER_date = "19000000"
        SENDORDER_date = str(SENDORDER_date[:4])+"/"+str(SENDORDER_date[4:6])+"/"+str(SENDORDER_date[6:])
        SENDORDER_ID = str(SENDORDER)
    
        for j in SENDORDER_ID:
            if int(j) !=0:
                SENDORDER_ID = int(SENDORDER_ID[SENDORDER_ID.index(j):])
                break
        ## build the day request dictionary 
        ## let us know which requests should be matched in the specific day
        request_info[SENDORDER_ID] = [SENDORDER_date]+temp_one[0:2]+[SENDORDER_ID]+temp_one[2:10]
        request_info_now = request_info[SENDORDER_ID]
#        if request_info_now[2] not in village_key:
#            village_key.append(request_info_now[2])
        
        if request_info_now[0] not in Day_request_info[village_key[0]].keys():
            Day_request_info[village_key[0]][request_info_now[0]] = {}
            Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
        else:
            if request_info_now[1] not in Day_request_info[request_info_now[2]][request_info_now[0]].keys():
                Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]] = []
                Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
            else:
                Day_request_info[village_key[0]][request_info_now[0]][request_info_now[1]].append(request_info_now[3])
#        print Day_request_info
#%% sql resource              
    resource_info = {}
    
    ## the dictionary of the car did not be used 
    unuse_resource_info = {}
    ## the dictionary of the car have been used 
    useed_resource_info = {}
    
    for i in resource:
        car_code = i[4]+'-'+str(resource.index(i)+1)
        start_time = time_form(i[6])
        close_time = time_form(i[7])   
        temp_resource = [car_code,i[0],i[1],i[2].strftime('%Y/%m/%d'),i[3],i[4],i[5],time_form(i[6]),time_form(i[7]),i[8]]
        ## pretend the driver's location as a day order 
        ## but it does not include in day request
        Day_order[car_code] = [car_code,i[9],start_time,close_time,0]
#        temp_carnumber = temp_resource[4]
#        
#        temp_village = temp_resource[3]
#        
#        temp_date = temp_resource[0]
        
        temp_carnumber = temp_resource[0]
        
#        temp_village = village_key[0]
        temp_village = temp_resource[4]
     
        temp_date = temp_resource[3]
        
        if temp_village not in unuse_resource_info.keys():
            unuse_resource_info[temp_village] = {}
            useed_resource_info[temp_village] = {}
        if  temp_date not in unuse_resource_info[temp_village].keys():
            unuse_resource_info[temp_village][temp_date] = [temp_carnumber]
            useed_resource_info[temp_village][temp_date] = {}
        else:
            unuse_resource_info[temp_village][temp_date].append(temp_carnumber)
        resource_info[temp_carnumber] = temp_resource      
#    print unuse_resource_info
#%% generate the initial route
    Day_request = copy.copy(Day_request_info)
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
#                    reserve_Plan[village][day][reser_Day] = final_route
                else:
                    final_route = regret_insert(unroute_Day_requests,village,reser_Day)
                reserve_Plan[village][day][reser_Day] = final_route
#%% show the initial result               
#    print "------initial result------"
#    for i in useed_resource_info[village][reser_Day]:
#        print useed_resource_info[village][reser_Day][i]                
#%% improvement the initial route            
    improvement = False

    if improvement == True:
#        print "+"
        for village in village_key:
            for reser_Day in useed_resource_info[village].keys(): 
                relocation_sign = True
                exchange_sign = True
                while True:
#                    
                ############## Trip relocation ##############                   
                    if relocation_sign == True:
#                        print "---relocation_operator---"   
                        old_plan = copy.copy(useed_resource_info[village][reser_Day])
                        new_plan = relocation_operator(useed_resource_info[village][reser_Day])
                        if old_plan != new_plan:
                            useed_resource_info[village][reser_Day] = new_plan
                        else:
                            relocation_sign = False   
#                        print "---relocation_operator---"                      
#                    
                ############## Trip exchange ##############                                       
                    if exchange_sign == True:
#                        print "---exchange_operator---"
                        old_plan = copy.copy(useed_resource_info[village][reser_Day])
                        new_plan = exchange_operator(useed_resource_info[village][reser_Day])
                        if old_plan != new_plan:
                            useed_resource_info[village][reser_Day] = new_plan
                        else:
                            exchange_sign = False  
#                        
                    if relocation_sign == False and exchange_sign ==  False:
                        break

#%% show the improved result                
    print "------improved result------"
    total_dist = 0
    for i in useed_resource_info[village][reser_Day]:
        print useed_resource_info[village][reser_Day][i],total_distant(useed_resource_info[village][reser_Day][i])
        total_dist += total_distant(useed_resource_info[village][reser_Day][i])
    print 'Total distance:', total_dist
#%% show the unservable result         
    print "------unservable result------"        
    print unservable_requests        
#%% waiting strategy & Fix TW      
    for village in village_key:
        for reser_Day in useed_resource_info[village].keys():  
            for route in useed_resource_info[village][reser_Day]:
#                    print useed_resource_info[village][reser_Day][route]
                fix_route = useed_resource_info[village][reser_Day][route]
#                if waiting_strategy == "drive_first":
#                    nodeservice_time =  check_service_time(fix_route,"list")     
#                elif waiting_strategy == "wait_first":
                nodeservice_time =  ride_counter(fix_route,"list")
                e_time_list = [Day_order[j][2] for j in fix_route]
                l_time_list = [Day_order[j][3] for j in fix_route] 
#                    print nodeservice_time
#                    print e_time_list
#                    print l_time_list
                for j,k,l,m in zip(e_time_list,nodeservice_time,l_time_list,fix_route):
                    if m != 0:
#                        print
#                        print m,Day_order[m][2],Day_order[m][3]
                        if round(j,2)+service_time/2.0 > round(k,2):
#                                print round(j,2),round(k,2),round(l,2),"up"
                            Day_order[m][3] = j + new_tw
                        elif round(l,2)-service_time/2.0 < round(k,2):
#                                print round(j,2),round(k,2),round(l,2),"down"
                            Day_order[m][2] = l - new_tw
                        else:
#                                print round(j,2),round(k,2),round(l,2),"+5-5"
                            Day_order[m][2] = k - new_tw/2                          
                            Day_order[m][3] = k + new_tw/2
#                        print m,Day_order[m][2],Day_order[m][3]
#%% calculate the trip & format the data 
#    result_start_time = time.time()
    total_num = 0
    for i in useed_resource_info[village][reser_Day]:
#        print useed_resource_info[village][reser_Day][i] 
        total_num += (len(useed_resource_info[village][reser_Day][i])-2)/2.0
#    print total_num                      
    result = []
    trip_number = 0
    trip_dist = dict.fromkeys(useed_resource_info.keys())
    trip_time = dict.fromkeys(useed_resource_info.keys())
#    print useed_resource_info.keys()
    for i in useed_resource_info.keys(): 
        temp_trip_dist = dict.fromkeys(useed_resource_info[i].keys(),[])
        temp_trip_time = dict.fromkeys(useed_resource_info[i].keys(),[])
        for j in sorted(useed_resource_info[i].keys()):    
            temp_trip_dist_list = []
            temp_trip_time_list = []
            for k in useed_resource_info[i][j]:
                
                test_route = useed_resource_info[i][j][k]        
#                temp_store_list = [] 
                
#                customer_sign = 0
                cal_sign = 0
                cal_anchor = 1
                trip_list = []
                trip_dict ={}
#                print test_route
                for cus in test_route :
                    
                    if type(cus) == int:

                        cal_sign += cus
                        if cal_sign == 0:
            #                print "     ---",temp_store_list[cal_anchor:feasible_route.index(i)+1]
                            cal_route = test_route[cal_anchor:test_route.index(cus)+1]
#                            print "cal_route",cal_route
                            trip_list.append(cal_route)
                            cal_anchor = test_route.index(cus)+1 
                run_sign = True
                start_sign = 0
                while run_sign == True:
                    if len(trip_list)>1:
                        take_time = (Day_order[trip_list[start_sign][-1]][3]+Day_order[trip_list[start_sign][-1]][2])/2
                        arive_time = (Day_order[trip_list[start_sign+1][0]][2]+Day_order[trip_list[start_sign+1][0]][3])/2                        
                        if arive_time - take_time > Max_trip_interval:
                            start_sign += 1
                        else:
                            test_trip = trip_list[start_sign] + trip_list[start_sign+1]
                            if total_distant(test_trip) > Max_mile:
                                start_sign += 1
                            else:
                                trip_list[start_sign] = test_trip
                                trip_list.remove(trip_list[start_sign+1])
                        if start_sign == len(trip_list)-1:
                            run_sign = False
                    else:
                        run_sign = False
#                print "---"                        
#                print trip_list      
#                print "---"
                p_new_trip = []
                up_order = {}
                down_order = {}   
                for m in trip_list:
                    
                    temp_trip_dist_list.append(total_distant(m))
                    temp_trip_time_list.append(total_time(m))
                    temp_p_new_trip = []
                    uporder = 0
                    downorder = 0                    
                    for l in m:
                        if l > 0:

                            temp_p_new_trip.append(l)
                            uporder += 1                            
                            up_order[l] = uporder
                        else:
                            downorder += 1                            
                            down_order[l] = downorder                            
                    p_new_trip.append(temp_p_new_trip)
#                print p_new_trip
                for m in range(len(p_new_trip)):
#                    print p_new_trip
                    trip_number += 1
                    for l in range(len(p_new_trip[m])):
#                        if p_new_trip[m][l] > 0:
                        trip_dict[p_new_trip[m][l]] = trip_number
                        sin_req = p_new_trip[m][l]
                        UP_order = up_order[sin_req]
                        DOWN_order = down_order[-sin_req]
                        
                        TAKE_TIME = str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2//60))+":"+str(int((Day_order[sin_req][2]+Day_order[sin_req][3])/2%60))
                        AVR_TIME = str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2//60))+":"+str(int((Day_order[sin_req][6]+Day_order[sin_req][7])/2%60))

                        TAKE_DATE = j[0:4]+"-"+j[5:7]+"-"+j[8:]
                        TAKE_DATE = datetime.datetime.strptime(TAKE_DATE, "%Y-%m-%d")
                        TAKE_TIME = datetime.datetime.strptime(TAKE_TIME, "%H:%M")
                        AVR_TIME = datetime.datetime.strptime(AVR_TIME, "%H:%M")
                        temp_result = [TAKE_DATE,i,sin_req,Day_order[sin_req][1],Day_order[sin_req][5],trip_number,"Vrp",UP_order,DOWN_order,resource_info[k][6],resource_info[k][5],TAKE_TIME,AVR_TIME]
#                        print "temp_result",temp_result
                        result.append(temp_result)    

            temp_trip_dist[j] = temp_trip_dist_list
            temp_trip_time[j] = temp_trip_time_list
        trip_dist[i] = temp_trip_dist
        trip_time[i] = temp_trip_time

    return useed_resource_info,result


#%% Data Input and Data Ouput
useed_resource,result = main_funtion(sql_request,sql_cost,sql_resource)

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
                                                 DOWN_ORDER,
                                                 DRIVER_NAME, 
                                                 CAR_NUMBER, 
                                                 TAKE_TIME, 
                                                 AVR_TIME)
                                                 
                                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""","None",result[i][0],result[i][1],result[i][2],result[i][3],result[i][4],result[i][5],result[i][6],result[i][7],result[i][8],result[i][9],result[i][10],result[i][11],result[i][12])

cursor.execute('SELECT * from VRP_HAS_MATCHED')
VRP_HAS_MATCHED = datafit(cursor,"pandas") 
cnxn.commit()
>>>>>>> 7d8691cfa8529e4d1afe9dc681dedcadbe9f4fc3
