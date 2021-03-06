# SleepParser
## A tool for creating sleep data from ActivePAL activity monitoring data

This tool takes as input a directory of ActivePAL CSV files of events, and outputs a CSV file with a single sleeping period per day, for each file.

### Requirements

- Python 2.7

### Input file format

The input files should be named in the following way:

`X.X.ID.csv`

Where X is anything, of any length, ID is the ID for the user in the file, consisting of 4 digits.

The input directory is specified with `-f DIR`, and the program will search the directory for csv files, and attempt to use all of them.

The file must contain data in the following form:
`TIME,X,INTERVAL,ACTIVITY,X`
- TIME is the time for the datapoint in the following format `DAYS.TIME_OF_DAY` where DAYS is the number of days since December 30th 1899, and TIME_OF_DAY is the percentage of the day (e.g. .25 is 06:00)
- INTERVAL is the duration of the activity
- ACTIVITY is the activity, where 0 = sedentary, 1 = standing, 2 = stepping
- X is ignored

### Output file format

The output (`output.csv`) file contains one row per file given to it, and is again a CSV file.
The fields here are composed like so:
`ID, WEEK, *DAY* LIGHTS OFF, *DAY* LIGHTS ON, *DAY* TIME IN BED, *DAY* MID-SLEEP, *DAY_TYPE* MEAN LIGHTS OFF, *DAY_TYPE* MEAN MID SLEEP, *DAY_TYPE* MEAN LIGHTS ON, *DAY_TYPE* MEAN SLEEP TIME`

## Processing done

- The first and last data point are removed (these are often artifacts).
- Sedentary periods above 24 hours, or below 3 hours, are removed.
- The day is determined by the date 12 hours before the start of the sleeping period.
- For each date, the longest sedentary period is chosen.
- Only sleeping periods with a midpoint before 7 days after the first data point are selected.
- If there are multiple sleeping periods for one day of the week (e.g. two sleeping periods on Monday, where one is a week later than the other), the latter is chosen.
