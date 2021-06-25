# FiberTest
These packages perform measurements of PMT signal along a wavelength shifting fiber illuminated by a laser. 
The hardware setup is as follow:
A rectangular black box 2.55 x 0.40 x 0.34 m contains a rail with a moving platform.
A laser illumination system sits on the platform. 
The platform can move along the rail, controlled by an Arduino board. 

ft_arduino and fibertest contains the base functions to move the platform.

am_reader contains functions to read a pair of ammeter readings.
DAQ integrates the functionality of ft_arduino, am_reader and save the output to csv format. 

RunDAQ.py invokes DAQ to perform measurment of a WLS fibers

protofit.ino: Arduino Uno software optimized by Dave Munson of Universiy of Rochester. 
