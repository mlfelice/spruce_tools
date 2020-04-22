#!/usr/bin/env python

# This python script will parse desired temperature data from the full DPH dataset.
# Code returns 3 files: 
		# B series temps from desired dates, 
		# Average temp for sampling depth increments at all timestamps,
		# Average temp for sampling depths at each sampling time.
# To run script:
		# Save this script in the same directory as the data file you want to parse.
		# Make sure starting file name, sampling dates, and before date are correct in the script
		# Open terminal window and cd to directory with data and script
		# Type chmod "SPRUCE_Soil_Temp.py"
		# Type "./SPRUCE_Soil_Temp.py" and script will begin to run.
# if you have questions or errors contact Laurel.Kluber@gmail.com		

#############
# This script has been updated by Mark Felice on 10/17/2019 in order to work 
# with 2016 data sets.
#   - Updated plots: added plots 7 and 21 and ordered ascending
#   - Changed dates to reflect 2016 sampling dates
#   - Changed the filter() function so that columns correspond to 2016 data
#     - 2, 6, 24-32 in original script
#   - Changed print statements to Python 3 format
#   - Still written for sensor B
#   - Changed InFileName: originally "DPH_all_data.csv"
#   - Cleaned up format for consistency throughout and wrap lines at 80 char
#   - Changed datetime format to '%Y/%m/%d %H:%M' from '%Y-%m-%d %H:%M'

# 2020-01-09: changed the in_range function so that this calculates mean annual
# temperature for the year in which the date falls

#####################################

import datetime
import bisect
import numpy

InFileName = ("C:/Users/Mark/Desktop/"
              "wew_files_temp/DPH_all_data.csv") #Change file name if starting data is different 
sampling_dates = [ datetime.datetime(2016, 6, 13, 16),
                   datetime.datetime(2016, 7, 15, 16),  # MF: Not sure of the July and October sampling dates
                   datetime.datetime(2016, 8, 23, 16),
                   datetime.datetime(2016, 10, 15, 16) ]  

plots = [ 4, 6, 7, 8, 10, 11, 13, 16, 17, 19, 20 ]

depths = [0, 5, 10, 20, 30, 40, 50, 100, 200] 

intervals = [(1, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 75), 
             (75, 100), (100, 125), (125, 150), (150, 175), (175, 200)]

## Extract desired columns and timepoints from the full datafile(TimeStamp, plot, B_SeriesTemp)

def filter(line):
  columns = line.split(',')
  return [ columns[3], columns[7], columns[37], columns[38], 
          columns[39], columns[40], columns[41], columns[42], columns[43], 
          columns[44], columns[45] ]

def in_range(fields, date): #this filters timepoint based on sampling date of interest
   d = datetime.datetime(int(fields[0][:4]), int(fields[0][5:7]), int(fields[0][8:10])) 
   if d.year == date.year: #this gives us data from desired time before sampling date
    return True
   else:
    return False

def average(line, interval):
  sum = 0 
  for i in range(interval[0], interval[1]+1):
    sum += get_depth(line, i) 
  return sum / ((interval[1] - interval[0]) + 1)

InFile = open(InFileName,'r')

OutFile1 = "C:/Users/Mark/Desktop/wew_files_temp/DPH_Btemps.csv"
e = open(OutFile1, 'w') 

# The input file has a header, copy it to the output.
header = InFile.readline()
e.write(','.join(filter(header))+"\n")

data = []

for line in InFile: 
  fields = filter(line)
  for date in sampling_dates:
    if in_range(fields, date):
      break 
  else:
    continue  
  p = int(fields[1]) 
  if p not in plots:
    continue
  
  data.append(fields)
  output = ",".join(fields)
  e.write(output + "\n")   

InFile.close()      
e.close()

## This part uses the slope between temp measurements to determine the temp at each cm increment
## For each plot, the slope between the B-series temperature measurements
## ex: (Temp1, Depth1) and (Temp2, Depth2), is used to estimate the temperature for each cm depth increment at every 30-minute timestamp.

def get_depth(fields, depth): 
  if depth == 0:
    return fields[2]                                            
  i = bisect.bisect_left(depths, depth)                                         
  if depth < 0 or i >= len(depths):          
    raise ValueError                       

  lo = float(fields[2+(i-1)])    
  hi = float(fields[2+i])        
  m = (hi - lo) / (depths[i] - depths[i - 1])
  result = lo + ((depth - depths[i - 1]) * m)
  return result


## Calculate the average temperature per DPH sampling depth increment for each plot at each 30-minute timestamp.

OutFile2 = ("C:/Users/Mark/Desktop/wew_files_temp/DPH_Averages.txt") # tab-separated b/c interval is tuple
f = open(OutFile2, 'w')

print("TimeStamp \tPlot \tupper depth \tlower depth \taverage temperature \n", 
      file = f)
for line in data:
  for i in intervals:
    print(line[0], "\t", line[1], "\t", str(i[0]), "\t", str(i[1]), "\t", 
          average(line, i),  file = f) 

f.close()

## Return the average, standard deviation, maximum, and minimum temperature 
## for each DPH sampling depth increment over the 48 hour time period prior to the day of sampling.

OutFile3 = "C:/Users/Mark/Desktop/wew_files_temp/DPH_plot_depth_date.txt"  # tab-separated b/c interval is tuple
g = open(OutFile3, 'w')
print("Date \tPlot \tDepth \tMin \tMax \tAverage \tStDev \n", file = g)
for plot in plots:
   for date in sampling_dates:
     max_depth = 200
     for interval in intervals:
       temps = [ average(sample, interval) for sample in data 
                if in_range(sample, date) and int(sample[1]) == plot ]
       if len(temps) == 0:
         print("no data for" , interval, plot, date)
         continue
       avg = numpy.mean(temps)
       stdev = numpy.std(temps) 
       print(date, "\t", plot, "\t", interval, "\t",min(temps), "\t", 
             max(temps),"\t", avg, "\t", stdev, file = g)
g.close()
