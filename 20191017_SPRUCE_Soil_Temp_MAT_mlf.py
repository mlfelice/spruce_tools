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

#####################################

import datetime
import bisect
import numpy

print(datetime.datetime.now())

InFileName = ("C:/Users/Mark/Desktop/"
              "wew_files_temp/DPH_all_data.csv") #Change file name if starting data is different 
sampling_dates = [ #datetime.datetime(2016, 6, 13, 16),
                   #datetime.datetime(2016, 7, 15, 16),  # MF: Not sure of the July and October sampling dates
                   #datetime.datetime(2016, 8, 23, 16),
                   datetime.datetime(2016, 10, 15, 16) ]  

plots = [ 4, 6, 7, 8, 10, 11, 13, 16, 17, 19, 20 ]

depths = [0, 5, 10, 20, 30, 40, 50, 100, 200] 

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
  if d >= date.year: #this gives us data from desired time before sampling date
    return True
  else:
    return False

def get_depth(fields, depth): # throws ValueError if it encounters a missing value in the line
  """
  Estimates temp at point between sensors using linear interpolation
  
  Parameters
  ----------
  fields : list
    List representing one line of SPRUCE WEW data filtered with 
    filter() fun.
  depth : int
    Depth at which you want to estimate temperature.

  Returns
  -------
  float
    Returns a float value of the temperature estimated at specified 
    point based on linear interpolation between adjacent temperature 
    sensors.
  """
  if depth == 0:
    return fields[2]  # if depth is zero, just return the temp from the upper-most sensor (surface)                                
  i = bisect.bisect_left(depths, depth)  # depth is the depth between interval, i is the sensor above depth                              
  if i >= len(depths):  # Removed depth < 0 condition, as this is not possible This could be the case if depth was shallower than min or deeper than max depth in depths list        
    raise ValueError                       

  lo = float(fields[2+(i-1)])  # finds index of temp at shallowest adjacent sensor 
  hi = float(fields[2+i])  # finds index of temp at deepest adjacent sensor
  m = (hi - lo) / (depths[i] - depths[i - 1])
  result = lo + ((depth - depths[i - 1]) * m)
  return result


def average(line, interval):
  """
  Calcs average temp interpolated across specified depth interval.

  Parameters
  ----------
  line : list
    List representing one line of SPRUCE WEW data filtered with 
    filter() fun.
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
  
  missing = []
  sum = 0 
  for i in range(interval[0], interval[1]+1):
    try:
      sum += get_depth(line, i) # if there is a missing value, throws ValueError, should proceed to except statement
    except: 
      #break  #this seems to be the issue; looks like it would break out of the for loop completely, leaving sum = 0
      # really need to filter out lines with missing vals earlier
      #print(line)
      return  # This returns None; I think we need to test for missing values earlier
  return sum / ((interval[1] - interval[0]) + 1)

# Import csv data into list of lists, filtering to match dates and plots
InFile = open(InFileName,'r')

data = []  # instantiate empty list to house the data lines (will be a list of strings)

with open(InFileName, 'r') as InFile:
  header = InFile.readline()  # Reads first line of input file and stores as header
  for line in InFile:  # Iterate line by line through file
    yr = int(line[0:4])  #  select the year from data line
    for date in sampling_dates:  # Iterate over all target dates to check match with data line
    #TO DO: change target date input to years instead of datetime, then we can
    # use if date in sampling_dates:, which would eliminate one level of nest
      if is_year(yr, date):  # checks to see if date is within range of specified dates
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
AvgCSV = ('C:/Users/Mark/Desktop/wew_files_temp/DPH_Averages.txt') # tab-separated b/c interval is tuple
with open(AvgCSV, 'w') as av:
  print('TimeStamp \tPlot \tupper depth \tlower depth \taverage temperature',  # Print header to ouput csv
        file = av)  
  for line in data:  # Iterate over lines in list containing data
    # Use each line of data to calculate average temp across each peat sampling interval
    # Remember, 'data' contains sensor temps, but output file will have peat sampling temps
    for i in intervals:  
      print(line[0], '\t', line[1], '\t', str(i[0]), '\t', str(i[1]), '\t', 
            average(line, i),  file = av)  # see average() documentation for more info
print(datetime.datetime.now())
## Return the average, standard deviation, maximum, and minimum temperature 
## for each DPH sampling depth increment over the calendar year of sampling

# Average the interpolated sampling depth temps over all sampling dates over the calendar year, save to output file
FinalCSV = 'C:/Users/Mark/Desktop/wew_files_temp/DPH_plot_depth_date.txt'  # tab-separated b/c interval is tuple
with open(FinalCSV, 'w') as fi:
  print('Date \tPlot \tDepth \tMin \tMax \tAverage \tStDev \n', file = fi)
  for plot in plots:
    for date in sampling_dates:
      for interval in intervals:
        temps = [ average(sample, interval) for sample in data  # recalc the sampling interval avg temp for each date and append to list for easy averaging
                 if in_range(sample, date) and int(sample[1]) == plot ]  # If statements ensure that if you have multiple target dates, they stay separate in output
        # The line above repeats code for the average, but no good workaround without major overhaul
        temps = numpy.array(temps, dtype = numpy.float64)  # Converting to float64 array changes None to NaN, necessary for numpy functions that ignore missing values
        if len(temps) != 0:  # Ensure that all data is not missing
          print(None in temps)  # None is included in temps
          print(0 in temps)
          avg = numpy.nanmean(temps)  # nanmean() ignores NaN, formerly None
          stdev = numpy.nanstd(temps)  # nanstd() ignores NaN, formerly None
          print(date, "\t", plot, "\t", interval, "\t",numpy.nanmin(temps), 
                "\t", numpy.nanmax(temps),"\t", avg, "\t", stdev, file = fi)  
        else:
          print("no data for" , interval, plot, date)  # If there was no data for a given plot/depth/date, this will ID
          # Print statement above will only let you know the target date for which there was no data at plot/depth. This does not warn that there were missing values within the average calc
          # TO DO: Identify individual records with missing data
print(datetime.datetime.now())  # Would probably be most helpful to have the measurement number. Then you could easily find the entry in question