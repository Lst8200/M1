#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 23:51:32 2024

@author: latavia
"""

"""
This script generates and runs a simulation of 100 neurons attached to two
current sources at different locations.

The amplitudes of the current sources into any given cell are dependent on 
the 3D distance between the current source and the cell.

This script requires you to download and compile "ipulse4.mod" in advance.  
This mod file is a modified version of "ipulse3.mod" as found here:
https://neuron.yale.edu/neuron/faq/general-questions#faq-I-want-a-current-clamp-that-will-generate-a-pulse-when-I-send-it-an-event,-or-that-I-can-use-to-produce-pulses-at-precalculated-times.

"""

from netpyne import specs, sim

netParams = specs.NetParams()
simConfig = specs.SimConfig()


# Create the cell type for the actual cells
netParams.cellParams['CellType0'] = {
    "secs": {
        "soma": {
            "geom": {"diam": 20, "L": 20, "Ra": 100.0, "cm": 1},
            "mechs": {"pas": {}}
        }
    }
}

# Create the population of actual cells (default size is 100um cube)
netParams.popParams['Population0'] = {
    "cellModel": "",
    "cellType": "CellType0",
    "numCells": 100
}

# Create a single-cell population to hold current source Source0
# located at the origin
netParams.popParams['Source0'] = {
    "cellModel": "NetStim",
    "cellType": "source0",
    "numCells": 1,
    "interval": 200,
    "start": 100,
    "xRange": [0, 0.1],
    "yRange": [0, 0.1],
    "zRange": [0, 0.1],

}

# Create a single-cell population to hold current source Source1
# located at the opposite corner
netParams.popParams['Source1'] = {
    "cellModel": "NetStim",
    "cellType": "source1",
    "numCells": 1,
    "interval": 200,
    "start": 200,
    "xRange": [99.9, 100],
    "yRange": [99.9, 100],
    "zRange": [99.9, 100],
}

# Load the Ipulse4 mod to source0 and set its duration to 10
netParams.synMechParams['synSource0'] = {
    "mod": "Ipulse4",
    "dur": 10,
}

# Load the Ipulse4 mod to source1 and set its duration to 20
netParams.synMechParams['synSource1'] = {
    "mod": "Ipulse4",
    "dur": 20,
}

# Connect source0 to the cells
# Note that the 'weight' is a function of 3D distance (dist_3D)
# See http://netpyne.org/reference.html#functions-as-strings
# You can also set the delay as a function of distance
netParams.connParams['ConnSource0'] = {
    "preConds": {"pop": ["Source0"]},
    "postConds": {"pop": ["Population0"]},
    "synMech": "synSource0",
    "synsPerConn": 1,
    "probability": 1.0,
    "delay": 0.0, # "dist_3D/10"
    "weight": "1.0/(dist_3D/10)",  # 1.0
}

# Connect source1 to the cells
netParams.connParams['ConnSource1'] = {
    "preConds": {"pop": ["Source1"]},
    "postConds": {"pop": ["Population0"]},
    "synMech": "synSource1",
    "synsPerConn": 1,
    "probability": 1.0,
    "delay": 0.0, # "dist_3D/10"
    "weight": "0.5/(dist_3D/10)",  # 0.5
}

# Set up the sim config
simConfig.duration = 500
simConfig.recordCells = [0, 1, 2]
simConfig.recordTraces = {"V_soma": {"sec": "soma", "loc": 0.5, "var": "v"}}

# Run the simulation
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

# Plot some results
#sim.analysis.plotTraces(oneFigPer='trace', overlay=True, saveFig=True, showFig=True)
#sim.analysis.plot2Dnet(saveFig=True, showFig=True)
#sim.analysis.plotRaster(include=['all'],showFig=True)
