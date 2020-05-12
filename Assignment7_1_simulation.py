# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 21:23:54 2018

@author: Yang
"""

from tkinter import *
import math
import numpy as np
import random
import copy
import networkx as nx
people_number = 30

door_coordinate = (1,1)
remain_probability = 0
# open maze
import csv
maze = []
with open('maze1.csv', newline='') as csv_file:
#    print (csv_file)
    rows = csv.reader(csv_file)
#    print (rows)
    for row in rows:
        maze.append(row)
#print (maze)
        #print(', '.join(row))
# transfer i,j into x,y and build floor and  obstacle
obstacle_field = {}
floor_key = []   
maze_shape = np.array(maze)
floor_size =maze_shape.shape
for i in range(maze_shape.shape[0]):
    for j in range(maze_shape.shape[1]):
        if maze[i][j] == '0':
            obstacle_field[(j,int(maze_shape.shape[0]-1-i))] = 0
        else:
            obstacle_field[(j,int(maze_shape.shape[0]-1-i))] = 1
            floor_key.append((j,int(maze_shape.shape[0]-1-i)))
            

#creat network
G = nx.DiGraph()
for (x,y) in floor_key:
    G.add_node((x,y))

for (xo,yo) in floor_key:
    for xd in [xo-1,xo,xo+1]:
        for yd in [yo-1,yo,yo+1]:
            if (xd,yd) != (xo,yo) and (xd,yd) in floor_key:
                G.add_edge((xo,yo),(xd,yd))

static_field = nx.shortest_path_length(G,source=door_coordinate)
#print (static_field)
#print (static_field.iteritems())
#for key, value in static_field.iteritems():
for key, value in static_field.items():
#    print (key, value)
    static_field[key] = -value

people_key = [i for i in range(people_number)]
people_initial_coordinate = []
while len(people_initial_coordinate) < people_number:
    chosen_one = random.choice(floor_key)
    if chosen_one not in people_initial_coordinate and chosen_one[0] <18 and chosen_one[1] > 12:
        people_initial_coordinate.append(chosen_one)

occupied_field = dict(zip(floor_key,[0]*len(floor_key)))
'''
obstacle_field = dict(zip(floor_key,[1]*len(floor_key)))
for i in obstacle_key :
    obstacle_field[i] = 0
'''

cell_position = {}
cell_target = {}
for i in range(people_number):
    
    occupied_field[people_initial_coordinate[i]] = 1
    cell_position[i] = people_initial_coordinate[i]
    cell_target[i] = people_initial_coordinate[i]
'''
cell_position = dict(zip(people_key,people_initial_coordinate))
cell_target = dict(zip(people_key,people_initial_coordinate))
'''
stop_signal = False
#cell_initial_coordinate = dict(zip(people_key,people_initial_coordinate))

move_dict = []
move_dict.append(people_initial_coordinate)
for move in range(500): 

    for i in people_key:
        xy_exp_sum = 0
        xy_exp_list = []
        candidate_position = []
        for x in [cell_position[i][0]-1,cell_position[i][0],cell_position[i][0]+1]:
            for y in [cell_position[i][1]-1,cell_position[i][1],cell_position[i][1]+1]:
                
                if (x,y) in floor_key:
                    candidate_position.append((x,y))
                    xy_exp = math.exp(static_field[x,y])*(1-occupied_field[x,y])*obstacle_field[x,y]
                    xy_exp_sum += xy_exp
                    xy_exp_list.append(xy_exp)
        if xy_exp_sum != 0:
            candidate_probability = [j/xy_exp_sum for j in xy_exp_list]
            cell_target[i] = candidate_position[np.random.choice(len(candidate_position),p = candidate_probability)]
        else:
            cell_target[i] = cell_position[i]
    conflict_key = []
    conflict_field = {}    
    for key, value in cell_target.items():
       if value not in conflict_field:
           conflict_field[value] = [key]
       else:
           conflict_field[value].append(key)     
    for key, value in conflict_field.items():
        
        if len(value) > 1:
            move_probability = np.random.uniform(0,1)
            if move_probability <= remain_probability:
                for i in value:
                    cell_target[i] = cell_position[i]
            else:
                remain_one = random.sample(value,len(value)-1)
                for i in remain_one:
                    cell_target[i] = cell_position[i]
    for key, value in cell_target.items():
        if cell_position[key] != value:
            occupied_field[cell_position[key]] = 0 
            cell_position[key] = value
            occupied_field[value] = 1
#    print (cell_position.values())
    copy_cell_position = copy.copy(list(cell_position.values()))
    move_dict.append(copy_cell_position)
    

outfile = open('people_movement1.txt','w')
for row in move_dict:
    #print row
    for colum in row:
        for i in colum:
            outfile.write(str(i)+' ')
        
            #print i
    outfile.write('\n')
outfile.close()

'''

outfile = open('people_movement.csv','w')
writer = csv.writer(outfile)
for row in move_dict:
    print row
    for colum in row:
        for cor in colum:
            print cor
            writer.writerow(str(cor))
    writer.writerow('\n')
outfile.close()
'''
'''
x_range = 15
canvas_height = (floor_size[0])*x_range
canvas_width = (floor_size[1])*x_range
 
x_origin = floor_size[1]
y_origin = floor_size[0]

xy_shift = 0.5
time = canvas_width/x_range
def physical2canvas(move_dict):
    
    for move in move_dict:
        for key, value in move.iteritems(): 
            move[key] = ((value[0]+xy_shift)*x_range,canvas_height-(value[1]+xy_shift)*x_range)
    return move_dict


new_move_dict = physical2canvas(move_dict)
new_cell_initial_coordinate = physical2canvas([cell_initial_coordinate])



root = Tk()
c = Canvas(root,width=canvas_width, height=canvas_height)
c.pack()

for key, value in obstacle_field.iteritems():
    if value == 0:
        a = key[0]
        b = key[1]
        a = (a+xy_shift)*x_range
        b = canvas_height - (b+xy_shift)*x_range
        c.create_rectangle(a-x_range/2,b-x_range/2,a+x_range/2,b+x_range/2.0,fill="black")



text_2_id=c.create_text((door_coordinate[0]+xy_shift)*x_range, canvas_height-(door_coordinate[1]+xy_shift)*x_range, text='*')

c.update()
c.after(1000)

for i in range(people_number):
    locals()['oval_%s' % (i)] = c.create_oval(new_cell_initial_coordinate[0][i][0]-x_range/2, new_cell_initial_coordinate[0][i][1]-x_range/2, (new_cell_initial_coordinate[0][i][0]+1)+x_range/2, (new_cell_initial_coordinate[0][i][1])+x_range/2, fill='red', outline='blue')
    locals()['text_%s' % (i+1)] = c.create_text(new_cell_initial_coordinate[0][i][0], (new_cell_initial_coordinate[0][i][1]),text='%s'%(i))
c.update()

for new_move_position in np.array(new_move_dict):
    for i in range(people_number):
        c.coords(locals()['oval_%s' % (i)],new_move_position[i][0]-x_range/2, new_move_position[i][1]-x_range/2,new_move_position[i][0]+x_range/2,new_move_position[i][1]+x_range/2)
        c.coords(locals()['text_%s' % (i+1)],new_move_position[i][0], new_move_position[i][1])
    c.update()
    c.after(150)
c.mainloop()  

'''