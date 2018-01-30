import numpy as np
import math,sys,os,csv
import time
import threading
import itertools
import random
import matplotlib.pyplot as plt
from pprint import pprint
import Grid_Demo

path=sys.path[0]
Bank_account=0
Bank=[]
step=1
actions = Grid_Demo.actions
Q_values={}
alpha=0.3
discount=0.5
allstates=[]
init=Grid_Demo.start
pick = [[0,0],[2,2],[4,4],[0,3]]
drop = [[0,4],[3,3]]
is_picked=False
total_reward=0
states=[]
hasblock=0
#ind1=find_index([init[0],init[1]],allstates)
for i in range(Grid_Demo.x):
	for j in range(Grid_Demo.y):
		allstates.append([i,j])
'''
for i in range(len(self.actions)):
	a=allstates[i][0]
	b=allstates[i][1]
	key=(a,b,Grid_Demo.actions[i])
	Q_values[key]=0.0
'''
def find_index(target, myList):
	for i in range(len(myList)):
		if (myList[i] == target):
			return i
##ind1=find_index([init[0],init[1]],allstates)
#nitial=allstates[ind1]
for state in allstates:
	for action in actions:
		
		Grid_Demo.set_color((state[0],state[1]), action, 0, Q_values.get((state[0],state[1],action,0),0.0))
		Grid_Demo.set_color((state[0],state[1]), action, 0,Q_values.get((state[0],state[1],action,1),0.0))


def Reward(variable):
	if(variable == "pick"):
		r=12
	elif(variable == "drop"):
		r=12
	else:
		r=-1
	return r

class States(object):
	def __init__(self, state):
		pick = [[0,0],[2,2],[4,4],[0,3]]
		drop = [[0,4],[3,3]]
		self.name = state
		if(self.name in pick):
			self.pickup=4
		if(self.name in drop):
			self.dropoff=0

		#self.pickup=4
		#self.dropoff=0
		self.actions=Grid_Demo.actions
		for i in range(len(self.actions)):
			a=self.name[0]
			b=self.name[1]
			key=(a,b,self.actions[i],0)
			key1=(a,b,self.actions[i],1)
			Q_values[key]=0.0
			Q_values[key1]=0.0



def get_max_value(state,x):
	values=[]
	a=state.name[0]
	b=state.name[1]
	for i in range(4):
		values.append(Q_values[(a,b,state.actions[i],x)])
	m,ind=max( (values[i],i) for i in range(len(values)) )
	return m,ind
	


def aplop(state,x,policy):
	#print pick
	#print drop
	#print [i,j]
	i=state.name[0]
	j=state.name[1]
	
	if([i,j] in pick and x==0):
		var= "pick"
	elif([i,j] in drop and x==1):
		var= "drop"
	else:
		var=None

	if(policy==0):
		action= PRandom(state,x)
	elif(policy==1):
		action= PExploit(state,x)
	elif(policy==2):
		action= PGreedy(state,x)
	return var,action
	
def PRandom(state,x):
	operator = random.choice(state.actions)
	return operator

def PExploit(state,x):
	
	
	seed=random.randint(1,100)
	if(seed<=85):
		operator = PGreedy(state,x)

	else:
		operator=PRandom(state,x)

	
	return operator
	

def PGreedy(state,x):
	values=[]
	a=state.name[0]
	b=state.name[1]
	for i in range(len(state.actions)):
		values.append(Q_values[(a,b,state.actions[i],x)])
	maxv=max(values)
	count=values.count(maxv)
   
	if(count>1):
		best=[]
		for i in range(len(state.actions)):
			if(values[i]==maxv):
				best.append(state.actions[i])
		operator = random.choice(best)
		
	else:
		ind=values.index(maxv)
		operator=state.actions[ind]

	#print count, operator
	return operator
	
	

def apply_op(state,x,option):
	i=state.name[0]
	j=state.name[1]
	global is_picked
	var,op=aplop(state,x,option)
	#print op
	rew_this_step=0
	if(var == "pick" and (state.pickup>0) and (x==0)):
		

		state.pickup-=1
		is_picked=True
		rew_this_step+=12
		x=1
		applicable="pick"
		#print Bank_account
	elif((var == "drop") and (state.dropoff<8) and(x==1)):
		rew_this_step+=12
		x=0
		state.dropoff+=1
		is_picked = False 
		applicable="drop"
	
	
	else:
		l=len(op)
		applicable=None
		rew_this_step+=Reward(op)

	return applicable,rew_this_step,x,op


	

def get_next_state(state,action):
	x=state.name[0]
	y=state.name[1]
	if(action=='e'):
		next_x=x+1
		next_y=y
	elif(action=='w'):
		next_x=x-1
		next_y=y
	elif(action=='n'):
		next_x=x
		next_y=y-1
	elif(action=='s'):
		next_x=x
		next_y=y+1
	
	new_cord=[next_x,next_y]
	
	if (new_cord in allstates):
		new_index=find_index(new_cord,allstates)
		next_state=states[new_index]
	else:
		next_state=None
		
	return next_state
	


def Qlearn(state,x,policy):  
   
	global Bank_account ,total_reward,Bank
	i=state.name[0]
	j=state.name[1]

  
	var,r,new_x,action=apply_op(state,x,policy)
	if(var=="pick" or var=="drop"): #Learning for pick, drop
		m,ind=get_max_value(state,new_x)
		q=Q_values[(i,j,action,x)]
		reward=12
		new_q=(1-alpha)*q + alpha*(reward+ (discount*m))
		#print new_q
		Q_values[(i,j,action,x)] = new_q
		Grid_Demo.set_color((state.name[0],state.name[1]), action, x,new_q )
		block=Grid_Demo.agent_move(0,0,x)
		next_state=state
		if(x==0):
			iter_x=1
		else:
			iter_x=0

	else: #moving
		if action == actions[0]:
			block=Grid_Demo.agent_move(1,0,x)
		elif action == actions[1]:
			block=Grid_Demo.agent_move(-1, 0,x)
		elif action == actions[2]:
			block=Grid_Demo.agent_move(0,-1,x)
		elif action == actions[3]:
			block=Grid_Demo.agent_move(0, 1,x)

		iter_x=block
		next_state=get_next_state(state,action)
	
		if(next_state==None):
			m=0	
		else:
			m,ind=get_max_value(next_state,x)
	
		q=Q_values[(i,j,action,x)]	
		reward=-1
		#Applying the formula
		new_q=(1-alpha)*q + alpha*(reward+ (discount*m))
		Q_values[(i,j,action,x)] = new_q
	
	
		Grid_Demo.set_color((state.name[0],state.name[1]), action, x,new_q )
	
		if(next_state==None):
			next_state=state

	if(state.name in pick and state.pickup==0 ):
		#REMOVE ELEMENT FROM PICK
		#print state.name, "pick", pick
		pick.remove(state.name)
		#print "pick now",pick
	if(state.name in drop and state.dropoff==8 ):
		drop.remove(state.name)

	if (Grid_Demo.restart is True):
		print "RESET"
		reset()
		ini=Grid_Demo.start
		ini_ind=find_index([ini[0],ini[1]],allstates)
		init=states[ini_ind]
		next_state=init
		Grid_Demo.restart = False

		b=Grid_Demo.agent_move(0,0,0)
		
		

	
	Bank.append(Grid_Demo.total_reward)
	
	print "state:" ,state.name,"Action :", action,"Next_state :",next_state.name,"Reward = ", reward,

	#print 'Grid Reward', Grid_Demo.total_reward
	return next_state,iter_x



def SARSA(state,x,op,aa):
	global Bank_account ,total_reward,Bank, states,pick,drop,allstates,total_reward
	i=state.name[0]
	j=state.name[1]

	var,reward,new_x,action1=apply_op(state,x,op)
	if(var=="pick" or var=="drop"):
		if(x==0):
			iter_x=1
		else:
			iter_x=0

		var1, r_, new_xx_, next_action1=apply_op(state,iter_x,op)
		m=Q_values[(i,j,next_action1,iter_x)]
		q=Q_values[(i,j,action1,x)]
		reward=12

		new_q=(1-alpha)*q + alpha*(reward+ (discount*m))

		
		Q_values[(i,j,action1,x)] = new_q

		Grid_Demo.set_color((state.name[0],state.name[1]), action1, x,new_q )
		block=Grid_Demo.agent_move(0,0,x)
		next_state=state
		next_action=next_action1

	

	else:
		if(aa==None):
			action=action1
		else:
			action=aa
			reward=-1
	
		if action == actions[2]:
			block=Grid_Demo.agent_move(0, -1,x)
		elif action == actions[3]:
			block=Grid_Demo.agent_move(0, 1,x)
		elif action == actions[1]:
			block=Grid_Demo.agent_move(-1, 0,x)
		elif action == actions[0]:
			block=Grid_Demo.agent_move(1, 0,x)

		iter_x=block
	
		next_state=get_next_state(state,action)
	
	
		if(next_state==None):
			m=0
		else:
			var2,reward_, new_x_, next_action=apply_op(next_state,x,op)
			ii=next_state.name[0]
			jj=next_state.name[1]
			m=Q_values[(ii,jj,next_action,x)]
	
	
		
		q=Q_values[(i,j,action,x)]
		#Applying the formula
		
		new_q=(1-alpha)*q + alpha*(reward+ (discount*m))
		Q_values[(state.name[0],state.name[1], action, x)] = new_q

		Grid_Demo.set_color((state.name[0],state.name[1]), action, x,new_q )

		if(next_state==None):
			next_state=state
			next_action=None

	
	if(state.name in pick and state.pickup==0 ):
		#REMOVE ELEMENT FROM PICK
		#print state.name, "pick", pick
		pick.remove(state.name)
		#print "pick now",pick
	if(state.name in drop and state.dropoff==8 ):
		drop.remove(state.name)
		
		#print "DRop", drop, state.name
	if (Grid_Demo.restart is True):
		#RESET
		print "RESET"
		
		reset()
		ini=Grid_Demo.start
		ini_ind=find_index([ini[0],ini[1]],allstates)
		init=states[ini_ind]
		next_state=init
		block =Grid_Demo.agent_move(ini[0],ini[1],0)
		Grid_Demo.restart = False
		Grid_Demo.restart_game()
	

	   
	 
	Bank.append(Grid_Demo.total_reward)
	#total_reward+=reward
	#print "state:" ,state.name,"Action :", action,"Next_state :",next_state.name,"Reward = ", reward, 
	#print 'Grid Reward', Grid_Demo.total_reward
	#time.sleep(0.5)
	return next_state,iter_x,next_action

def reset():
	global states,pick,drop,allstates,total_reward
	del states[:]
  
	for i in range(25):
		states.append(States(allstates[i]))

	pick = [[0,0],[2,2],[4,4],[0,3]]
	drop = [[0,4],[3,3]]



def Experiment1(initial):

	global total_reward,Bank,allstates,states
	for step in range(1,3001):
		if(step==1): 
			print "step" ,step
			agent,x = Qlearn(initial,0,0)
				#time.sleep(0.01)
		else:
			print "step" ,step
			agent,x = Qlearn(agent,x,0)
			#time.sleep(0.01)

		step+=1
	Grid_Demo.agent=Grid_Demo.start
	for step in range(3001,6001):	
	
			print "step" ,step
			agent,x = Qlearn(agent,x,2)
			#time.sleep(0.01)
			#time.sleep(0.01)
			step+=1

	
	print "Bank account",Grid_Demo.total_reward
	print "Number of Operators", len(Grid_Demo.num_operators)

	with open(path+"/Experiment1_Q_values.csv", 'wb') as csv_file:
		writer = csv.writer(csv_file)
		for key, value in Q_values.items():
			writer.writerow([key, value])
	
	'''
	b=Bank[:3000]
	a=[i for i in range(len(b))]
	fig = plt.figure()
	plt.plot(a,b)
	plt.title('Experiment 1 :Random')
	fig.savefig(path+"/Experiment1_Random.png")
	'''
	b=Bank
	a=[i for i in range(len(b))]
	fig = plt.figure()
	plt.plot(a,b)
	plt.title('Experiment 1 :Random+Greedy')
	fig.savefig(path+"/Experiment1 Random+Greedy.png")

	
	Grid_Demo.quit()

def Experiment2(initial):
	global total_reward,Bank
	
	num_steps=100
	print "Experiment2"

	print "-----"
	for step in range(1,2000):
		if(step==1): 
			print "step" ,step
			agent,x = Qlearn(initial,0,0)
			#time.sleep(0.01)
		   
		else:
			print "step" ,step
			agent,x = Qlearn(agent,x,0)
			#time.sleep(0.01)
	 
		step+=1

	print "-----"   
	for step in range(2001,10001):

		print "step" ,step

		agent,x = Qlearn(agent,x,1)
		time.sleep(0.01)

		

		step+=1

	

	print "Bank_account",Grid_Demo.total_reward
	print "Number of Operators", len(Grid_Demo.num_operators)
	
	
	b=Bank
	a=[i for i in range(len(b))]
	fig = plt.figure()
	plt.plot(a,b)
	plt.title('Experiment 2 :QLearn Random+Exploit')
	fig.savefig(path+"/Experiment2.png")
	with open(path+"/Experiment2_Q_values.csv", 'wb') as csv_file:
		writer = csv.writer(csv_file)
		for key, value in Q_values.items():
			 writer.writerow([key, value])
	#time.sleep(2)
	Grid_Demo.quit()
	
	
def Experiment3(initial):
  
	global total_reward,Bank
	print 'Experiment3:Implementing SARSA'
	for step in range(1,201):
		if(step==1): 
			print "step" ,step
			agent,x,aa = SARSA(initial,0,0,None)
		else:
			print "step" ,step
			agent,x,aa = SARSA(agent,x,0,aa)
		step+=1

	print "-----"   
	for step in range(201,6001):
		print "step" ,step
		agent,x ,aa= SARSA(agent,x,1,aa)

		step+=1

	print "Bank_account",Grid_Demo.total_reward
	print "Number of Operators", len(Grid_Demo.num_operators)
	
	
	b=Bank
	a=[i for i in range(len(b))]
	fig = plt.figure()
	plt.plot(a,b)
	plt.title('Experiment 3 :Sarsa Random+Exploit')
	fig.savefig(path+"/Experiment3.png")
	with open(path+"/Experiment3_Q_values_2.csv", 'wb') as csv_file:
		writer = csv.writer(csv_file)
		for key, value in Q_values.items():
			writer.writerow([key, value])
	Grid_Demo.quit()



def main():
	#time.sleep(1)
	for i in range(25):
		states.append(States(allstates[i]))



	ini=Grid_Demo.start
	index=find_index([ini[0],ini[1]],allstates)
	initial=states[index]

	#Experiment1(initial)
	#Experiment2(initial)
	Experiment2(initial)


t = threading.Thread(target=main)
t.daemon = True
t.start()
Grid_Demo.init()
