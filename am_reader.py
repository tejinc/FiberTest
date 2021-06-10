#!/usr/local/bin/python3.8

import pyvisa
import time
import numpy

# define resource manager
rm = pyvisa.ResourceManager()

# list resources
equipment_names = [ r for r in rm.list_resources() if "GPIB" in r ]

#he way it's defined, resource 1 is the digital and the resource 2 is the analog scope.
equipments=tuple([ rm.open_resource(n) for n in equipment_names])


ammeter1, ammeter2=equipments

print(ammeter1,ammeter2)

#the code used to initialize digital ammeter
def initialize( am, range=5e-6 ):
  write_commands = [ "*RST", "SYST:ZCH ON", "CURR:RANG %s"%(str(range)), "INIT", "SYST:ZCOR:ACQ", "SYST:ZCOR ON", "CURR:RANG:AUTO ON", "SYST:ZCH OFF" ]
  for command in write_commands:
    #print(command)
    #time.sleep(1)
    #print(am.write(command))
    am.write(command)
    

def getDigitalReading( am ):
  ret = am.query("READ?")
  #print( ret )
  return float( ret.split(",")[0][:-1] )


def getAnalogReading( am ):
  ret = am.query("READ?")
  #print( ret )
  return float(ret[4:])

def getAvgStdev(readingfunc, am, n=10 ):
  """calculate average and stdev for n measurements

  Args:
      readingfunc (functional): a reading function to parse ammeter outut
      am (GPIB0 object): the ammeter object
      n (int, optional): number of measurements in one go. Defaults to 10.

  Returns:
      tuple(double,double): average and stdev
  """
  readings=[ readingfunc(am) for i in range(n)]
  avg=numpy.average(readings)
  stdev=numpy.std(readings)
  return (avg,stdev)

initialize(ammeter1, "2e-5")
initialize(ammeter2, "2e-5")

#print( getAvgStdev(getDigitalReading, ammeter1, 10) )
#print( getAvgStdev(getAnalogReading, ammeter2, 10) )


