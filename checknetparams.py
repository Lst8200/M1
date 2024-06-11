#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 23:32:04 2024

@author: latavia
"""
import numpy as np
from netpyne import specs
import pickle, json

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

netParams.version = 56

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------
netParams.scale = cfg.scale # Scale factor for number of cells
netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder' # cylindrical (column-like) volume

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.scaleConnWeight = 1.0 # Connection weight scale factor (default if no model specified)
netParams.scaleConnWeightModels = {'HH_simple': 1.0, 'HH_reduced': 1.0, 'HH_full': 1.0} #scale conn weight factor for each cell model
netParams.scaleConnWeightNetStims = 1.0 #0.5  # scale conn weight factor for NetStims
netParams.defaultThreshold = 0.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 2.0 # default conn delay (ms)
netParams.propVelocity = 500.0 # propagation velocity (um/ms)
netParams.probLambda = 100.0  # length constant (lambda) for connection probability decay (um)
netParams.defineCellShapes = True  # convert stylized geoms to 3d points



#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------
cellModels = ['HH_simple', 'HH_reduced', 'HH_full']
layer = {'2':[0.1,0.29],'24':[0.1,0.37],'5B': [0.47,0.8]}  # normalized layer boundaries

#------------------------------------------------------------------------------
## Load cell rules previously saved using netpyne format
cellParamLabels = ['IT2_reduced','IT5B_reduced', 'PT5B_reduced',
   'PV_simple', 'SOM_simple']# 'VIP_reduced', 'NGF_simple','PT5B_full'] #  # list of cell rules to load from file
loadCellParams = cellParamLabels
saveCellParams = False #True

for ruleLabel in loadCellParams:
    netParams.loadCellParamsRule(label=ruleLabel, fileName=ruleLabel+'_cellParams.pkl')
    
    # Adapt K gbar
    if ruleLabel in ['IT2_reduced',  'IT5B_reduced']:
        cellRule = netParams.cellParams[ruleLabel]
        for secName in cellRule['secs']:
            for kmech in [k for k in cellRule['secs'][secName]['mechs'].keys() if k.startswith('k') and k!='kBK']:
                cellRule['secs'][secName]['mechs'][kmech]['gbar'] *= cfg.KgbarFactor 

#------------------------------------------------------------------------------
# Specification of cell rules not previously loaded
# Includes importing from hoc template or python class, and setting additional params

#------------------------------------------------------------------------------
# Reduced cell model params (6-comp) 
reducedCells = {  # layer and cell type for reduced cell models
    'IT2_reduced':  {'layer': '2',  'cname': 'CSTR6', 'carg': 'BS1578'}, 
    'IT4_reduced':  {'layer': '4',  'cname': 'CSTR6', 'carg': 'BS1578'},
    'IT5A_reduced': {'layer': '5A', 'cname': 'CSTR6', 'carg': 'BS1579'},
    'IT5B_reduced': {'layer': '5B', 'cname': 'CSTR6', 'carg': 'BS1579'},
    'PT5B_reduced': {'layer': '5B', 'cname': 'SPI6',  'carg':  None},
    'IT6_reduced':  {'layer': '6',  'cname': 'CSTR6', 'carg': 'BS1579'},
    'CT6_reduced':  {'layer': '6',  'cname': 'CSTR6', 'carg': 'BS1578'}}

reducedSecList = {  # section Lists for reduced cell model
    'alldend':  ['Adend1', 'Adend2', 'Adend3', 'Bdend'],
    'spiny':    ['Adend1', 'Adend2', 'Adend3', 'Bdend'],
    'apicdend': ['Adend1', 'Adend2', 'Adend3'],
    'perisom':  ['soma']}


#------------------------------------------------------------------------------
## PV cell params (3-comp)
if 'PV_simple' not in loadCellParams:
    cellRule = netParams.importCellParams(label='PV_simple', conds={'cellType':'PV', 'cellModel':'HH_simple'}, 
      fileName='FS3.hoc', cellName='FScell1', cellInstance = True)
    cellRule['secLists']['spiny'] = ['soma', 'dend']
    netParams.addCellParamsWeightNorm('PV_simple', 'conn/PV_simple_weightNorm.pkl', threshold=cfg.weightNormThreshold)
    if saveCellParams: netParams.saveCellParamsRule(label='PV_simple', fileName='PV_simple_cellParams.pkl')


#------------------------------------------------------------------------------
## SOM cell params (3-comp)
if 'SOM_simple' not in loadCellParams:
    cellRule = netParams.importCellParams(label='SOM_simple', conds={'cellType':'SOM', 'cellModel':'HH_simple'}, 
      fileName='LTS3.hoc', cellName='LTScell1', cellInstance = True)
    cellRule['secLists']['spiny'] = ['soma', 'dend']
    netParams.addCellParamsWeightNorm('SOM_simple', 'conn/SOM_simple_weightNorm.pkl', threshold=cfg.weightNormThreshold)
    if saveCellParams: netParams.saveCellParamsRule(label='SOM_simple', fileName='SOM_simple_cellParams.pkl')




#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
## load densities
with open('cellDensity.pkl', 'rb') as fileObj: density = pickle.load(fileObj)['density']

## Local populations
netParams.popParams['IT2']  =   {'cellModel': cfg.cellmod['IT2'],  'cellType': 'IT', 'ynormRange': layer['2'], 'density': 0.5*density[('M1','E')][0]}
netParams.popParams['SOM2'] =   {'cellModel': 'HH_simple',         'cellType': 'SOM','ynormRange': layer['24'], 'density': 0.5*density[('M1','SOM')][5]}
netParams.popParams['PV2']  =   {'cellModel': 'HH_simple',         'cellType': 'PV', 'ynormRange': layer['24'], 'density': 0.5*density[('M1','PV')][5]}
netParams.popParams['IT5B'] =   {'cellModel': cfg.cellmod['IT5B'], 'cellType': 'IT', 'ynormRange': layer['5B'], 'density': 0.125*density[('M1','E')][3]}
netParams.popParams['PT5B'] =   {'cellModel': cfg.cellmod['PT5B'], 'cellType': 'PT', 'ynormRange': layer['5B'], 'density': 0.125*density[('M1','E')][3]}
netParams.popParams['SOM5B'] =  {'cellModel': 'HH_simple',         'cellType': 'SOM','ynormRange': layer['5B'], 'density': 0.25*density[('M1','SOM')][3]}
netParams.popParams['PV5B']  =  {'cellModel': 'HH_simple',         'cellType': 'PV', 'ynormRange': layer['5B'], 'density':0.25* density[('M1','PV')][3]}

#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 15, 'tau2NMDA': 150, 'e': 0}
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3*cfg.AMPATau2Factor, 'e': 0}
netParams.synMechParams['GABAB'] = {'mod':'MyExp2SynBB', 'tau1': 3.5, 'tau2': 260.9, 'e': -93} 
netParams.synMechParams['GABAA'] = {'mod':'MyExp2SynBB', 'tau1': 0.07, 'tau2': 18.2, 'e': -80}
netParams.synMechParams['GABAASlow'] = {'mod': 'MyExp2SynBB','tau1': 2, 'tau2': 100, 'e': -80}
netParams.synMechParams['GABAASlowSlow'] = {'mod': 'MyExp2SynBB', 'tau1': 200, 'tau2': 400, 'e': -80}

ESynMech = ['AMPA', 'NMDA']
SOMESynMech = ['GABAASlow','GABAB']
SOMISynMech = ['GABAASlow']
PVSynMech = ['GABAA']



#------------------------------------------------------------------------------
# stimulus
#------------------------------------------------------------------------------


#sinusoidal current:
#create Source0 as stimSourceParams, can record current
# netParams.stimSourceParams['Source0'] = {'type': 'NetStim', 'rate': 10, 'noise': .1, 'start': 5}
# netParams.synMechParams['synSource0'] = {'mod': 'Icos','amp':15,'f':15,'n':500}
# netParams.stimTargetParams['Source0->IT2'] = {'source': 'Source0', 'sec':'soma', 'loc': 0.5,'conds': {'pop':['IT2']}, 'weight': 1, 'delay': 5,'synMech': 'synSource0'}

# #or create Source0 as artificial cells == pop params, unsure how to record current
# netParams.popParams['Source0'] = {'cellModel': 'NetStim', 'cellType': 'source0','ynormRange': layer['2'], 'numCells':1000}
# #Load the Icos mod to source0
# netParams.synMechParams['synSource0'] = {'mod': 'Icos','amp':.6,'f':10,'n':50}


#- - - - -
#couldnt figure out ramped/sawtooth current but tried here, need to figure out vecstim ig: using stimSourceParams:
    
    #first get iclamp working
# netParams.stimSourceParams['Source1'] = {'type': 'IClamp', 'amp': .5, 'dur': 300, 'delay': 50}
# netParams.stimTargetParams['Source1->IT2'] = {'source': 'Source1', 'conds': {'pop': ['IT2']}, 'sec': 'soma', 'loc': 0.5,'synMech': ESynMech}

    #then try vecstims again:
    #netParams.popParams['artif3'] = {'cellModel': 'VecStim', 'numCells': 100, 'spkTimes': spkTimes, 'pulses': pulses}  # VecStim with spike times

#use popParams if wanting specific spike times
# create custom list of spike times
spkTimes = list(range(0,100,5)) + [13, 55, 70]

# create list of pulses (each item is a dict with pulse params)
pulses = [{'start': 10, 'end': 100, 'rate': 2, 'noise': 0.5},
        {'start': 50, 'end': 60, 'rate': 1, 'noise': 0.0}]

netParams.popParams['Source1'] = {'cellModel': 'VecStim','numCells': 1000, 'spkTimes': spkTimes, 'pulses': pulses,'ynormRange': layer['2']}

#- - - - -
# #noise
# netParams.stimSourceParams['NetStims'] = {'type': 'NetStim', 'rate': 5, 'noise': .5, 'start': 1}

#     #IT
# netParams.stimTargetParams['NetStim->IT'] = {'source': 'NetStims', 'sec':'soma', 'loc': 0.5,'conds': {'cellType':['IT']}, 'weight': .2, 'delay': 5,'synMech': ESynMech}

#     #PT
# netParams.stimTargetParams['NetStim->PT'] = {'source': 'NetStims', 'sec':'soma', 'loc': 0.5, 'conds': {'cellType':['PT']},'weight': .2, 'delay': 5,'synMech': ESynMech}

#     #SOM
# netParams.stimTargetParams['NetStim->SOM'] = {'source': 'NetStims', 'sec':'soma', 'loc': 0.5,'conds': {'cellType':['SOM']}, 'weight': .2, 'delay': 5,'synMech': SOMESynMech,}

#     #PV
# netParams.stimTargetParams['NetStim->PV'] = {'source': 'NetStims', 'sec':'soma', 'loc': 0.5,'conds': {'cellType':['PV']}, 'weight': .2, 'delay': 5,'synMech': PVSynMech}
 

#------------------------------------------------------------------------------
#connectivity params
#------------------------------------------------------------------------------

##E->I
netParams.connParams['E->I'] = {
    'preConds': {'cellType': ['IT','PT']}, 'postConds': {'cellType': ['PV', 'SOM']},
    'probability':  '(1e-4)*dist_3D',
    'synMech': ESynMech,                #  ESynMech = ['AMPA','NMDA']
    # 'probability': .1,
    'weight': 1,                  # synaptic weight
    'delay': 5,                       # transmission delay (ms)
    'sec': 'soma'}                    # section to connect to} 

##IT->E
netParams.connParams['IT->E'] = {
    'preConds': {'cellType': 'IT'}, 'postConds': {'cellType': ['IT','PT']},
    'probability':   '(1e-4)*dist_3D',
    'synMech': ESynMech,                #  ESynMech = ['AMPA','NMDA']
    # 'probability': .1,
    'weight': 1,                  # synaptic weight
    'delay': 5,                       # transmission delay (ms)
    'sec': 'soma'}                    # section to connect to}                    

#PT->PT
netParams.connParams['PT->PT'] = {
    'preConds': {'cellType': 'PT'}, 'postConds': {'cellType': 'PT'},
    'probability':   '(1e-4)*dist_3D',
    'synMech': ESynMech,                #  ESynMech = ['AMPA','NMDA']
    'weight': 1,                  # synaptic weight
    'delay': 5,                       # transmission delay (ms)
    'sec': 'soma'}   

##S->E
netParams.connParams['S->E'] = {
    'preConds': {'cellType':'SOM'}, 'postConds': {'cellType': ['IT','PT']},
    'probability':   '(1e-4)*dist_3D',
    'synMech': SOMESynMech,
    # 'probability': .1,
    'weight': 1,                  # synaptic weight
    'delay': 5,                       # transmission delay (ms)
    'sec': 'soma'}                    # section to connect to} 
##S->I
netParams.connParams['S->I'] = {
    'preConds': {'cellType':'SOM'}, 'postConds': {'cellType': ['PV', 'SOM']},
    'probability':   '(1e-4)*dist_3D',
    'synMech': SOMISynMech,
    # 'probability': .1,
    'weight': 1,                  # synaptic weight
    'delay': 5,                       # transmission delay (ms)
    'sec': 'soma'}                    # section to connect to}      
  

      ##P->[E,I]
netParams.connParams['PV->All'] = {
    'preConds': {'cellType':'PV'}, 'postConds': {'cellType': ['PV', 'SOM','IT','PT']},
    'probability': '(1e-4)*dist_3D',
    'synMech': PVSynMech,
    # 'probability': .1,
    'weight': 1,                  # synaptic weight
    'delay': 5,                       # transmission delay (ms)
    'sec': 'soma'}                    # section to connect to}      
       

# netParams.connParams['P->E'] = {
#     'preConds': {'cellType':'PV'}, 'postConds': {'cellType': ['IT','PT']},
#     'probability': '(1e-4)*dist_3D',   # max number of incoming conns to cell
#     'synMech': PVSynMech,
#     # 'probability': .1,
#     'weight': 1,                  # synaptic weight
#     'delay': 5,                       # transmission delay (ms)
#     'sec': 'soma'}                    # section to connect to}     


#if using source0 as stim, don't need this?
# Connect source1 to the cells
# Note that the 'weight' is a function of 3D distance (dist_3D)
# See http://netpyne.org/reference.html#functions-as-strings
# You can also set the delay as a function of distance
netParams.connParams['ConnSource1'] = {
    'preConds': {'cellType': 'Source1'},'postConds': {'pop': ['IT2']},
    'synMech': ESynMech,
    'probability': 1,
    'delay': 0, #'dist_3D/10',
    'weight': 1}#}  # 1.0}


#------------------------------------------------------------------------------
# pulse currents
#------------------------------------------------------------------------------
#netParams.popParams['PV5B']  =  {'cellModel': 'HH_simple', 'cellType': 'PV', 'ynormRange': layer['5B'], 'density':0.25* density[('M1','PV')][3]}
# Create a single-cell population to hold current source Source0

#"note if netstims are defined in popParams (vs stimSourceParams) they are not considered stims (ie. dont need cfg.recordStims=1)"
#unsure how to collect current trace this way? so wont use popParams:
    #netParams.popParams['Source0'] = {'cellModel': 'NetStim', 'cellType': 'source0','ynormRange': layer['2'], 'numCells':1000}
    #Load the Icos mod to source0
    #netParams.synMechParams['synSource0'] = {'mod': 'Icos','amp':.6,'f':10,'n':50}
