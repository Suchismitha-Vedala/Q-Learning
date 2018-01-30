import time,os
from Tkinter import *
from PIL import Image,ImageTk
import numpy as np
import tkMessageBox
import tkSimpleDialog

root = Tk()
#root.wm_title("Learning Paths from Feedback Using Q-Learning ")
num_operators=[]
op_count=0
triangle_size = 0.3
text_offset = 15
cell_score_min = -0.2
cell_score_max = 0.2
x=5
y=5
width=120
board = Canvas(root, width=x*width, height=y*width)
actions=['e','w','n','s']

start=(4,0)

agent_picked_blocked=False
reward =-1
pd={}
pick=[(0,0),(0,3),(2,2),(4,4)]
drop=[(0,4),(3,3)]
for i in range(4):
	key=pick[i]
	pd[key]=4
for i in range(2):
	key=drop[i]
	pd[key]=0


pick_drop = [(0,0,'cyan2',12,4),(0,3,'cyan2',12,4),(2,2,'cyan2',12,4),(4,4,'cyan2',12,4),(0,4,'purple1',12,0),(3,3,'purple1',12,0)]
dropoff=pickup=0
tri_objects = {}
text_objects = {}
restart = False
total_reward=0.0
#rew_this_step=0
agent=start 
def create_triangle(i, j, action):
	if action == actions[2]: #north
		return (board.create_polygon((i+0.5-triangle_size)*width, (j+triangle_size)*width,
									(i+0.5+triangle_size)*width, (j+triangle_size)*width,
									(i+0.5)*width, j*width,
									fill="white", width=1),
				board.create_text((i+0.5)*width, j*width+text_offset, text=str(width), fill="white"))
	elif action == actions[3]:#south
		return (board.create_polygon((i+0.5-triangle_size)*width, (j+1-triangle_size)*width,
									(i+0.5+triangle_size)*width, (j+1-triangle_size)*width,
									(i+0.5)*width, (j+1)*width,
									fill="white", width=1),
				board.create_text((i+0.5)*width, (j+1)*width-text_offset, text=str(width), fill="white"))
	elif action == actions[1]:#west
		return (board.create_polygon((i+triangle_size)*width, (j+0.5-triangle_size)*width,
									(i+triangle_size)*width, (j+0.5+triangle_size)*width,
									i*width, (j+0.5)*width,
									fill="white", width=1),
				board.create_text(i*width+text_offset, (j+0.5)*width, text=str(width), fill="white"))
	elif action == actions[0]:#east
		return (board.create_polygon((i+1-triangle_size)*width, (j+0.5-triangle_size)*width,
									(i+1-triangle_size)*width, (j+0.5+triangle_size)*width,
									(i+1)*width, (j+0.5)*width,
									fill="white", width=1),
				board.create_text((i+1)*width-text_offset, (j+0.5)*width, text=str(width), fill="white"))


def visualize_grid():
	global pick_drop, width, x, y, agent,agent_picked_blocked
	for i in range(x):
		for j in range(y):
			board.create_rectangle(i*width, j*width, (i+1)*width, (j+1)*width, fill="white", width=1)
			temp = {}
			temp_val = {}
			for action in actions:
				(temp[action], temp_val[action]) = create_triangle(i, j, action)
			tri_objects[(i,j,0)] = temp
			tri_objects[(i,j,1)] = temp
			text_objects[(i,j,0)] = temp_val
			text_objects[(i,j,1)] = temp_val

	for (i, j, c, r,n) in pick_drop: #i,j is the state and c is color , r reward, n number of cells
		# board.create_rectangle(i*width, j*width, (i+1)*width, (j+1)*width, fill=c, width=1)
		board.create_rectangle(i*width, j*width, (i+1)*width, (j+1)*width, fill=c, width=1)
		temp = {}
		temp_val = {}
		for action in actions:
			(temp[action], temp_val[action]) = create_triangle(i, j, action)
		tri_objects[(i,j,0)] = temp
		text_objects[(i,j,0)] = temp_val
		tri_objects[(i,j,1)] = temp
		text_objects[(i,j,1)] = temp_val


visualize_grid()

def set_color(state, action, block, val):
	global cell_score_min, cell_score_max
	triangle = tri_objects[(state[0],state[1],block)][action]
	text = text_objects[(state[0],state[1],block)][action]
	green_dec = int(min(255, max(0, (val - cell_score_min) * 255.0 / (cell_score_max - cell_score_min))))
	green = hex(green_dec)[2:]
	red = hex(255-green_dec)[2:]
	if len(red) == 1:
		red += "0"
	if len(green) == 1:
		green += "0"
	color = "#" + red + green + "00"
	board.itemconfigure(triangle, fill=color)
	board.itemconfigure(text, text = str(format(val, '.2f')), fill="black")
def reset_agent():
	global agent,start
	agent=start
def agent_move(dx, dy,hasblock):

	global agent, x, y, pickup,reward,num_operators, robot, restart,dropoff,pick_drop,total_reward,agent_picked_blocked,pick,drop,pd,op_count
	p=agent[0]
	q=agent[1]
	rew_this_step=0
	if (restart == True):
		restart_game()

	nx=p+dx
	ny =q+dy
	block=hasblock
	if((dx==0) and (dy==0)):
		rew_this_step=12
		op_count+=1

	elif((nx >= 0) and (nx < 5) and (ny >= 0) and (ny < 5)):
		rew_this_step=-1
		op_count+=1
	else:
		rew_this_step=0

	if ((nx >= 0) and (nx < 5) and (ny >= 0) and (ny < 5)):
		
		new_x=nx
		new_y=ny
		agent=(new_x, new_y)
	else:
		new_x=p
		new_y=q
		agent=(new_x,new_y)


	board.coords(robot, new_x*width+width*2/10, new_y*width+width*2/10, new_x*width+width*8/10, new_y*width+width*8/10)


	
	if((p,q) in pick or (p,q) in drop):
	
		if(((p,q) in pick) and (block==0) and pd[(p,q)]>0):
			pd[(p,q)]=pd[(p,q)]-1
			pickup+=1
			block=1
			print "pick"
		
	
		elif (((p,q) in drop) and (block==1) and pd[(p,q)] < 8):
			agent_picked_blocked = False
			dropoff += 1
			block=0
			pd[(p,q)]=pd[(p,q)]+1
			print "drop"

		if (dropoff == 16 ):
			num_operators.append(op_count)
			op_count=0
			restart = True
			dropoff = 0
			block=0
			agent=start
			for i in range(4):
				key=pick[i]
				pd[key]=4
			for i in range(2):
				key=drop[i]
				pd[key]=0
			print ("Restart")
		'''
		print "*****"
		print new_x,new_y, pd[(new_x,new_y)]
		print "*****"
		'''
	total_reward+=rew_this_step
	print (p,q),rew_this_step,total_reward,(new_x,new_y),op_count
	return block
	#time.sleep(0.2)

def restart_game():
	global agent, robot, restart,agent_picked_blocked,pick_drop,pick,drop,pd,dropoff,num_operators,op_count
	restart = False
	agent_picked_blocked=False	
	board.coords(robot, start[0]*width+width*2/10, start[1]*width+width*2/10,start[0]*width+width*8/10, start[1]*width+width*8/10) 

			   
#robot =board.create_oval(10, 10, 200, 200, width=2, fill='blue') 
robot=board.create_oval(start[0]*width+width*2/10, start[1]*width+width*2/10,
							start[0]*width+width*8/10, start[1]*width+width*8/10, fill="blue", width=1, tag="robot")
'''
def call_up(event):
	agent_move(0, -1)


def call_down(event):
	agent_move(0, 1)


def call_left(event):
	agent_move(-1, 0)


def call_right(event):
	agent_move(1, 0)


root.bind("<Up>", call_up)
root.bind("<Down>", call_down)
root.bind("<Right>", call_right)
root.bind("<Left>", call_left)
'''
board.grid(row=0, column=0)
	
def quit():
	time.sleep(1)
	root.destroy()
		
def init():
	root.mainloop()


