# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 17:09:12 2019

@author: Kuan
"""
import numpy as np
import math
import copy
import time
import os

def test_exp(file_name,heuristic,seed,a,b,insert_type,unknown_rate,arrive_time = None,improvement = None,waiting_time = None,waiting_strategy = None,dynamic = None):
  
#    print seed,type(seed),heuristic,type(heuristic)
    def dist(x1,x2,y1,y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5   
    new_tw = 10
    service_time = 10
    np.random.seed(seed)
    #####################################################

    f = open(file_name,'r')
    txt_read = []
    for line in f.readlines():
        line = line.split()
        for i in range(len(line)):
            line[i] = float(line[i])
        txt_read.append(line)
        
    txt_basic = txt_read[0]
    txt_depot = txt_read[1]
    fleet_n = int(txt_basic[0])
    people_n = int(txt_basic[1])
    
    max_route_duration = txt_basic[2]
    max_ride_time  = 99999999999999999
#    print file_name[:5],",",people_n,",",int(max_route_duration),",",int(txt_basic[3]),","
#    print "max_route_duration,max_ride_time",max_route_duration,max_ride_time
    txt_requst = txt_read[2:]
    txt_xy = []
    txt_xy.append([0]+txt_depot[1:3])
    for i in txt_requst:

        if int(i[0]) <= txt_basic[1]:    
            txt_p_name = int(i[0])
            txt_d_name = int(txt_p_name + txt_basic[1])-1            
            txt_xy.append([txt_p_name]+i[1:3])
            txt_xy.append([txt_d_name]+txt_requst[txt_d_name][1:3])
    t = {}
    d = {}
   
    for i in range(len(txt_xy)):
        for j in range(i,len(txt_xy)):
#            print txt_xy[i],txt_xy[j]
            t[txt_xy[i][0],txt_xy[j][0]] = dist(txt_xy[i][1],txt_xy[j][1],txt_xy[i][2],txt_xy[j][2])
            d[txt_xy[i][0],txt_xy[j][0]] = dist(txt_xy[i][1],txt_xy[j][1],txt_xy[i][2],txt_xy[j][2])
            t[txt_xy[j][0],txt_xy[i][0]] = t[txt_xy[i][0],txt_xy[j][0]]
            d[txt_xy[j][0],txt_xy[i][0]] = d[txt_xy[i][0],txt_xy[j][0]]    
#    print txt_requst
    Day_order = {}
    Day_order[int(txt_depot[0])] = [0,0,0,1440,0,0,0,1440]
    
    Day_request_info = {u'\u5ef6\u5e73\u9109': {'1900/00/00': {'2018/11/19': []}}}
    
    for i in txt_requst:
#        print int(i[0]),txt_basic[1]/2.0
        if int(i[0]) <= txt_basic[1]:
            
            txt_order = int(i[0])
            txt_p_name = int(i[0])
            txt_d_name = int(txt_p_name + txt_basic[1])-1

            txt_p_time = i[-2:]
            txt_d_time = txt_requst[txt_d_name][-2:]

            if txt_p_time[0] == 0:
                user_max_ride_time = a + b * t[txt_p_name,txt_d_name]
                txt_p_time[0] = txt_d_time[1] - user_max_ride_time
                txt_p_time[1] = txt_d_time[1] - t[txt_p_name,txt_d_name]
                
            if txt_d_time[0] == 0:
                user_max_ride_time = a + b * t[txt_p_name,txt_d_name]
                txt_d_time[1] = txt_p_time[0] + user_max_ride_time 
                txt_d_time[0] = txt_p_time[0] + t[txt_p_name,txt_d_name]
                
            Day_order[txt_order] = [txt_order] + [txt_p_name] + txt_p_time + [1] + [txt_d_name] + txt_d_time
            Day_order[-txt_order] = [-txt_order] + [txt_d_name] + txt_d_time + [1] 
#            print Day_order[txt_order]
#            print Day_order[-txt_order]
            Day_request_info[u'\u5ef6\u5e73\u9109']['1900/00/00']['2018/11/19'].append(txt_order)

    resource_info = {}
    unuse_resource_info = {u'\u5ef6\u5e73\u9109': {'2018/11/19': []}}
    useed_resource_info = {u'\u5ef6\u5e73\u9109': {'2018/11/19': {}}}
    for i in range(fleet_n):
        resource_info[i+1] = [i+1, u'', u'', '2018/11/19', u'\u5ef6\u5e73\u9109', u'RAP-3017', u'\u90b1\u7d2b\u5609', txt_depot[-2], txt_depot[-1], txt_basic[3]]
        unuse_resource_info[u'\u5ef6\u5e73\u9109']['2018/11/19'].append(i+1)
    print resource_info
    village_key = [u'\u5ef6\u5e73\u9109']
    #####################################################
 
#    data_start_time = time.time()
#    #---sql_resource---
#    fleet = fleet_n
#    sql_resource = []
##    sql_resource_start_time = time.time()
#    for i in range(fleet):
#        resource_info  = [u'', u'', datetime.datetime(2018, 11, 19, 0, 0), u'\u5ef6\u5e73\u9109', u'RAP-3017', u'\u90b1\u7d2b\u5609', 
#                          datetime.datetime(1900, 1, 1, 0, 0), datetime.datetime(1900, 1, 1, 23, 59), 4]
#        sql_resource.append(resource_info)
#
##    sql_resource_end_time = time.time()
##    print "sql_resource_time",sql_resource_end_time-sql_resource_start_time
#    #---sql_cost---
#    sql_cost = []
##    [u'2018/11/19', u'\u5ef6\u5e73\u9109',
##     u'\u53f0\u7063\u53f0\u6771\u7e23\u5351\u5357\u9109\u5609\u8c50\u675189\u865f',
##     u'\u53f0\u7063\u53f0\u6771\u7e23\u5351\u5357\u9109\u5609\u8c50\u675189\u865f', 0, 0.0,
##     u'Administrator', datetime.datetime(2018, 12, 27, 9, 40, 27, 73000), None, None]
#    
#
#
#    #pick xy and delivery xy -> uniform
#    #pick tw -> taipei distribution  -> uniform
#    #delivery tw ->  estimate
##    
#    np.random.seed(seed)
#    total_num = people_n
#    size = 16.0
#    speed = 24.14/60
#
##    Max_mile = 10000000000000000
#    hourly_requests =[]
#    distrbution = [0.0011,0.0018,0.0018,0.0023,0.0052,0.0163,0.0429,0.1634,0.142,0.07,0.056,0.039,0.026,0.0187,0.022,0.022,0.055,0.131,0.086,0.033,0.02,0.0249,0.0196,0]
#
#    for i in range(total_num):
#        hourly_requests.append(int(np.random.choice(len(distrbution),p = distrbution)))
#    #print sum(distrbution)
#    #print sorted(hourly_requests)    
#    px = np.random.uniform(-size/2,size/2,total_num)
#    py = np.random.uniform(-size/2,size/2,total_num)
#    dx = np.random.uniform(-size/2,size/2,total_num)
#    dy = np.random.uniform(-size/2,size/2,total_num)
#    pt = np.random.uniform(0,60,total_num)
#    #print
#    cost_list = []
#    req_num = 0
#    hourly_requests = sorted(hourly_requests)
##    sql_request_start_time = time.time()
#    
#    #---sql_request---
#    sql_request = []
##    [u'2018/11/19', u'\u5ef6\u5e73\u9109', u'', 316, u'\u90b1\u5065\u5fb7',
##     u'\u53f0\u7063\u53f0\u6771\u7e23\u5351\u5357\u9109\u5609\u8c50\u675189\u865f', u'\u53f0\u7063\u53f0\u6771\u7e23\u5ef6\u5e73\u9109\u6607\u5e73\u8def84\u865f', 2,
##     None, None, datetime.datetime(1900, 1, 1, 6, 50), datetime.datetime(1900, 1, 1, 7, 0),
##     u'Administrator', datetime.datetime(2018, 12, 27, 9, 40, 27, 730000), None, None]
#    
#    for i in range(len(hourly_requests)):
#        if i < total_num:
#    #        print i
#            DRT = dist(px[i],py[i],dx[i],dy[i])/speed
#            MRT = a + b*DRT
#            time_start = hourly_requests[i]*60
#            pick_u = round(pt[i]+time_start)
#            pick_l = round(pick_u+tw)
#            deli_u = round(pick_u+DRT)
#            deli_l = round(pick_u+tw+MRT)
#    #        whole_tw = [pick_u+time_start,pick_u+time_start+tw,pick_u+time_start+DRT,pick_u+time_start+tw+MRT]
#    #        for j in range(len(whole_tw)):
#    #            print whole_tw[j]
#            if deli_l >= 1440:
#                deli_l = 1439
#            if deli_u >= 1440:
#                deli_u = 1439        
#    #        print 
#    #        print hourly_requests[i],DRT
#    #        print pt[i],time_start,hourly_requests[i]
#    #        print [pick_u,pick_l,deli_u,deli_l]
#    #        print px[i],py[i],dx[i],dy[i]
#            cost_list.append([px[i],py[i]])
#            cost_list.append([dx[i],dy[i]])
#            SENDORDER_ID_CAR_SHARING = u''
#            if i+1 == 3 or i+1 ==7 or i+1 ==9:
#                SENDORDER_ID_CAR_SHARING = 1
#            elif i+1 == 4 or i+1 ==8 or i+1 ==6:
#                SENDORDER_ID_CAR_SHARING = 2
#            elif i+1 == 5 or i+1 ==1 or i+1 ==10:
#                SENDORDER_ID_CAR_SHARING = 3
#            elif i+1 == 2:
#                SENDORDER_ID_CAR_SHARING = 0
#    #        print SENDORDER_ID_CAR_SHARING
#            req_info=[
#                    u'2018/11/19', u'\u5ef6\u5e73\u9109',SENDORDER_ID_CAR_SHARING , i+1, u'\u90b1\u5065\u5fb7',
#                    u'%i'%(req_num+1), u'%i'%(req_num+2), 1,
#                    datetime.datetime(1900, 1, 1, int(pick_u//60), int(pick_u%60)), datetime.datetime(1900, 1, 1, int(pick_l//60), int(pick_l%60)),
#                    datetime.datetime(1900, 1, 1, int(deli_u//60), int(deli_u%60)), datetime.datetime(1900, 1, 1, int(deli_l//60), int(deli_l%60)),
#                    u'Administrator', datetime.datetime(2018, 12, 27, 9, 40, 27, 730000), None, None]
##            print req_info
#            sql_request.append(req_info)
#            req_num = req_num+2
##    sql_request_end_time = time.time()
##    print "sql_request_time",sql_request_end_time-sql_request_start_time
##    print  len(sql_request)
#
#    #        print req_num
#    #[u'2018/11/19', u'\u5ef6\u5e73\u9109', u'', 316, u'\u90b1\u5065\u5fb7',
#    # u'\u53f0\u7063\u53f0\u6771\u7e23\u5351\u5357\u9109\u5609\u8c50\u675189\u865f', u'\u53f0\u7063\u53f0\u6771\u7e23\u5ef6\u5e73\u9109\u6607\u5e73\u8def84\u865f', 2,
#    # None, None, datetime.datetime(1900, 1, 1, 6, 50), datetime.datetime(1900, 1, 1, 7, 0),
#    # u'Administrator', datetime.datetime(2018, 12, 27, 9, 40, 27, 730000), None, None]
#    cost_info = {}
#    dist_info = {}    
##    sql_cost_start_time = time.time()
#    for i in range(len(cost_list)):
#        for j in range(len(cost_list)):
#    #        print cost_list[i],cost_list[j]
#            temp_dist = dist(cost_list[i][0],cost_list[i][1],cost_list[j][0],cost_list[j][1])
#            cost_informatiom=[u'2018/11/19', u'\u5ef6\u5e73\u9109',
#             u'%i'%(i+1),u'%i'%(j+1), temp_dist/speed,temp_dist,
#             u'Administrator', datetime.datetime(2018, 12, 27, 9, 40, 27, 73000), None, None]
#            sql_cost.append(cost_informatiom)
#            cost_info[u'%i'%(i+1),u'%i'%(j+1)] = temp_dist/speed
#            dist_info[u'%i'%(i+1),u'%i'%(j+1)] = temp_dist           
#    #        print i+1,j+1
##    sql_cost_end_time = time.time()
##    print "sql_cos_time",sql_cost_end_time-sql_cost_start_time
#    #%%            
#    resource,cost,request = sql_resource,sql_cost,sql_request
#    #%%
#    def time_form(intime):
#        str_intime =  str(intime)
#        int_intime = int(str_intime[11])*10*60+int(str_intime[12])*60+int(str_intime[14])*10+int(str_intime[15])
#        return int_intime
#    
##    tnd_copy_start_time = time.time()     
#    t = copy.deepcopy(cost_info)
#    d = copy.deepcopy(dist_info)
##    tnd_copy_end_time = time.time() 
##    print t
##    print d    
#    #def main_fun(request,cost,resource): 
#    request_info = {}
#    village_key = []
#    Day_request_info = {}
##    request_info_start_time = time.time()  
#
#    
#    Day_order = {}
#    
#    for i in request:
#        
#        SENDORDER = i[3]
#        
#        if i[9] == None:
#            Pp,Dp,n_C= i[5],i[6],i[7]
#            
#            EPT = time_form(i[10])-3*t[Pp,Dp]+new_tw/2
#            EDT = time_form(i[11])-t[Pp,Dp]-new_tw/2            
#            
#            LPT = time_form(i[10])+new_tw/2-15
#            LDt = time_form(i[11])-new_tw/2+15 
#
#            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDt]
#            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDt,n_C]            
#            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDt]
#            
#        elif i[10] == None or i[11] == None:
#            Pp,Dp,n_C= i[5],i[6],i[7]
#            
#            EPT = time_form(i[8])+new_tw/2-15
#            EDT = time_form(i[9])-new_tw/2+15       
#            
#            LPT = time_form(i[8])+t[Pp,Dp]-new_tw/2   
#            LDt = time_form(i[9])+3*t[Pp,Dp]+new_tw/2   
#
#            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDt]
#            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDt,n_C]            
#            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDt]   
#            
#        else:
#            Pp,Dp,n_C= i[5],i[6],i[7]
#            
#            EPT = time_form(i[8])+new_tw/2
#            EDT = time_form(i[9])-new_tw/2       
#            
#            LPT = time_form(i[10])+new_tw/2
#            LDt = time_form(i[11])-new_tw/2
#            
#            Day_order[SENDORDER] = [SENDORDER]+[Pp,EPT,EDT,n_C,Dp,LPT,LDt]
#            Day_order[-SENDORDER] = [SENDORDER]+[Dp,LPT,LDt,n_C]             
#            temp_one = [str(i[0]),i[1],i[4],i[5],i[6],i[7],EPT,EDT,LPT,LDt]
#    #        print SENDORDER
#    #    SENDORDER_date = SENDORDER[0:8]
#        SENDORDER_date = "19000000"
#        SENDORDER_date = str(SENDORDER_date[:4])+"/"+str(SENDORDER_date[4:6])+"/"+str(SENDORDER_date[6:])
#    #    SENDORDER_ID = str(SENDORDER[8:])
#        SENDORDER_ID = str(SENDORDER)
#    
#        for j in SENDORDER_ID:
#            if int(j) !=0:
#                SENDORDER_ID = int(SENDORDER_ID[SENDORDER_ID.index(j):])
#                break
#    #        print temp_one
#        request_info[SENDORDER_ID] = [SENDORDER_date]+temp_one[0:2]+[SENDORDER_ID]+temp_one[2:10]
#        
#        request_info_now = request_info[SENDORDER_ID]
#        if request_info_now[2] not in village_key:
#            village_key.append(request_info_now[2])
#            Day_request_info[request_info_now[2]] = {}
#        if request_info_now[0] not in Day_request_info[request_info_now[2]].keys():
#            Day_request_info[request_info_now[2]][request_info_now[0]] = {}
#            Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
#        else:
#            if request_info_now[1] not in Day_request_info[request_info_now[2]][request_info_now[0]].keys():
#                Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]] = []
#                Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]] = [request_info_now[3]]
#            else:
#                Day_request_info[request_info_now[2]][request_info_now[0]][request_info_now[1]].append(request_info_now[3])
#    print village_key
#    print "-----Day_order-----"  
#    print Day_order        
#    for i in Day_order:
#        print i,Day_order[i]
#    print        
#    print "-----Day_request_info-----"
#    print Day_request_info
#    print Day_request_info[u'\u5ef6\u5e73\u9109']['1900/00/00']['2018/11/19']
#    print
#%%unknown
    unknown_canidate = range(1,people_n+1)
#    print unknown_canidate
#    unknown_canidate = []
#    for i in range(1,people_n+1):
#        l_up = Day_order[i][3]
#        l_down = Day_order[i][7]
#        Tud = t[Day_order[i][1],Day_order[i][5]]
#        upper_bound_i = min(l_up,l_down-Tud-service_time) 
#        if upper_bound_i-arrive_time > 0:
#            unknown_canidate.append(i)
#        else: 
#            print i
    unknown_request = {}
    unknown_num = int(round(people_n*unknown_rate))
    unknown_request = dict.fromkeys(village_key, [])
#    print unknown_num,len(unknown_canidate)
    if unknown_num < len(unknown_canidate):
        for village in village_key:
            Day_keys = sorted(Day_request_info[village].keys())
            unknown_request[village] = dict.fromkeys(Day_keys, [])
            for day in Day_keys:
                reser_Day_keys = sorted(Day_request_info[village][day].keys())
                unknown_request[village][day] = dict.fromkeys(reser_Day_keys, [])
        #        for reser_Day in reser_Day_keys[:1]:
                for reser_Day in reser_Day_keys:
                    for i in range(unknown_num):
                        while True:
                            unknown_draw = int(np.random.choice(unknown_canidate,1))
                            l_up = Day_order[unknown_draw][3]
                            l_down = Day_order[unknown_draw][7]
                            Tud = t[Day_order[unknown_draw][1],Day_order[unknown_draw][5]]
                            upper_bound_i = min(l_up,l_down-Tud-service_time) 
                            if upper_bound_i-arrive_time >= 0:
                            
                                if unknown_draw not in unknown_request[village][day][reser_Day]:
                                    unknown_request[village][day][reser_Day].append(unknown_draw)
                                    unknown_request[village][day][reser_Day] = sorted(unknown_request[village][day][reser_Day])
                                    break
                                else:
#                                    print unknown_draw,"NO"
                                    continue
                            else:
#                                print unknown_draw,"NO000"
                                break
    else:
        
        for village in village_key:
            Day_keys = sorted(Day_request_info[village].keys())
            unknown_request[village] = dict.fromkeys(Day_keys, [])
            for day in Day_keys:
                reser_Day_keys = sorted(Day_request_info[village][day].keys())
                unknown_request[village][day] = dict.fromkeys(reser_Day_keys, [])
                for reser_Day in reser_Day_keys:   
                    unknown_request[village][day][reser_Day] = unknown_canidate
#    print unknown_request[village][day][reser_Day]
#                print "    all",len(Day_request_info[village][day][reser_Day]),Day_request_info[village][day][reser_Day] 
#    print "unknown ",len(unknown_request[village][day][reser_Day]),unknown_request
    for village in village_key:
        Day_keys = sorted(Day_request_info[village].keys())
        for day in Day_keys:
            reser_Day_keys = sorted(Day_request_info[village][day].keys())
            for reser_Day in reser_Day_keys:
                for i in unknown_request[village][day][reser_Day]:
                    Day_request_info[village][day][reser_Day].remove(i)
#                print "  known",len(Day_request_info[village][day][reser_Day]),Day_request_info[village][day][reser_Day] 
#    print Day_request_info[village][day][reser_Day]
##    print request_info[1]
##    unroute_request_info = request_info.keys()
##    request_info_end_time = time.time()  
##    print "request_info_time",request_info_end_time-request_info_start_time    
#    #%% 
#    resource_info = {}
#    unuse_resource_info = {}
#    useed_resource_info = {}
##    resource_info_start_time = time.time()  
#
#    car_x=0
#    for i in resource:
#        car_x+=1
#        temp_resource = [car_x,i[0],i[1],i[2].strftime('%Y/%m/%d'),i[3],i[4],i[5],time_form(i[6]),time_form(i[7]),i[8]]
#
#        temp_carnumber = temp_resource[4]
#        temp_village = temp_resource[3]
#        temp_date = temp_resource[0]
#
#        if temp_carnumber not in unuse_resource_info.keys():
#            unuse_resource_info[temp_carnumber] = {}
#            useed_resource_info[temp_carnumber] = {}
#        if  temp_village not in unuse_resource_info[temp_carnumber].keys():
#            unuse_resource_info[temp_carnumber][temp_village] = [temp_date]
#            useed_resource_info[temp_carnumber][temp_village] = {}
#        else:
#            unuse_resource_info[temp_carnumber][temp_village].append(temp_date)
#        resource_info[temp_date] = temp_resource
##    resource_info_end_time = time.time()  
##    print "resource_infotime",resource_info_end_time-resource_info_start_time  
#    print  "-----resource_info-----"
#    print resource_info
#    for i in resource_info:
#        print i,resource_info[i]
#    print
#    print  "-----unuse_resource_info-----"
#    print unuse_resource_info
#    print    
#    print  "-----useed_resource_info-----"   
#    print useed_resource_info 
#    print    

#    data_end_time = time.time()  
##    print "data_time",data_end_time-data_start_time  
#    start_time =	time.time()
    #%%
    Large_cost = 99999
    unservable_requests = {}
#    func_start_time = time.time()
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
    def route_seed_initialer(unroute_list,village,Day):
#        print "route_seed_initialer unroute_list",unroute_list
    #        print useed_resource_info[village][Day]
        now_uroute_list = []
        for i in unroute_list:
            now_uroute_list.append(Day_order[i])
        print "--",now_uroute_list[0][2]
        sort_now_uroute_list = sorted(now_uroute_list, key = lambda x : (x[2]))
        sort_uroute_list = []
        for i in sort_now_uroute_list:
            sort_uroute_list.append(i[0])   
    #        print sort_uroute_list
        all_car_key_info = []
    #        print all_car_key_info
        for i in unuse_resource_info[village][Day]:
            all_car_key_info.append(resource_info[i])

        sort_all_car_key_info = sorted(all_car_key_info, key = lambda x : (x[-7]))
        sort_all_car_key = []
        for i in sort_all_car_key_info:
            sort_all_car_key.append(i[0])   
        new_uroute_list = copy.copy(sort_uroute_list)

        for j in sort_uroute_list:
    #            print "----"
            unservable_time = 0
            break_sign = 0
            for i in sort_all_car_key:
                current_routeA = [j,-j]
    #                print "  repeat time",len(sort_all_car_key[sort_all_car_key.index(i):])
    #                print current_routeA,i,check_feasible_route(current_routeA,i),resource_info[i]
                if check_feasible_route(current_routeA,i) == 0:
    #                    print "here"
    #                    print " It is feasible",current_routeA,i,j
                    break_sign += 1
                    useed_resource_info[village][Day][i] = [0,j,-j,0]
#                    print "useed_resource_info",useed_resource_info[village][Day]
                    new_uroute_list.remove(j)
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
                new_uroute_list.remove(j)
            if break_sign>0:
                break

        return new_uroute_list
    
    def route_seed_initialer2(uroute_list,village,Day):
#        print "uroute_list,village,Day",uroute_list,village,Day
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
                current_routeA = [0,j,-j,0]
    #                print current_routeA,i,check_feasible_route(current_routeA,i),resource_info[i]
                if check_feasible_route(current_routeA,i) == 0:
    #                print " It is feasible"
                    print i 
                    useed_resource_info[village][Day][i] = [0,j,-j,0]
                    print useed_resource_info[village][Day][i]
                    seed_list.remove(j)
                    break                  
                else:
                    unservable_time += 1
        for i in useed_resource_info[village][Day].keys():
            if i in unuse_resource_info[village][Day]:
                unuse_resource_info[village][Day].remove(i)
        return new_uroute_list+seed_list
    #%% Check feasibility
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
  
    
    def idle_counter(feasible_route):
#        print "    ",feasible_route
#        print "debug_time",debug_time
        node_service_time = check_service_time(feasible_route,"list")
        node_arrive_time = check_arrive_time(feasible_route,"list")
        ##########################
        test = feasible_route
        test_n = 0
        e_time_list = [Day_order[i][2] for i in feasible_route]
        l_time_list = [Day_order[i][3] for i in feasible_route]
#        print len(l_time_list)
        cuttime_list = []
        for i,j in zip(node_service_time,node_arrive_time):
            if j < i:
                cuttime_list.append(i-j)
            else:
                cuttime_list.append(0)
#        print len(cuttime_list)
        id_time = 0
#        route_arrive_time = check_service_time(test)
        test_ancher = 0
        if test[0] == 0:
            for i in range(len(test)-1):
                test_n += test[i]
                if test_n == 0:
                    if test[i] != 0:
#                        print test[i],test_ancher,i+1,test[test_ancher:i+1]
#                        print "          ",cuttime_list[test_ancher:i+1]
#                        print "     ",node_service_time[test_ancher:i+1] 
#                        print "     ",node_arrive_time[test_ancher:i+1] 
#                        print
                        for j in range(test_ancher,i+1):
#                            print test[j]
    #                        if test[j] == 29 or test[j] == 4:
    #                        print test[i],test_ancher,i+1,test[test_ancher:i+1]
#                            print "     ",cuttime_list[test_ancher:i+1]                            
    #                            print "          ",test[j],node_arrive_time[j],node_service_time[j],cuttime_list[j],e_time_list[j],l_time_list[j]
#                            print "     ",node_arrive_time[test_ancher:i+1] 
#                            print "     ",e_time_list[test_ancher:i+1] 
#                            print "     ",l_time_list[test_ancher:i+1] 
                            
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
#                                        print "NOOOO",test[j]
                                        left_time_list = [l_time_list[l]-node_arrive_time[l]for l in range(test_ancher,j)]
#                                        print left_time_list
#                                        print "     ",node_service_time[test_ancher:i+1] 
#                                        print "     ",node_arrive_time[test_ancher:i+1]                                         
                                        min_left_time = min(left_time_list)
                                        for l in range(test_ancher,j):
#                                            print test[l],left_time_list[l-test_ancher]
                                            node_service_time[l] = node_service_time[l] + min_left_time
                                            node_arrive_time[l] = node_arrive_time[l] + min_left_time
                                        node_arrive_time[j] = node_arrive_time[j] + min_left_time                                               
#                            print
#                                        print "     ",node_service_time[test_ancher:i+1] 
#                                        print "     ",node_arrive_time[test_ancher:i+1] 
#                                        print "------"
#                                        print "     ",e_time_list[test_ancher:i+1] 
#                                        print "     ",l_time_list[test_ancher:i+1]                            
#                        print "     ",node_service_time[test_ancher:i+1] 
#                        print "     ",node_arrive_time[test_ancher:i+1] 
#                        print "     ",e_time_list[test_ancher:i+1] 
#                        print "     ",l_time_list[test_ancher:i+1]                                            
#                        print [l_time_list[j]-node_arrive_time[j]for j in range(test_ancher,i+1)]
                        left_time_list = [l_time_list[j]-node_arrive_time[j]for j in range(test_ancher,i+1)]
                        min_left_time = min(left_time_list)
#                        print min_left_time,left_time_list.index(min(left_time_list))
                        for j in range(test_ancher,i+1):
                            node_service_time[j] = node_service_time[j] + min_left_time
                            node_arrive_time[j] = node_arrive_time[j] + min_left_time  
#                        print "     ",node_service_time[test_ancher:i+1] 
#                        print "     ",node_arrive_time[test_ancher:i+1] 
#                        print "     ",e_time_list[test_ancher:i+1] 
#                        print "     ",l_time_list[test_ancher:i+1] 
#                        print "-----"                            
                    test_ancher = i+1
                    
#        for i in range(len(feasible_route)):
#            afasfadv = ""
#            if node_service_time[i]>node_arrive_time[i]:
#                afasfadv = "****************************"
#                id_time += (node_service_time[i]-node_arrive_time[i])
#            print feasible_route[i],node_arrive_time[i],node_service_time[i],afasfadv

        return id_time  
    def empty_counter(feasible_route):
        test = feasible_route
        ep_time = 0
        test_n = 0
        for i in range(len(test)-1):
            test_n += test[i]
            if test_n == 0:
                now_node = Day_order[test[i]][1]            
                nex_node = Day_order[test[i+1]][1]  
#                print i,test[i],test[i+1],"++++",t[now_node,nex_node]
                ep_time += t[now_node,nex_node]
#        print ep_time
        return ep_time 
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
    
    def trip_counter(feasible_route):
#        print feasible_route
        test = feasible_route
        trip_time = 0
        test_n = 0
        for i in range(len(test)-1):
            test_n += test[i]
            if test_n == 0:
#                print test_n
                if test[i] != 0:
                    
                    trip_time += 1
#                    print i,test[i],test[i+1],"++++",trip_time
#        print trip_time
        return trip_time     

    def check_feasible_route(feasible_route,car_number):
#        print feasible_route
#        check_start_time = time.time()
        debug_time = Day_order[feasible_route[0]][2]
        starttime = resource_info[car_number][-3]
        endtime = resource_info[car_number][-2]
        debug_route_cap = resource_info[car_number][-1]
        debug1 = 0
        debug2 = 0    
        ################################################
        if debug_time<starttime:
            debug2 += 10
        ################################################
        debug6 = 0
        debug7 = 0
        if len(feasible_route)%2 == 0:
            test = feasible_route
            test_n = 0
            test_ancher = 0         
            route_arrive_time = check_service_time(test,"list")
            
            for i in range(len(test)):
                test_n += test[i]
                if test_n == 0:
                    total_duration = route_arrive_time[i]-route_arrive_time[test_ancher]
                    if total_duration > max_route_duration:
                        debug6 += 1000
                    test_ancher = i+1
                    
            for i in range(len(test)):
                test_n += test[i]
                if test[i] > 0:
                    test_target = test.index(-test[i])
                    ride_time =  route_arrive_time[test_target] - route_arrive_time[i]
                    if ride_time > max_ride_time :
                        debug7 += 1000
        ################################################
        #check 12Km
                     
        ################################################
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
        debug_route_time = []
        debug_real_time = []    
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
                    if now_node > 0:
                        debug_time += service_time
            for i,j in zip(debug_route_time,debug_real_time):
                if  i > j:
                    debug1 = 1
            if debug_time > endtime:
                debug2 = 10
                
        debug5 = 0
        if waiting_time != "AllowWait" and len(feasible_route)%2 == 0:   
            if waiting_time == "forward":
                node_service_time = check_service_time(feasible_route,"list")
                node_arrive_time = check_arrive_time(feasible_route,"list")                 
            if waiting_time == "backwaed":
            
                node_service_time = ride_counter(feasible_route,"list")
                node_arrive_time = ride_counter(feasible_route,"arrive")  

            cuttime_list = []
            for i,j in zip(node_service_time,node_arrive_time):
                if j < i:
                    cuttime_list.append(i-j)
                else:
                    cuttime_list.append(0)            
            test = feasible_route
            test_n = 0
            test_ancher = 0
            if test[0] == 0:
                for i in range(len(test)-1):
                    test_n += test[i]
                    if test_n == 0:
                        if test[i] != 0:  
                            wait_time = sum(cuttime_list[test_ancher:i+1])-cuttime_list[test_ancher]
#                            print "    wait_time",wait_time
                            if wait_time > 0:
                                debug5 += 1
                        test_ancher = i+1 
                        
#            print debug_time , endtime
    
    #    debug5 = 0
        debug_signal = debug1 + debug2 + debug4 + debug5 + debug6 + debug7
    #    print feasible_route,o_dist,debug_signal
#        check_end_time = time.time()

        return debug_signal
#    print "             ",check_feasible_route([0, 20, 22, 11, -11, -22, 3, -3, 10, -10, 5, -20, -5, 0],3)
    def check_start_place(o_route,arrive_insert_time):
        now_route_time = check_service_time(o_route,"list")
        
        if arrive_insert_time <= now_route_time[0]:
    #                            print "--",0,now_route_time[0]
            start_place = 0
        elif arrive_insert_time >= now_route_time[-1]:
    #                            print "---------",-1,now_route_time[-1]
            start_place = -1
            
        else:
            for now_position in range(len(now_route_time)-1):                           
                if arrive_insert_time >= now_route_time[now_position] and arrive_insert_time <= now_route_time[now_position+1]:

                    pre_node = Day_order[o_route[now_position]][1]
                    now_node = Day_order[o_route[now_position+1]][1]
                    e_time = Day_order[o_route[now_position+1]][2]

                    if now_route_time[now_position] +10 + t[pre_node,now_node] < e_time:
                        start_place = now_position + 1
                    else: 
                        start_place = now_position + 2  
        return start_place
    #%% regret_insert    
    def regret_insert(unroute_list,village,Day,arrive_insert_time = None):
#        print "----",arrive_insert_time
#        print unroute_list
#        print arrive_insert_time
        reserve_Plan_key = reserve_Plan[village][day].keys()
#        print reserve_Plan_key
        if Day not in reserve_Plan_key:
#            print "++"
            unroute_list = route_seed_initialer2(unroute_list,village,Day)    
#            print "unroute_list",unroute_list
#        print useed_resource_info[village][Day]            
    #    for fadfad in range(10):
        tt_dist_for_time = 0
        o_route_tt_dist_for_time = 0
        o_route_time = 0
        customer_time = 0
        regret_time = 0
        insert_for_time = 0
        insert_for_second_time = 0
        after_insert_check_time = 0
#        before_insert_second_time = 0
#        before_check_time = 0
#        before_insert_time = 0      
        regret_start_time = time.time()
        while len(unroute_list) > 0:

            car_keys = useed_resource_info[village][Day].keys()        
            temp_route = copy.copy(useed_resource_info[village][Day].values())
#            print "car_keys",car_keys,"temp_route:",temp_route
            c2_value = []
            c2_route = []
            c2_place = []
            c2_customer = []
            customer_start_time = time.time() 
            for customer in unroute_list:
                min_c1_route = []
                min_c1_value = []
                min_c1_place = []
                customer_p = customer
                customer_d = -customer_p
                o_route_start_time = time.time()
                for o_route in temp_route: 
                    
                    
                    if arrive_insert_time != None and arrive_insert_time != 0:
                        
                        start_place = check_start_place(o_route,arrive_insert_time)

                    elif arrive_insert_time == 0:
                        start_place = 1
                    else:
                        start_place = 1
                    car_number = car_keys[useed_resource_info[village][Day].values().index(o_route)]
                     
                    c1_value = []
                    c1_place = []

                    insert_for_start_time = time.time()         
                    for p_place in range(start_place,len(o_route)): 
#                        before_insert_second_start_time = time.time()
                        test_p_route =  copy.copy(o_route)
#                        before_insert_end_time = time.time()
#                        before_insert_time += (before_insert_end_time-before_insert_second_start_time)                        
                        test_p_route.insert(p_place,customer_p) 
#                        before_check_end_time = time.time()
#                        before_check_time += (before_check_end_time-before_insert_second_start_time)
                        if check_feasible_route(test_p_route,car_number) == 0:
#                            before_insert_second_end_time = time.time()
#                            before_insert_second_time+=(before_insert_second_end_time-before_insert_second_start_time)
                            
                            for d_place in range(p_place+1,len(o_route)+1):
                                insert_for_second_start_time = time.time()
                                test_d_route = copy.copy(test_p_route)
                                test_d_route.insert(d_place,customer_d)      
                                
                                if check_feasible_route(test_d_route,car_number) == 0:
                                    ##################################################################
                                    tt_dist_for_start_time = time.time()
                                    tt_dist = 0
                                    for test_c in range(len(test_d_route)-1):
                                        tt_dist += d[Day_order[test_d_route[test_c]][1],Day_order[test_d_route[test_c+1]][1]]
                                    tt_dist_for_end_time = time.time()
                                    tt_dist_for_time += (tt_dist_for_end_time-tt_dist_for_start_time)
#                                    print tt_dist_for_end_time-tt_dist_for_start_time
#                                    o_route_tt_dist_for_start_time = time.time()
                                    o_route_tt_dist = 0
                                    for test_c in range(len(o_route)-1):
                                        o_route_tt_dist += d[Day_order[o_route[test_c]][1],Day_order[o_route[test_c+1]][1]]                                     
                                    c1 = tt_dist-o_route_tt_dist
                                    o_route_tt_dist_for_end_time = time.time()
                                    o_route_tt_dist_for_time += (o_route_tt_dist_for_end_time-tt_dist_for_start_time)
    #                                c1 = tt_dist
                                    ##################################################################
                                    c1_value.append(c1)
                                    c1_place.append([p_place,d_place])
                                insert_for_second_end_time = time.time()
                                insert_for_second_time += (insert_for_second_end_time-insert_for_second_start_time)
                    insert_for_end_time = time.time()   
                    insert_for_time += (insert_for_end_time-insert_for_start_time)
                    min_c1_route.append(o_route)   
                    after_insert_check_start_time = time.time()
                    if len(c1_value) > 0:
#                        print c1_value
                        min_value = min(c1_value)
                        min_place = c1_place[c1_value.index(min_value)]                           
                        min_c1_value.append(min_value)
                        min_c1_place.append(min_place)
                    else:   
#                        print "??"
                        min_c1_value.append(Large_cost)
                        min_c1_place.append([-Large_cost,-Large_cost])    
                    after_insert_check_end_time = time.time()
                    after_insert_check_time += (after_insert_check_end_time-after_insert_check_start_time)
    #            print "min_c1_value",min_c1_value
                o_route_end_time = time.time()
                o_route_time += (o_route_end_time-o_route_start_time)
#                print min_c1_value
                if len(min_c1_value) == 0:
                    continue
                else:
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
#                print "c2_route",max_c2_index,c2_route
                max_c2_route = c2_route[max_c2_index]
                max_c2_place = c2_place[max_c2_index]
                max_c2_customer = c2_customer[max_c2_index]
#                print max_c2_customer
                max_c2_index = useed_resource_info[village][Day].values().index(max_c2_route)     
#                print max_c2_route
                for insert_p,insert_c in zip(max_c2_place,max_c2_customer):
                    max_c2_route.insert(insert_p,insert_c)
#                print max_c2_route
                useed_resource_info[village][Day].values()[max_c2_index] = max_c2_route
#                print useed_resource_info
                unroute_list.remove(max_c2_customer[0])    
#                print unroute_list
            else:
                new_car = len(useed_resource_info[village][Day])+1
                resource_info[new_car] = [new_car, u'', u'', '2018/11/19', u'\u5ef6\u5e73\u9109', u'RAP-3017', u'\u90b1\u7d2b\u5609', txt_depot[-2], txt_depot[-1], txt_basic[3]]               

                useed_resource_info[village][Day][new_car] = [0,customer,-customer,0]
                unroute_list.remove(customer)
       
            customer_end_time = time.time() 
            customer_time += (customer_end_time-customer_start_time)
        regret_end_time = time.time() 
        regret_time += (regret_end_time-regret_start_time)
#        print useed_resource_info[village][Day],len(useed_resource_info[village][Day])
#        print "             customer_time",customer_time        
#        print "              o_route_time",o_route_time        
#        print "           insert_for_time",insert_for_time
#
#        print "        before_insert_time",before_insert_time
#        print "         before_check_time",before_check_time
#        print " before_insert_second_time",before_insert_second_time
#        print "    insert_for_second_time",insert_for_second_time
#        print "   after_insert_check_time",after_insert_check_time
#        print "          tt_dist_for_time",tt_dist_for_time
#        print "  o_route_tt_dist_for_time",o_route_tt_dist_for_time        
#        print
#
#        print "                check_time",check_time
#        print "               regret_time",regret_time        
        return 
    #%% reject_insert
    def reject_insert(unroute_list,village,Day,arrive_insert_time = None):
#        print "reject"
        now_uroute_list = []
        for i in unroute_list:
            now_uroute_list.append(Day_order[i])
        sort_now_uroute_list = sorted(now_uroute_list, key = lambda x : (x[2]))
    #    print sort_now_uroute_list
        sort_uroute_list = []
        for i in sort_now_uroute_list:
            sort_uroute_list.append(i[0])
    #    print sort_uroute_list
        if len(useed_resource_info[village][Day]) == 0:
            for car in unuse_resource_info[village][Day]:
    #            print car
                for customer in sort_uroute_list:
                    if check_feasible_route([0,customer,-customer,0],car) == 0:
#                        print "--------------------",useed_resource_info
#                        print unuse_resource_info
                        useed_resource_info[village][Day][car]=[0,customer,-customer,0]
#                        print "--------------------",useed_resource_info
#                        print unuse_resource_info
                        sort_uroute_list.remove(customer)
                        break

        for i in useed_resource_info[village][Day].keys():
            if i in unuse_resource_info[village][Day]:
                unuse_resource_info[village][Day].remove(i)

        for customer in sort_uroute_list:
            car_place = {}
            car_value = {}
            for car in useed_resource_info[village][Day].keys():
    #            print customer,carbe
                best_place = {}
                insert_route = copy.copy(useed_resource_info[village][Day][car])
                if arrive_insert_time != None and arrive_insert_time != 0:                    
                    start_place = check_start_place(insert_route,arrive_insert_time)
                elif arrive_insert_time == 0:
                    start_place = 1
                else:
                    start_place = 1                
                for p_place in range(start_place,len(insert_route)):
                    for d_place in range(p_place+1,len(insert_route)+1): 
                        o_route = copy.copy(insert_route)
                        o_route.insert(p_place,customer)
                        o_route.insert(d_place,-customer)
    #                    print o_route,check_feasible_route(o_route,car),total_distant(o_route)
    #                    if customer == 14:
    #                        print o_route,check_feasible_route(o_route,car) 
                        if check_feasible_route(o_route,car) == 0:
    #                        print insert_route,o_route,check_feasible_route(o_route,car),total_distant(o_route)
                            best_place[p_place,d_place] = total_distant(o_route)
                if len(best_place)>0:
    #                print car,best_place
    #                print "    ",customer,car,min(best_place, key=best_place.get),best_place[min(best_place, key=best_place.get)]
    #                
                    car_place[car]=min(best_place, key=best_place.get)
                    car_value[car]=best_place[min(best_place, key=best_place.get)]
            if len(car_value)>0:
#                print "yes"
                insert_car = min(car_value, key=car_value.get)
                insert_place = car_place[insert_car]
                useed_resource_info[village][Day][insert_car].insert(insert_place[0],customer)
                useed_resource_info[village][Day][insert_car].insert(insert_place[1],-customer)
            else:
#                print "        reject",customer,start_place
    #            print Day_order[customer],Day_order[-customer]
    #            print useed_resource_info
                total_C = {}
                for car in useed_resource_info[village][Day]:
    #                print car
                    for scheduled_request in useed_resource_info[village][Day][car]:
                        if scheduled_request > 0:
                            
                            EPTi = Day_order[scheduled_request][2]
                            LDTi = Day_order[scheduled_request][6]
                            EPTk = Day_order[customer][2]
                            LDTk = Day_order[customer][6]
                            
                            if EPTi <= LDTk or EPTk <= LDTi:
#                                print "car,customer,scheduled_request",car,customer,scheduled_request
                                
                                remove_route = copy.copy(useed_resource_info[village][Day][car])
    #                            print remove_route
                                original_remove_cost = total_distant(remove_route)
                                remove_route.remove(scheduled_request)
                                remove_route.remove(-scheduled_request)
                                new_remove_cost = total_distant(remove_route)
                                Ci_remove = new_remove_cost-original_remove_cost
#                                print remove_route,Ci_remove
                                best_place = {}
                                for p_place in range(start_place,len(remove_route)+1):
                                    for d_place in range(p_place+1,len(remove_route)+1):
                                        insert_route_i = copy.copy(remove_route)
                                        insert_route_i.insert(p_place,customer)
                                        insert_route_i.insert(d_place,-customer)  
                                        if check_feasible_route(insert_route_i,car) == 0:
#                                            print insert_route,o_route,check_feasible_route(o_route,car),total_distant(o_route)
                                            best_place[p_place,d_place] = total_distant(insert_route_i)   
                                if len(best_place) > 0:
                                    Ck_insert = best_place[min(best_place, key=best_place.get)] 
                                    Ck_insert_place = min(best_place, key=best_place.get)
#                                    print "Ck_insert",Ck_insert,min(best_place, key=best_place.get)
    #                                print scheduled_request
                                    car_place = {}
                                    car_value = {}                                
                                    for avail_vehicle in useed_resource_info[village][Day]:
                                        if avail_vehicle != car:
                                            insert_route = copy.copy(useed_resource_info[village][Day][avail_vehicle])
                                            best_place = {}
                                            for p_place in range(start_place,len(insert_route)+1):
                                                for d_place in range(p_place+1,len(insert_route)+1):
                                                    insert_route_i = copy.copy(insert_route)
                                                    insert_route_i.insert(p_place,scheduled_request)
                                                    insert_route_i.insert(d_place,-scheduled_request)  
    #                                                print insert_route_i,insert_route,check_feasible_route(insert_route_i,avail_vehicle),total_distant(insert_route_i)
                                                    if check_feasible_route(insert_route_i,avail_vehicle) == 0:
    #                                                    print insert_route,o_route,check_feasible_route(o_route,avail_vehicle),total_distant(o_route)
                                                        best_place[p_place,d_place] = total_distant(insert_route_i)   
                                            if len(best_place)>0:
                                                car_place[avail_vehicle]=min(best_place, key=best_place.get)
                                                car_value[avail_vehicle]=best_place[min(best_place, key=best_place.get)]                                                    
                                    if len(car_value)>0:
                                        
#                                        print car_place
#                                        print car_value
                                        insert_car = min(car_value, key=car_value.get)
                                        Ci_insert_place = car_place[insert_car]
                                        Ci_insert = car_value[insert_car]
                                        total_C[scheduled_request,car,Ck_insert_place,insert_car,Ci_insert_place] = Ci_remove + Ck_insert + Ci_insert
                                    else:
                                        continue
                                else:
                                    continue 
                            else:
                                continue
                
                if len(total_C) > 0:
#                    print "--"
                    min_c = min(total_C, key=total_C.get)
                    useed_resource_info[village][Day][min_c[1]].remove(min_c[0])
                    useed_resource_info[village][Day][min_c[1]].remove(-min_c[0])
                    useed_resource_info[village][Day][min_c[1]].insert(min_c[2][0],customer)
                    useed_resource_info[village][Day][min_c[1]].insert(min_c[2][1],-customer)
                    useed_resource_info[village][Day][min_c[3]].insert(min_c[4][0],min_c[0])
                    useed_resource_info[village][Day][min_c[3]].insert(min_c[4][1],-min_c[0])
                else:
#                    print "++"
                    new_car = len(useed_resource_info[village][Day])+1
#                    unuse_resource_info[village][Day].append(new_car)
                    resource_info[new_car] = [new_car, u'', u'', '2018/11/19', u'\u5ef6\u5e73\u9109', u'RAP-3017', u'\u90b1\u7d2b\u5609', txt_depot[-2], txt_depot[-1], txt_basic[3]]                    
                    useed_resource_info[village][Day][new_car] = [0,customer,-customer,0]

        return 

    #%% basic_insert
    def basic_insert(unroute_list,village,Day,arrive_insert_time = None):
#        print unroute_list,village,Day
    #    print unuse_resource_info
    #    print useed_resource_info
        now_uroute_list = []
        for i in unroute_list:
            now_uroute_list.append(Day_order[i])
        sort_now_uroute_list = sorted(now_uroute_list, key = lambda x : (x[2]))
    #    print sort_now_uroute_list
        sort_uroute_list = []
        for i in sort_now_uroute_list:
            sort_uroute_list.append(i[0])
    #    print sort_uroute_list
        if len(useed_resource_info[village][Day]) == 0:
            for car in unuse_resource_info[village][Day]:
    #            print car
                for customer in sort_uroute_list:
                    if check_feasible_route([0,customer,-customer,0],car) == 0:
#                        print "--------------------",useed_resource_info
#                        print unuse_resource_info
                        useed_resource_info[village][Day][car]=[0,customer,-customer,0]
#                        print "--------------------",useed_resource_info
#                        print unuse_resource_info
                        sort_uroute_list.remove(customer)
                        break
#        print unuse_resource_info[village][Day]            
#        print useed_resource_info[village][Day]
        for i in useed_resource_info[village][Day].keys():
            if i in unuse_resource_info[village][Day]:
                unuse_resource_info[village][Day].remove(i)
#        print unuse_resource_info[village][Day]            
#            
#        print sort_uroute_list
        for customer in sort_uroute_list:
            car_place = {}
            car_value = {}
            for car in useed_resource_info[village][Day].keys():
    #            print customer,carbe
                best_place = {}
                insert_route = copy.copy(useed_resource_info[village][Day][car])
                if arrive_insert_time != None and arrive_insert_time != 0:
                    
                    start_place = check_start_place(insert_route,arrive_insert_time)

                elif arrive_insert_time == 0:
                    start_place = 1
                else:
                    start_place = 1                
                for p_place in range(start_place,len(insert_route)+1):
                    for d_place in range(p_place+1,len(insert_route)+1): 
                        o_route = copy.copy(insert_route)
                        o_route.insert(p_place,customer)
                        o_route.insert(d_place,-customer)
    #                    print o_route,check_feasible_route(o_route,car),total_distant(o_route)
    #                    if customer == 14:
    #                        print o_route,check_feasible_route(o_route,car) 
                        if check_feasible_route(o_route,car) == 0:
    #                        print insert_route,o_route,check_feasible_route(o_route,car),total_distant(o_route)
                            best_place[p_place,d_place] = total_distant(o_route)
                if len(best_place)>0:
    #                print car,best_place
    #                print "    ",customer,car,min(best_place, key=best_place.get),best_place[min(best_place, key=best_place.get)]
    #                
                    car_place[car]=min(best_place, key=best_place.get)
                    car_value[car]=best_place[min(best_place, key=best_place.get)]
            if len(car_value)>0:
                
    #            print car_place
    #            print car_value
                insert_car = min(car_value, key=car_value.get)
                insert_place = car_place[insert_car]
    #            print insert_car,insert_place
                useed_resource_info[village][Day][insert_car].insert(insert_place[0],customer)
                useed_resource_info[village][Day][insert_car].insert(insert_place[1],-customer)

            else: 
                new_car = len(useed_resource_info[village][Day])+1
#                    unuse_resource_info[village][Day].append(new_car)
                resource_info[new_car] = [new_car, u'', u'', '2018/11/19', u'\u5ef6\u5e73\u9109', u'RAP-3017', u'\u90b1\u7d2b\u5609', txt_depot[-2], txt_depot[-1], txt_basic[3]]                    
                useed_resource_info[village][Day][new_car] = [0,customer,-customer,0]                
               
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
            o_route_tt_dist += d[Day_order[feasible_route[test_c]][1],Day_order[feasible_route[test_c+1]][1]]  
        
        return o_route_tt_dist
#    func_end_time = time.time()
#    print "func_time",func_end_time-func_start_time
    #%%main program
    #print tt_cost([10118, -10118, 10129, -10129, 10122, -10122])
    Day_request = copy.copy(Day_request_info)
    
    reserve_Plan = {}
#    main_program_start_time = time.time()
    for village in village_key:
        Day_keys = sorted(Day_request[village].keys())
        reserve_Plan[village] = {}
        for day in Day_keys:
            reserve_Plan[village][day] = {}
            reser_Day_keys = sorted(Day_request[village][day].keys())
    #        for reser_Day in reser_Day_keys[:1]:
            for reser_Day in reser_Day_keys:
                unroute_Day_requests = copy.copy(Day_request[village][day][reser_Day])
    #            print unroute_Day_requests
    #            reserve_Plan_key = reserve_Plan[village][day].keys()
    #            if reser_Day not in reserve_Plan_key:
    #                unroute_Day_requests = route_seed_initialer2(unroute_Day_requests,village,reser_Day)
    #                print "unroute_Day_requests",unroute_Day_requests
#                heuristic_start_time = time.time()
                if heuristic == "regret" :
#                    print useed_resource_info
                    final_route = regret_insert(unroute_Day_requests,village,reser_Day)
                elif heuristic == "reject" :
                    final_route = reject_insert(unroute_Day_requests,village,reser_Day)
                elif heuristic == "basic" :
                    final_route = basic_insert(unroute_Day_requests,village,reser_Day)                    
#                heuristic_end_time = time.time()
#                print "            heuristic_time",heuristic_end_time-heuristic_start_time
#                print final_route
                reserve_Plan[village][day][reser_Day] = final_route
#    main_program_end_time = time.time()
#    print "main_program_time",main_program_end_time-main_program_start_time
#    print village_key
    
    for village in village_key:
        for reser_Day in useed_resource_info[village].keys(): 
            a = 0
            distant = 0
            for i in useed_resource_info[village][reser_Day].keys():
#                print i,useed_resource_info[village][reser_Day][i]
                a+=len(useed_resource_info[village][reser_Day][i])
                distant += tt_cost(useed_resource_info[village][reser_Day][i])  
#            print
#            print "total number:",a/2-len(useed_resource_info[village][reser_Day]),",total distant:",distant 

    #%% operator
    
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
                                        if tt_cost(original_plan[car_c])+tt_cost(original_plan[l])-tt_cost(remoeve_route_c)-tt_cost(insert__route_c) > 0:
#                                            print tt_cost(original_plan[car_c])+tt_cost(original_plan[l])-tt_cost(remoeve_route_c)-tt_cost(insert__route_c) 
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
        #    print i,original_plan[i]
            for j in original_plan[i]:
                if j > 0 :
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
            #                print
            #                print "customer:",i,"car:",car_r
            #                print "customer:",j,"car:",car_s        
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
                                            if tt_cost(insert_route_r) < tt_cost(best_insert_route_r):
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
                                                if tt_cost(insert_route_s) < tt_cost(best_insert_route_s):
                                                    best_insert_route_s = insert_route_s
                                exchange_second_end_insert = time.time()
                                exchange_second_insert += (exchange_second_end_insert-exchange_second_start_insert)
                                if len(best_insert_route_s) > 0:
                                    if (tt_cost(original_plan[car_r])+tt_cost(original_plan[car_s]))-(tt_cost(best_insert_route_r)+tt_cost(best_insert_route_s))>0:
#                                        print (tt_cost(original_plan[car_r])+tt_cost(original_plan[car_s]))-(tt_cost(best_insert_route_r)+tt_cost(best_insert_route_s))
                                        original_plan[car_r] = best_insert_route_r                 
                                        original_plan[car_s] = best_insert_route_s
                                        all_reinsert_info[i] = car_s
                                        all_reinsert_info[j] = car_r  
                                        if len(best_insert_route_r) == 0 or len(best_insert_route_s) == 0 :
                                            print "need to cut car"
        return original_plan
        

    #%% Improvement

    if improvement == True:
#        print "+"
        for village in village_key:
            for reser_Day in useed_resource_info[village].keys(): 
                relocation_sign = True
                exchange_sign = True
                while True:
#                    
                    
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
#                    new_plan = exchange_operator(copy.copy(mid_plan))
#                    if old_plan != new_plan:
#                        useed_resource_info[village][reser_Day] = new_plan
#                    else:
#                        break
    
#                while True:
#                    print "---exchange_operator---"
#                    old_plan = copy.copy(useed_resource_info[village][reser_Day])
#                    new_plan = exchange_operator(useed_resource_info[village][reser_Day])
#                    
#                    if old_plan != new_plan:
#                        useed_resource_info[village][reser_Day] = new_plan
#                    else:
#                        break            
#    improve_time =	time.time()

    #%% waiting strategy & Fix TW
    if waiting_strategy != None:
    
        for village in village_key:
            for reser_Day in useed_resource_info[village].keys():  
                for route in useed_resource_info[village][reser_Day]:
#                    print useed_resource_info[village][reser_Day][route]
                    fix_route = useed_resource_info[village][reser_Day][route]
                    if waiting_strategy == "drive_first":
                        nodeservice_time =  check_service_time(fix_route,"list")     
                    elif waiting_strategy == "wait_first":
                        nodeservice_time =  ride_counter(fix_route,"list")
                    e_time_list = [Day_order[j][2] for j in fix_route]
                    l_time_list = [Day_order[j][3] for j in fix_route] 
#                    print nodeservice_time
#                    print e_time_list
#                    print l_time_list
                    for j,k,l,m in zip(e_time_list,nodeservice_time,l_time_list,fix_route):
                        if m != 0:
#                            print m,Day_order[m][2]-Day_order[m][3]
                            if round(j,2)+5 > round(k,2):
#                                print round(j,2),round(k,2),round(l,2),"up"
                                Day_order[m][3] = j + new_tw
                            elif round(l,2)-5 < round(k,2):
#                                print round(j,2),round(k,2),round(l,2),"down"
                                Day_order[m][2] = l - new_tw
                            else:
#                                print round(j,2),round(k,2),round(l,2),"+5-5"
                                Day_order[m][2] = k - new_tw/2                          
                                Day_order[m][3] = k + new_tw/2
#                            print m,Day_order[m][2]-Day_order[m][3]
    #                print useed_resource_info[village][reser_Day][i]  
    #                a_e_time_list = [Day_order[j][2] for j in useed_resource_info[village][reser_Day][i]]
    #                a_l_time_list = [Day_order[j][3] for j in useed_resource_info[village][reser_Day][i]] 
    #                for a,b,y,z in zip(e_time_list,l_time_list,a_e_time_list,a_l_time_list):
    #                    print a,b,y,z
#        for village in village_key:
#            for reser_Day in useed_resource_info[village].keys():  
#                for i in useed_resource_info[village][reser_Day]:
#                    print useed_resource_info[village][reser_Day][i]  
#                    for j in useed_resource_info[village][reser_Day][i]:
#                        print j,Day_order[j][2],Day_order[j][3],Day_order[j][2]-Day_order[j][3]
        
    #%% Dynamic & Fix TW
#    print unknown_request[village][day][reser_Day]

    if waiting_strategy != None:
#        print "TTTTTTTTTTTTTTTTTTTTT"
        if len(unknown_request[village][day][reser_Day]) > 0:
        
            arrival_time = {}
#            print unknown_request[village][day][reser_Day],len(unknown_request[village][day][reser_Day])
            for i in unknown_request[village][day][reser_Day]:
                l_up = Day_order[i][3]
                l_down = Day_order[i][7]
                Tud = t[Day_order[i][1],Day_order[i][5]]
                upper_bound_i = min(l_up,l_down-Tud-service_time)   
        #        print upper_bouDYNAMICnd_i,upper_bound_i-60
                if upper_bound_i-arrive_time > 0:
    #                print "              known after start"
                    arrival_time[i] = upper_bound_i-arrive_time
                else:
                    print "known before start",i
                    arrival_time[i] = 0
            arrival_order = sorted(arrival_time.items(), key = lambda x : (x[1]))
#            print arrival_order
            for i in arrival_order:    
        #    for i in arrival_order[:1]:
        #    for i in arrival_order[3:]:
                arrive_customer = i[0]
                arrive_time = i[1]
                if insert_type == "local":
                    basic_insert([arrive_customer],village,reser_Day,arrive_insert_time = arrive_time) 
                    
                for village in village_key:
                    for reser_Day in useed_resource_info[village].keys():  
                        for route in useed_resource_info[village][reser_Day]:
                            if arrive_customer in useed_resource_info[village][reser_Day][route]:
#                                print useed_resource_info[village][reser_Day][route]  
#                                for j in useed_resource_info[village][reser_Day][route]:
#                                    print j,Day_order[j][2]-Day_order[j][3]                                 
                                fix_route = useed_resource_info[village][reser_Day][route]
                                if waiting_strategy == "drive_first":
                                    nodeservice_time =  check_arrive_time(fix_route,"list")        
                                elif waiting_strategy == "wait_first":
                                    nodeservice_time =  ride_counter(fix_route,"list")  
                                e_time_list = [Day_order[j][2] for j in fix_route]
                                l_time_list = [Day_order[j][3] for j in fix_route] 
#                                print e_time_list
#                                print l_time_list
                                for j,k,l,m in zip(e_time_list,nodeservice_time,l_time_list,fix_route):
                                    if m != 0:
#                                        print m,Day_order[m][2]-Day_order[m][3]
                                        if round(j,2)+5 > round(k,2):
            #                                print round(j,2),round(k,2),round(l,2),"up"
                                            Day_order[m][3] = j + new_tw
                                        elif round(l,2)-5 < round(k,2):
            #                                print round(j,2),round(k,2),round(l,2),"down"
                                            Day_order[m][2] = l - new_tw
                                        else:
            #                                print round(j,2),round(k,2),round(l,2),"+5-5"
                                            Day_order[m][2] = k - new_tw/2                          
                                            Day_order[m][3] = k + new_tw/2                                
#                                print useed_resource_info[village][reser_Day][route]  
#                                for j in useed_resource_info[village][reser_Day][route]:
#                                    print j,Day_order[j][2]-Day_order[j][3]    
    a = 0
    for village in village_key:
        for reser_Day in useed_resource_info[village].keys():  
            for route in useed_resource_info[village][reser_Day]:  
                print useed_resource_info[village][reser_Day][route]
                a+=(len(useed_resource_info[village][reser_Day][route])-2)/2.0
#                        for j in useed_resource_info[village][reser_Day][route]:
#                            print j,Day_order[j][2]-Day_order[j][3]                                           
#                    if heuristic == "regret":
#                        regret_insert([arrive_customer],village,reser_Day,arrive_insert_time = arrive_time)
#                    elif heuristic == "reject":
#                        reject_insert([arrive_customer],village,reser_Day,arrive_insert_time = arrive_time)
#                    elif heuristic == "basic":
#                        basic_insert([arrive_customer],village,reser_Day,arrive_insert_time = arrive_time)                   
#%% data    
    total_miles, empty_distant, ride_hour, idle_hour, rideshare, increaceOFridemile, increaceOFridetime = 0,0,0,0,0,0,0
    trip_num = 0.0
    direct_time = 0.0
    wait_time = 0.0
    for village in village_key:
        for reser_Day in useed_resource_info[village].keys(): 
            for i in useed_resource_info[village][reser_Day].keys():
                cal_route = useed_resource_info[village][reser_Day][i]
#                print "  ",i,cal_route
                total_miles += tt_cost(cal_route) 
                empty_distant += empty_counter(cal_route)
                if waiting_strategy == "drive_first":
                    ride_hour += check_service_time(cal_route) 
#                    for a_t,s_t in zip(check_arrive_time(cal_route,"list"),check_service_time(cal_route,"list")):
#                        wait_time += (a_t-s_t)                    
                elif waiting_strategy == "wait_first":               
                    ride_hour += ride_counter(cal_route)
#                    for a_t,s_t in zip(ride_counter(cal_route,"arrive"),ride_counter(cal_route,"list")):
#                        wait_time += (a_t-s_t)                      
                idle_hour += idle_counter(cal_route)
                trip_num += trip_counter(cal_route)
                for j in cal_route:
                    if j != 0 and j > 0:
                        direct_time += t[Day_order[j][1],Day_order[-j][1]]
#                        print j,Day_order[j][1],Day_order[-j][1]
                if waiting_strategy == "drive_first":
                    node_service_time = check_service_time(cal_route,"list")
                    node_arrive_time = check_arrive_time(cal_route,"list")                 
                if waiting_strategy == "wait_first":
                    node_service_time = ride_counter(cal_route,"list")
                    node_arrive_time = ride_counter(cal_route,"arrive") 
#                print useed_resource_info[village][reser_Day][route]
                cuttime_list = []
                for i,j in zip(node_service_time,node_arrive_time):
                    if j < i:
                        cuttime_list.append(i-j)
                    else:
                        cuttime_list.append(0) 
#                print "  ",cuttime_list
                test = cal_route
                test_n = 0
                test_ancher = 0
                if test[0] == 0:
                    for i in range(len(test)-1):
                        test_n += test[i]
                        if test_n == 0:
                            if test[i] != 0:  
                                
                                wait_time += (sum(cuttime_list[test_ancher:i+1])-cuttime_list[test_ancher])
#                                print (sum(cuttime_list[test_ancher:i+1])-cuttime_list[test_ancher]),cal_route[test_ancher:i+1],cuttime_list[test_ancher:i+1],cuttime_list[test_ancher]
                            test_ancher = i+1                             
#    print Day_order[1]
#    print Day_order[-1]
#    print direct_time
#    print a,people_n                    
#    print trip_num
#    print algorithm
#    print waiting_time
#    print waiting_strategy
#    print wait_time
    veh_num = len(useed_resource_info[village][reser_Day])
    rideshare = people_n/trip_num
    increaceOFridetime = ride_hour/direct_time*100
    increaceOFridemile = total_miles/direct_time*100
    return float(veh_num), total_miles, empty_distant, ride_hour, idle_hour, rideshare, increaceOFridemile, increaceOFridetime,wait_time
#%% Result
#for i in range(len(result)):
#    cursor.execute("""INSERT INTO VRP_HAS_MATCHED (ENTERPRISEID,
#                                               TAKE_DATE, 
#                                                 GROUP_NAME, 
#                                                 PASSENGER_ORDER_ID, 
#                                                 START_PLACE, 
#                                                 END_PLACE, 
#                                                 SENDORDER_ID_VRP, 
#                                                 TYPE, 
#                                                 UP_ORDER, 
#                                                 DRIVER_NAME, 
#                                                 CAR_NUMBER, 
#                                                 TAKE_TIME, 
#                                                 AVR_TIME)
#                                                 
#                                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""","None",result[i][0],result[i][1],result[i][2],result[i][3],result[i][4],result[i][5],result[i][6],result[i][7],result[i][8],result[i][9],result[i][10],result[i][11])

#cursor.execute('SELECT * from VRP_HAS_MATCHED')
#VRP_HAS_MATCHED = datafit(cursor) 
#print (VRP_HAS_MATCHED)
##print unservable_requests
#cnxn.commit()

#with open('output.csv', 'w', newline='') as csvfile:
path='.'
files=os.listdir(path)     
file_names = ['a4-32.txt','a6-60.txt','a8-96.txt']
file_names2 = ['a7-70.txt','a7-84.txt','a8-80.txt','a8-96.txt']
file_names3 = ['a6-72.txt','a7-70.txt','a7-84.txt','a8-80.txt','a8-96.txt','b6-72.txt','b7-70.txt','b7-84.txt','b8-80.txt','b8-96.txt']
file_names4 = ['a7-84.txt','a8-96.txt']
file_names5 = ['a2-16.txt','a2-20.txt','a2-24.txt','a3-18.txt','a3-24.txt','a3-30.txt','a3-36.txt','a4-16.txt','a4-24.txt','a4-32.txt','a4-40.txt','a4-48.txt','b2-16.txt','b2-20.txt','b2-24.txt','b3-18.txt','b3-24.txt','b3-30.txt','b3-36.txt','b4-16.txt','b4-24.txt','b4-32.txt','b4-40.txt','b4-48.txt']

fleet_n,people_n,tw,a = 3,10,30,5

insertion = ["basic","reject","regret"]
insert_type = ["reoptimize","local"]


b_list = [1.5,2,2.5,3,3.5,4]
b_list2 = [4.5,5,5.5,6,6.5,7]
b_list3 = [1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7]
unknown_rate_list = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
unknown_rate_list2 = [0,0.3,0.6,0.9]
unknown_rate_list3 = [0.1,0.3,0.5,0.7,0.9]
k = "local"

arrive_time_list = [10,30,60]
output_result = []
dynamic_list = [None,True]
improvement_list = [None,True]
#waiting_strategy = "wait_first"

total_seed = 1
b = 4

unknown_rate = 0                  
arrive_time = 10
#waiting_strategy = "wait_first"
#waiting_strategy = "drive_first"
#improvement = True
 
improvement = None
waiting_time_list = ["forward","backwaed","AllowWait"]
waiting_strategy_list = ["drive_first","wait_first"]
waiting_time = "AllowWait"
#for arrive_time in arrive_time_list[1:]:
#for file_name in file_names:
#for b in b_list3:
#for algorithm in insertion: 
for algorithm in insertion[-1:]:     
    for waiting_time in waiting_time_list[-1:]:
        for waiting_strategy in waiting_strategy_list[-1:]:
        
        
#            for file_name in file_names[-1:]:
#            for file_name in files[:48]:
            for file_name in files[:1]:
    
    #            for file_name in files[:24]:            
#                    for unknown_rate in unknown_rate_list:
    #                for unknown_rate in unknown_rate_list2[:1]:    
                        for b in b_list3[5:6]:
                            sum_round_temp_output = [0,0,0,0,0,0,0,0,0,0]
                            for seed in range(total_seed):
            
                                total_start_time = time.time()
                                veh_num, total_miles, empty_distant, ride_hour, idle_hour, rideshare, increaceOFridemile, increaceOFridetime,wait_time =test_exp(file_name,
                                                                                                                                                       algorithm,seed,a,b,k,
                                                                                                                                                       unknown_rate,
                                                                                                                                                       arrive_time,
                                                                                                                                                       improvement,
                                                                                                                                                       waiting_time,
                                                                                                                                                       waiting_strategy)
                                total_end_time = time.time()   
                                cpu_time = total_end_time-total_start_time
            #                    print file_name,algorithm,seed,a,b,k,unknown_rate,veh_num, total_miles, empty_distant, ride_hour, idle_hour, rideshare, increaceOFridemile, increaceOFridetime,cpu_time 
                                temp_output = [veh_num, total_miles, empty_distant, ride_hour, idle_hour, rideshare, increaceOFridemile, increaceOFridetime,cpu_time,wait_time]
            #                    round_temp_output = [round(t_op,3) for t_op in temp_output]
            #                    output_result.append([file_name,algorithm,seed,a,b,k,unknown_rate]+round_temp_output)
            #                    print [file_name,algorithm,seed,a,b,k,unknown_rate]+round_temp_output
                                
                                for i in range(len(temp_output)):
                                    sum_round_temp_output[i] += temp_output[i]
                            round_temp_output = [round(t_op/total_seed,3) for t_op in sum_round_temp_output]
                            output_result.append([file_name,algorithm,seed,a,b,k,unknown_rate]+round_temp_output+[arrive_time,str(improvement),waiting_strategy,waiting_time])
#                            print [file_name,algorithm,seed,a,b,k,unknown_rate]+round_temp_output+[arrive_time,str(improvement),waiting_strategy,waiting_time]
#%% output
import csv
row_list  = ["file_name","algorithm","seed","a","b","k","unknown_rate", "veh_num", "total_miles", "empty_distant", "ride_hour", "idle_hour"," rideshare", "increaceOFridemile", "increaceOFridetime","cpu_time","wait_time"]
#print len(row_list)
#print len(output_result[0])
with open('output.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(row_list)
    writer.writerows(output_result)




#    for i in output_result:
#        print i


