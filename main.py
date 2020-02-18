#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import serial

# Write your program here
ev3 = EV3Brick()
s=serial.Serial("/dev/ttyACM0",9600)
ev3.speaker.beep()


#functions
def zeroListMaker(n):
     zeroList = [0]*n
     return zeroList

def calibrateNote(noteName, calibrateLength):
     #start calibrate
     ev3.speaker.say("Start calibrating note "+noteName)

     #writes average data to noteName.txt
     noteData = zeroListMaker(calibrateLength)
     i = 0
     
     #takes data for note until array fills
     while True:
          try:
               data=s.read(s.inWaiting()).decode("utf-8")
               data = data.splitlines()
               if i == len(noteData):
                    print('stopped')
                    break
               if len(data) == 1:
                    imu = data[0].split(',')
                    if len(imu) == 6:
                         if float(imu[2]) >= .2:
                              print('rest position')
                              print(imu[2])
                         elif float(imu[2]) <= .2:
                              print('taking data')
                              print(imu[2])
                              noteData[i] = imu
                              i = i + 1
          except Exception as e: print(e)
    

     #save to file
     with open(noteName+".txt",'w+') as outFile:
          for line in noteData:
               outFile.write(str(line) + '\n')
          outFile.close
     
     ev3.speaker.say("Done calibrating note "+noteName)

def parseNote(noteName):
     fileName = noteName + '.txt'
     idealNote = zeroListMaker(6)

     fin = open(fileName)
     lineCount = 0
     for line in fin:
          lineCount = lineCount + 1
          line = line.strip()
          line = line[2:-2]
          line = line.split("', '")
          for i in range(0,6):
               if line[i] == "":
                    line[i] = 0
               idealNote[i] = float(idealNote[i])+float(line[i])
     for i in range(0,6):
          idealNote[i] = idealNote[i]/lineCount

     return idealNote

def knn(imu,idealMatrix):
     minDist = 100000000
     min_j = 0
     for j in range(0,len(idealMatrix)):
          idealNote = idealMatrix[j]
          currTotal = 0
          for i in range(0,3):
               currTotal += (float(imu[i])-float(idealNote[i]))**2
          currTotal = currTotal**(1/2)
          if (currTotal < minDist):
               minDist = currTotal
               min_j = j

     chosenNote = mapNote(min_j)

     return chosenNote

def mapNote(index):
     if index == 0:
          note = 'A'
     elif index == 1:
          note = 'B'
     elif index == 2:
          note = 'C'
     elif index == 3:
          note = 'D'
     elif index == 4:
          note = 'E'
     elif index == 5:
          note = 'F'
     elif index == 6:
          note = 'G'
     return note


# Calibration of each note
calLength = 100
calibrateNote('A',calLength)
calibrateNote('B',calLength)
calibrateNote('C',calLength)
calibrateNote('D',calLength)
calibrateNote('E',calLength)
calibrateNote('F',calLength)
calibrateNote('G',calLength)


# Parse note files
#reads file and decides what a perfect 'A' note looks like etc.
ev3.speaker.say("Processing")
A_ideal = parseNote('A')
print(A_ideal)
B_ideal = parseNote('B')
print(B_ideal)
C_ideal = parseNote('C')
print(C_ideal)
D_ideal = parseNote('D')
print(D_ideal)
E_ideal = parseNote('E')
print(E_ideal)
F_ideal = parseNote('F')
print(F_ideal)
G_ideal = parseNote('G')
print(G_ideal)

idealMatrix = [A_ideal,B_ideal,C_ideal,D_ideal,E_ideal,F_ideal,G_ideal]

# Run a music (for each note decide what it is closest to and play that note)
ev3.speaker.say("Begin composing")
while True:
     #try:
     data=s.read(s.inWaiting()).decode("utf-8")
     data = data.splitlines()
     if len(data) == 1:
          imu = data[0].split(',')
          if len(imu) == 6:
               if float(imu[2]) >= .2:
                    print('rest position')
               elif float(imu[2]) <= .2:
                    chosenNote = knn(imu,idealMatrix)
                    ev3.speaker.say(chosenNote)
                    ev3.speaker.play_notes([chosenNote+'4/4'],tempo=120)

     #except Exception as e: print(e)



#---------------------------------------------------------------------
#notes = ['G3/8','G3/8', 'G3/8', 'Eb3/2','R/8','F3/8','F3/8', 'F3/8', 'D3/2']
#ev3.speaker.play_notes(notes, tempo=120)


# while True:
#      try:
#           data=s.read(s.inWaiting()).decode("utf-8")
#           data = data.splitlines()
#           if len(data) == 1:
#                imu = data[0].split(',')
#                if len(imu) == 6:
#                     print(imu)
#                     if float(imu[2]) >= .2:
#                          print('z posi or neg')

#      except Exception as e: print(e)


#old stuff
# for i in range(10):
#      data=s.read(s.inWaiting()).decode("utf-8")
#      #print('size = %d, buffer = %d' % (len(data),s.inWaiting()))
#      data = data.splitlines()
#      imu = data[:-2]
#      print(imu)

#decider code
# elif float(imu[0]) > .22:
#      if float(imu[1]) > .22:
#           print('+, +')
#           #ev3.speaker.beep(440,500)
#           #ev3.speaker.play_notes(notes[0], tempo=120)
#      elif float(imu[1]) < -.22:
#           print('+, -')
# elif float(imu[0]) < -.22:
#      if float(imu[1]) > .22:
#           print('-, +')
#      elif float(imu[1]) < -.22:
#           print('-, -')