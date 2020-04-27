"""
SPRUCE mean annual temperature calculator

This script imports SPRUCE WEW data and calculates mean annual temp for
specified sampling depths and year. Temperature sensors are not located
at the same depths as peat sampling intervals, so this script uses 
linear interpolation at 1-cm intervals within sampling intervals to 
estimate average temperature within each interval. These are then 
averaged across all temperature readings (taken every 30 minutes) 
during the specified year. Missing values will translate to None value
in the interpolated sample temp for interval with missing value. This 
will convert to NaN and be ignored when averaging across dates.

Accepts csv files from the following URL as input:
  
Returns 3 files:
  B series temps from desired dates, 
  Average temp for sampling depth increments at all timestamps,
  Average temp for sampling depths at each sampling time.
  
Requires 'numpy' module be installed within the Python directory you 
are running this script from. Numpy may also include other 
dependencies.

This script may be run as a script or imported as a module and contains 
the following functions:
  *filter - convert line to list with date, plot and temperature fields
  *is_year - compares year in data line to target year
  *in_range - compares year from full date field to target year
  *get_depth - gets temp from shallowest sensor adjacent to spec'd depth
  *average - finds average temp across interval using linear interp
"""

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
#
# 2020-04-27: missing values were initially throwing a ValueError when 
# averaging across dates. Initial fix led to 0 values (not sure of mechanism)

#####################################

import datetime
import bisect
import numpy

print(datetime.datetime.now())

InFileName = ("C:/Users/Mark/Desktop/"
              "wew_files_temp/DPH_all_data.csv") #Change file name if starting data is different 
sampling_dates = [ 2016 ]  

plots = [ 4, 6, 7, 8, 10, 11, 13, 16, 17, 19, 20 ]

depths = numpy.array([0, 5, 10, 20, 30, 40, 50, 100, 200], dtype = int) 

intervals = [(1, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 75), 
             (75, 100), (100, 125), (125, 150), (150, 175), (175, 200)]


def is_year(fields, date):
  """
  Checks if current line is from calendar year of interest.
  
  Parameters
  ----------
  fields : str
    String representation of year (eg. '2016')
  date : datetime.datetime object
    datetime.datetime object including at least the date. This fun 
    tests for matching calendar year, not +/- 365/366 day window.


  Returns
  -------
  bool
    True if year in line matches year of target date.
    False if year in line does not match year of target date.
  """
  
  if fields == date.year: #this gives us data from desired time before sampling date
   return True
  else:
   return False

## Extract desired columns and timepoints from the full datafile(TimeStamp, plot, B_SeriesTemp)
def filter(line):
  """
  Splits text line into fields and selects date, plot, and temperatures
  from B-series temperature sensors.

  Parameters
  ----------
  line : str
    String representing one data line from SPRUCE WEW data csv. Must be
    comma separated. Cols must be TIMESTAMP [3], Plot [7], 
    TS_0__B1 [37], temp sensors from other depths [38:45]

  Returns
  -------
  list
    List containing filtered data fields: TIMESTAMP, Plot, B-series 
    temperature data.
  """
  
  columns = line.split(',')
  return [ columns[3], columns[7], columns[37], columns[38], 
          columns[39], columns[40], columns[41], columns[42], columns[43], 
          columns[44], columns[45] ]


  
def in_range(fields, date): 
  """
  Checks if current line from data list is from calendar year of 
  interest.

  Parameters
  ----------
  fields : list
    List representing one line of data from SPRUCE WEW imported data 
    after processing with filter().

  date : datetime.datetime object
    datetime.datetime object including at least the date. This fun 
    tests for matching calendar year, not +/- 365/366 day window.

  Returns
  -------
  bool
    True if year in TIMESTAMP matches year of target date.
    False if year in TIMESTAMP does not match year of target date.

  """

  d = int(fields[0][0:4])
  if d >= date: #this gives us data from desired time before sampling date
    return True
  else:
    return False

def get_depth(fields, depth): 
  """
  Gets index of data for shallowest adjacent temp sensor
  
  Parameters
  ----------
  fields : list
    List representing one line of SPRUCE WEW data filtered with 
    filter() fun.
  depth : int
    Depth at which you want to estimate temperature.

  Returns
  -------
  int
    Returns the index of the field with temp data for shallowest temp sensor 
    that is adjacent to input depth.
  """

  if depth == 0:
    return 0  # if depth is zero, just return the temp from the upper-most sensor (surface)                                
  i = bisect.bisect_left(depths, depth)  # depth is the depth between interval, i is the sensor above depth                              
  
  if i >= len(depths):  # Removed depth < 0 condition, as this is not possible This could be the case if depth was shallower than min or deeper than max depth in depths list        
    raise ValueError 
  else:
    return i

def average(temps, darray, interval):  # interval is a tuple
  """
  Calcs average temp interpolated across specified depth interval.

  Parameters
  ----------
  temps : numpy.ndarray
    Array representing temperatures from one line of SPRUCE WEW data filtered 
    with filter() fun.
  darray : numpy.array
    Array of depths corresponding to B-series temperature sensors
  interval : tuple
    Tuple representing the upper and lower bound of the peat sampling
    interval in cm.

  Returns
  -------
  float
    Returns a float value of the mean temperature across the specified 
    sampling interval. Average is calculated from values estimated at 
    1-cm intervals from linear interpolation in get_depth() fun.
  """
  sum = 0
  for r in range(interval[0], interval[1]+1):
    sum += numpy.interp(r, darray, temps)
  avg = sum / (interval[1] - interval[0] + 1)
  return avg

# Import csv data into list of lists, filtering to match dates and plots
InFile = open(InFileName,'r')

data = []  # instantiate empty list to house the data lines (will be a list of strings)

with open(InFileName, 'r') as InFile:
  header = InFile.readline()  # Reads first line of input file and stores as header
  for line in InFile:  # Iterate line by line through file
    yr = int(line[0:4])  #  select the year from data line
    if yr in sampling_dates:
      fields = filter(line)  # if in date range, filter to fields of interest
      p = int(fields[1])  # store plot field as p
      if p in plots:  # Check plot matches target plots
        data.append(fields)  # if plot matches targets, add the line (list) to data list (produces list of lists)

# Write filtered to data to csv for documentation      
BTempsCSV = "C:/Users/Mark/Desktop/wew_files_temp/DPH_Btemps.csv"
with open(BTempsCSV, 'w') as bt:
  bt.write(','.join(filter(header))+"\n")  # Writes header to first line of output file 1
  for fields in data:
    output = ",".join(fields)  # condense list back into a string
    bt.write(output + "\n")  # write to line of output file
print(datetime.datetime.now())


## This part uses the slope between temp measurements to determine the temp at each cm increment
## For each plot, the slope between the B-series temperature measurements
## ex: (Temp1, Depth1) and (Temp2, Depth2), is used to estimate the temperature for each cm depth increment at every 30-minute timestamp.

# Calculate the average temperature per DPH sampling depth increment for each plot at each 30-minute timestamp.
# **Input data are for sensor temps, output is for actual sampling intervals. Each date x plot will have different number of entries
avgs = []
missing = []
# Code chunk below prints averages in wide format, unlike original script
# TO DO: rewrite to print long format
AvgCSV = ('C:/Users/Mark/Desktop/wew_files_temp/DPH_Averages.txt') # tab-separated b/c interval is tuple
with open(AvgCSV, 'w') as av:
  print('TimeStamp \tPlot\t' + '\t'.join(map(str, intervals)), file = av)  # Print header to ouput csv
  for line in data:
    tmp = line[0:2]  # placeholder for the date and plot so reappend after the array operations (requires conversions to numeric)
    try:
      tarray = numpy.array(line[2:], dtype = float)
    except ValueError:
      missing.append(line)
    for i in intervals:
      tmp.append(average(tarray, darray, i))  # goes into the line for single results
    avgs.append(tmp)  # becomes the full list of results and their date/plot
    av.write('\t'.join(map(str, tmp)) + '\n')
print(datetime.datetime.now())
## Return the average, standard deviation, maximum, and minimum temperature 
## for each DPH sampling depth increment over the calendar year of sampling

# Average the interpolated sampling depth temps over all sampling dates over the calendar year, save to output file         
FinalCSV = 'C:/Users/Mark/Desktop/wew_files_temp/DPH_plot_depth_date.txt'  # tab-separated b/c interval is tuple
with open(FinalCSV, 'w') as fi:
  print('Date \tPlot \tDepth \tMin \tMax \tAverage \tStDev \n', file = fi)
  final_res = []
  for date in sampling_dates:  # Remove index for final version
    for plot in plots:  
      for i in range(0, len(intervals)):
        #depth = get_depth()
        temps = []  # maybe there's a numpy function for transposing instead of going line by line?
        for sample in avgs:
          if in_range(sample, date) and plot == int(sample[1]):  # Is this necessary? Seems like maybe if you're going to have multiple ranges
            temps.append(sample[i+2])
        avg = numpy.mean(temps)
        stdev = numpy.std(temps) 
        tmp2 = [date, plot, intervals[i], min(temps), max(temps), avg, stdev] 
        final_res.append(tmp2)
        fi.write('\t'.join(map(str, tmp2)) + '\n')
print(datetime.datetime.now())  # Would probably be most helpful to have the measurement number. Then you could easily find the entry in question