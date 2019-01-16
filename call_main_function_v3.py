# -*- coding: utf-8 -*-
"""
Created on Sat Dec 08 16:17:16 2018

@author: Kuan
"""

import pyodbc 
import pandas as pd
import main_fun_v2

server = 'DESKTOP-C7FFVPQ' 
database = 'CarSharing_VRP' 
username = 'jameschu' 
password = 'jameschu' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#print 
#print "---sql_resource---"

cursor.execute('SELECT * from VRP_CAR_USEABLE')
colList = []
for colInfo in cursor.description:
    colList.append(colInfo[0])
rowList = []
while True:
    try:
        row = cursor.fetchone()
        if row:
            rowList.append(list(row))
        else:
            break
    except:   
        continue;
sql_resource = pd.DataFrame(rowList)
sql_resource.columns = colList 


print (sql_resource)
#%%
#print
#print ("---sql_cost---")
#print
cursor.execute('SELECT * from VRP_TRAVEL_MATRIX_DATA')
colList = []
for colInfo in cursor.description:
    colList.append(colInfo[0])
rowList = []
while True:
    try:
        row = cursor.fetchone()
        if row:
            rowList.append(list(row))
        else:
            break
    except:   
        continue;
sql_cost = pd.DataFrame(rowList)
sql_cost.columns = colList 
#print (sql_cost)

#print
#print ("---sql_request---")
#print
cursor.execute('SELECT * from VRP_PRE_ORDER')
colList = []
for colInfo in cursor.description:
    colList.append(colInfo[0])
rowList = []
while True:
    try:
        row = cursor.fetchone()
        if row:
            rowList.append(list(row))
        else:
            break
    except:   
        continue;
sql_request = pd.DataFrame(rowList)
#sql_request.columns = colList 
print (sql_request)
#%%
useed_resource,result = main_fun_v2.main_fun(sql_request,sql_cost,sql_resource)
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
colList = []
for colInfo in cursor.description:
    colList.append(colInfo[0])
rowList = []
while True:
    try:
        row = cursor.fetchone()
        if row:
            rowList.append(list(row))
        else:
            break
    except:   
        continue;
VRP_HAS_MATCHED = pd.DataFrame(rowList)
#VRP_HAS_MATCHED.columns = colList 

print (VRP_HAS_MATCHED)

















            