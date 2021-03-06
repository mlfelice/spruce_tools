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

####################################
# Original script written by Laurel Kluber and downloaded from URL below
#   ftp://mnspruce.ornl.gov/DPH_Peat_Core_Water_Content_and_Temperature/SPRUCE_Soil_Temp.py
#   Published with following dataset: 
#     Kluber, Laurel A., Jana R. Phillips, Paul J. Hanson, Christopher W. Schadt. 
#     2016. SPRUCE Deep Peat Heating (DPH) Peat Water Content and Temperature 
#     Profiles for Experimental Plot Cores, June 2014 through June 2015. 
#     Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, 
#     U.S. Department of Energy, Oak Ridge, Tennessee, U.S.A. 
#     http://dx.doi.org/10.3334/CDIAC/spruce.029  

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
#   - Replaced strptime() with string slice in in_range() -- 10-15x faster

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

before = datetime.timedelta(days = 2) #collect data from this number of days prior to sampling 

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
   d_str = fields[0].split(' ')
   d = d_str[0]
   t = d_str[1].zfill(8)  # Add leading 0 on single hour for uniform str len
   dt = datetime.datetime(int(d[:4]), int(d[5:7]), int(d[8:10]), int(t[0:2]), 
                         int(t[3:5]))  # added time fields
   if dt >= date - before and dt <= date: #this gives us data from desired time before sampling date
    return True
   else:
    return False
  
def average(line, interval):
  sum = 0 
  for i in range(interval[0], interval[1]+1):
    sum += get_depth(line, i) 
  return sum / ((interval[1] - interval[0]) + 1)


data = []  # instantiate empty list to house the data lines (will be a list of strings)

with open(InFileName, 'r') as InFile:
  
  header = InFile.readline()  # Reads first line of input file and stores as header
  
  for line in InFile:  # Go through file line by line
    fields = filter(line)  # select only the relevant columns (fields) after splitting into list of strings
    #can probably rewrite below with list comprehension
    for date in sampling_dates:  # iterate over all dates specified at beginning of code
      if in_range(fields, date):  # checks to see if date is within range of specified dates
        p = int(fields[1])  # store plot field as p
        if p in plots:
          data.append(fields)  # if plot did match list of plots, then add the list (line) to data list (produces list of lists)
      
OutFile1 = "C:/Users/Mark/Desktop/wew_files_temp/DPH_Btemps.csv"
with open(OutFile1, 'w') as e:
  e.write(','.join(filter(header))+"\n")  # Writes header to first line of output file 1
  for fields in data:
    output = ",".join(fields)  # condense list back into a string
    e.write(output + "\n")  # write to line of output file

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
OutFile2 = ('C:/Users/Mark/Desktop/wew_files_temp/DPH_Averages.txt') # tab-separated b/c interval is tuple
with open(OutFile2, 'w') as f:
  print('TimeStamp \tPlot \tupper depth \tlower depth \taverage temperature', 
        file = f)
  for line in data:
    for i in intervals:
      print(line[0], '\t', line[1], '\t', str(i[0]), '\t', str(i[1]), '\t', 
            average(line, i),  file = f)  

## Return the average, standard deviation, maximum, and minimum temperature 
## for each DPH sampling depth increment over the 48 hour time period prior to the day of sampling.

OutFile3 = 'C:/Users/Mark/Desktop/wew_files_temp/DPH_plot_depth_date.txt'  # tab-separated b/c interval is tuple
with open(OutFile3, 'w') as g:
  print('Date \tPlot \tDepth \tMin \tMax \tAverage \tStDev \n', file = g)
  for plot in plots:
   for date in sampling_dates:
     max_depth = 200
     for interval in intervals:
       temps = [ average(sample, interval) for sample in data 
                if in_range(sample, date) and int(sample[1]) == plot ]
       if len(temps) != 0:
         avg = numpy.mean(temps)
         stdev = numpy.std(temps) 
         print(date, "\t", plot, "\t", interval, "\t",min(temps), "\t", 
               max(temps),"\t", avg, "\t", stdev, file = g)
       else:
         print("no data for" , interval, plot, date)