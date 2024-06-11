#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 20:34:09 2024

@author: latavia
"""
#in spare time see if some stuff can be condensed, ex converting to arrays

#------------------------------------------------------------
#for an elbow located at origin:
#------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import pickle #M1 data
from matplotlib.animation import FuncAnimation;import matplotlib.animation as animation #fnimation 
# from scipy.optimize import fsolve,root ##inverse kinematics

#plot reference vs theta
#------------------------------------------------------------
#get spike times from M1 data
#------------------------------------------------------------
#all spike times:
# with open('/Users/latavia/netpyne/SLNC/M1 model/simplearm_output_data.pkl', 'rb') as fileObj: spk_PT = pickle.load(fileObj)['simData']['spkt']

#PT spike times
with open('/Users/latavia/netpyne/SLNC/M1 model/spk_PT.pkl', 'rb') as fileObj: spk_PT = pickle.load(fileObj)

#avg voltage of PT cells
with open('/Users/latavia/netpyne/SLNC/M1 model/voltagesum.pkl', 'rb') as fileObj2: voltageavg= pickle.load(fileObj2)

#input current
with open('/Users/latavia/netpyne/SLNC/M1 model/input_current.pkl', 'rb') as fileObj3: input_current= pickle.load(fileObj3)
input_current=np.array(input_current)

#spike time = N x T rather thsn 1xT
spk_PT=np.sort(spk_PT, axis=0)
unique_id, indice_to_splt = np.unique(spk_PT[:,0],return_index=True)
spkt=np.split(spk_PT[:,1],indice_to_splt[1:])

#initialize
timewindows=100
xloc = []
yloc =[]
joint1 = 1.5
joint2=.75
Unique_ST=[]
Theta1=[] 
Theta2=[]
NetFiringFreq=[]
Unique_spkt=np.zeros((len(spkt),timewindows-1))


for i in range(0,len(spkt)):
    for j in range(0,timewindows-1):
        if spkt[i][(spkt[i] >= (j*1)) & (spkt[i] < (j*1+10))].any():
            Unique_spkt[i][j]=j*((timewindows)/100) # u = j*1 or j*10
        else:
            Unique_spkt[i][j] = 0
            
            
#for cell 3, times it recieves stim
with open('spk_input.pkl', 'rb') as fileObj3: spk_input = pickle.load(fileObj3)




#------------------------------------------------------------
class ArmModel: #create arm movement
    
    def __init__(self,joint1,joint2): #initialize w joint lengths
        self.joint1 =joint1
        self.joint2=joint2

    def move_arm():   #calc freq -> number spikes/timewindow
        global Theta1,Theta2,xloc,yloc,joint1,joint2,timewindows

        for t in range(0,timewindows-1):  #time from 0 to 1000. this way, can take 1000 slices of time... [0,1], [1,2] .... [999,1000]
            j=t         

            #spikeTimes=spkt[i][(spkt[i] >= (j*10)) & (spkt[i]< (j*10+10))] #1ms window --> can increase
            spikeTimes=spk_PT[:,1][(spk_PT[:,1] >= (j)) & (spk_PT[:,1]< (j+1))]
            numspikes = float(len(spikeTimes)) #num spikes = amount of times fired in time window
            
            duration =  1
            netFiringFreq = numspikes/duration #freq = numspikes per timewindow
            NetFiringFreq.append(netFiringFreq)
                #------------------------------------------------------------
                #forward kinematics - change theta based on spike frequency. 
                #------------------------------------------------------------
                
           # deg
            theta1=(netFiringFreq*np.pi/2) #theta from rate
            theta2=(netFiringFreq*np.pi)
            Theta1.append(theta1) #add to empty lists #theta from rate
            Theta2.append(theta2)
 
        Theta1=np.array(Theta1) #list --> array
        Theta2=np.array(Theta2)
            # # Unique_ST = np.array(Unique_ST)

    # pos of each joint -> [joint 1 , joint 2]
        xpos=[joint1*np.cos(Theta1),joint1*np.cos(Theta1)+joint2*np.cos(Theta2+Theta1)] # t1 + t2 to use correct axis
        ypos=[joint1*np.sin(Theta1),joint1*np.sin(Theta1)+joint2*np.sin(Theta2+Theta1)]
        # ypos=[joint1*np.sin(Theta1),joint1*np.sin(Theta1)+joint2*np.sin(Theta2+Theta1)]

        xloc.append(xpos) #add to empty lists
        yloc.append(ypos)
        xloc=abs(np.array(xloc)) #list --> array
        yloc=abs(np.array(yloc))
        xloc=xloc.squeeze() #remove first dimension. (1,2,900) -> (2,900)
        yloc=yloc.squeeze()
        
        return(xloc,yloc)
    
    move_arm()
Arm = ArmModel(joint1,joint2) #run model



#------------------------------------------------------------
# weights - thetas derived from inverse kinematics
#------------------------------------------------------------ 
#Weight = SpikeTimes * ThetaInv
#[N,2] = [N,99] * [99,2]
#------------------------------------------------------------ 
#calc Weights, np.linalg.inv(A)

Thetas = np.stack((Theta1, Theta2), axis=-1)
ThetaStar = np.linalg.pinv(Thetas)
Weight = np.matmul(Unique_spkt, np.transpose(ThetaStar))


# # #------------------------------------------------------------
# # # plotting
# # #------------------------------------------------------------
# #X and Y vs time
timewindow=np.linspace(0,len(xloc[0])+1,len(xloc[0]))
plt.figure()
plt.plot(timewindow, xloc[1,:], label='X Position')
plt.plot(timewindow, yloc[1,:], label='Y Position')
# # plt.plot(timewindow, abs(xloc[1,:]-(yloc[1,:])), label='Sum')
plt.xlabel('Time Window (10ms/window)')
# plt.ylabel('Position')
plt.title('End Effector Position over Time')
plt.legend()
plt.show()

# plt.figure()
# spikeplot
# plt.scatter(np.array(spk_input),[1,1,1,1,1,1,1,1,1,1,1,1])
# plt.plot(timewindow,xloc[1,:])
# plt.plot(timewindow,yloc[1,:])
# plt.xlabel('Time Window (10ms/window)')
# #plt.legend('Stimulus','X pos','Y pos')
# plt.show()

# #3d plot
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# ax.plot(xloc[1,:],timewindow,yloc[1,:])
# ax.set_xlabel('X pos')
# ax.set_zlabel('Y pos')
# ax.set_ylabel('time')
# plt.title('3D XvY')
# plt.show()

# # X vs Y end effector position - scattered
# plt.figure()
# plt.scatter(xloc[1,:],yloc[1,:])
# # plt.scatter(xloc[0,:],yloc[0,:])
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('XvY')
# plt.show()


# current
current_time=np.linspace(0,len(xloc[0])+1,len(input_current))
plt.figure()
plt.scatter(current_time,input_current, label='current')
plt.plot(timewindow, xloc[1,:], label='X Position')
plt.plot(timewindow, yloc[1,:], label='Y Position')
plt.xlabel('time')
plt.title('current vs x')
plt.show()

# # #avg voltages
# # timeV=np.linspace(0,len(xloc[0]),len(voltageavg))
# # plt.figure()
# # plt.plot(timeV,voltageavg)
# # plt.title('Voltage Average')
# # plt.xlabel('time')
# # plt.show()


