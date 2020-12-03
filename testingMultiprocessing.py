# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 16:17:24 2020

@author: Ben
"""

import math as m
from multiprocessing import Pool
import time


pipeLength = 69.28
resHeight = 30
const1 = .15
const2 = .15
g = 9.81

def calcVelocity(flowVolume, diameter):
    return (flowVolume/ ((diameter / 2) * (diameter / 2) * m.pi))

def calcFriction(mass, f, length, velocity, diameter):
    return ((mass * f * length * velocity * velocity) / (2 * diameter))

def calcBend(mass, k, velocity):
    return ((mass * k * velocity * velocity) / 2)

def calcMass(height, depth, turbineEff, f, length, vDown, k1, k2, diameter):
    Eout = 120 # in Megawatt hours
    Eout = Eout * 3600000000 # convert to joules
    rightSide = Eout + Eout * (1/turbineEff - 1)
    leftSide = (g*(height + depth/2) - 
                calcFriction(1, f, length, vDown, diameter) - 
                calcBend(1, k1, vDown) - calcBend(1, k2, vDown))
    return (rightSide / leftSide)
                            
    
def calcEin(pumpEff, turbineEff, mass, f, length, vUp, diameter, vDown, k1, k2):
    Eout = 120 # in Megawatt hours
    Eout = Eout * 3600000000 # convert to joules
    # summing the energy consumed by factors dependent on Eout
    outDependentConsumed = (calcFriction(mass, f, length, vUp, diameter) + 
                            calcFriction(mass, f, length, vDown, diameter) + 
                            calcBend(mass, k1, vDown) + calcBend(mass, k1, vUp)
                            + calcBend(mass, k2, vDown) + calcBend(mass, k2, vUp)
                            + ((1/turbineEff - 1) * Eout) )
    Ein = ((outDependentConsumed + Eout) / pumpEff) 
    return (Ein / 3600000000)

def calcArea(mass, depth):
    return(mass / (1000 * depth))

def calcTime(flowVolume, mass):
    return((mass / (1000 * flowVolume)) / 3600 )

def doTheThing(pumpFlowVolume, pumpEfficiency, pipeDiameter, pipeF, resDepth, turbineEfficiency, turbineFlowVolume):
    velocityUp = calcVelocity(pumpFlowVolume,pipeDiameter)
    velocityDown = calcVelocity(turbineFlowVolume, pipeDiameter)
    theMass = calcMass(resHeight,resDepth,turbineEfficiency,pipeF,pipeLength,
                   velocityDown,const1,const2,pipeDiameter)
    initialE = calcEin(pumpEfficiency, turbineEfficiency, theMass, pipeF, 
                   pipeLength, velocityUp, pipeDiameter, velocityDown, const1, const2)
    return([initialE, theMass])

def letsTest(pumpFlowVolume):
    for pumpEfficiency in [.80, .83, .86, .89, .92]:
        for pipeDiameter in [.1,.25,.5,.75,1,1.25,1.5,1.75,2,2.25,2.5,2.75,3]:
            for pipeF in [.05,.03,.02,.01,.005,.002]:
                for resDepth in range(5,21):
                    for turbineEfficiency in [.83,.86,.89,.92,.94]:
                        for turbineFlowVolume in range(5,100):
                            value = doTheThing(pumpFlowVolume, pumpEfficiency, pipeDiameter, pipeF, resDepth, turbineEfficiency,turbineFlowVolume)
                            if (value[0] > 0 and value[0] < 150):
                                surfaceArea = calcArea(value[1],resDepth)
                                if (surfaceArea < 282743):
                                    fillTime = calcTime(pumpFlowVolume, value[1])
                                    if (fillTime <= 24.0):
                                        if(calcTime(turbineFlowVolume, value[1]) <= 12.0):
                                            outputString = "{:15.2f} {:18d} {:15.2f}  {:7.3f} {:7.2f} {:20.2f} {:20d} {:15.2f}  {:10.4f}\n".format(pumpEfficiency, pumpFlowVolume, pipeDiameter, 
                                                         pipeF, resDepth, turbineEfficiency,turbineFlowVolume, surfaceArea, value[0])
                                            fid2.write(str(outputString))
currentTime = time.time()
fid2 = open('./AcanIdoitright', 'w')                        
fid2.write("Pump Efficiency   Pump Flow Volume   Pipe Diameter   Pipe f   Depth   Turbine Efficiency  Turbine Flow Volume    Surface Area   Ein\n")
if __name__ == '__main__':
    p = Pool(processes=60)
    data = p.map(letsTest, range(5,100))
    p.close()
    print('done')
    print(time.time() - currentTime)
    fid2.close()


