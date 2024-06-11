#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 18:29:13 2024

@author: latavia
"""
#run M1 only wo arm
# --------------------------run sim---------------------------------
# to run simulation:
from netpyne import sim
import numpy as np
import pickle
from neuron import h

cfg, netParams = sim.readCmdLineArgs(simConfigDefault='cfg.py', netParamsDefault='checknetparams.py')
#sim.createSimulateAnalyze(netParams,cfg)
sim.create(netParams,cfg)
# init_amp = int(0.0)
# peak_amp = int(0.24)
# ramp_up = np.linspace(init_amp, peak_amp, int(cfg.duration/(cfg.dt)))
# t = h.Vector(np.arange(0,cfg.duration, cfg.dt))
# amp = h.Vector(ramp_up)
# for cell in sim.net.cells:
#     try:
#         amp.play(cell.stims[0]['hObj']._ref_amp, t, True)
#     except:
#         pass
sim.simulate()
sim.analyze()

 #------------------------------------------------------------------------------
#save specifically PT spike times
#spkt_PT = [sim.allSimData['spkt'][n] for n in range(len(sim.allSimData['spkt'])) if sim.net.cells[int(sim.allSimData['spkid'][n])].tags['pop']=='PT5B']

spk_PT=[[sim.allSimData['spkid'][n] for n in range(len(sim.allSimData['spkt'])) if sim.net.cells[int(sim.allSimData['spkid'][n])].tags['pop']=='PT5B'],[ sim.allSimData['spkt'][n] for n in range(len(sim.allSimData['spkt'])) if sim.net.cells[int(sim.allSimData['spkid'][n])].tags['pop']=='PT5B']]
spk_PT=np.transpose(spk_PT)
with open('spk_PT.pkl', 'wb') as f: pickle.dump(spk_PT, f)

#convert voltages of PT cells to array
import numpy as np
voltkeys=sim.allSimData['V_soma'].items() #get voltages
Listkeys=[]
listkeys=list(voltkeys) #convert dict to list
for i in range(0, len(listkeys)-2): #remove elements in voltage dict that arent voltages
    Listkeys[i:]=listkeys[i][1:]
voltages=np.array(Listkeys) #make to matrix

voltagesum=np.sum(voltages,0)/len(voltages)

with open('voltagesum.pkl', 'wb') as f: pickle.dump(voltagesum, f)

#source times for 1 cell
# spk_input=sim.allSimData.stims.cell_3['stims']['cell_3']['Source0']
# with open('spk_input.pkl', 'wb') as f: pickle.dump(spk_input, f)


# #current
# input_current = sim.allSimData['iStim']['cell_1']
# with open('input_current.pkl', 'wb') as f: pickle.dump(input_current, f)




