import argparse
from os import listdir
from os.path import isfile,join
from datetime import *
from collections import deque,defaultdict

# 40245 = 8 march 2010

class Rules:
  shortest_time = timedelta(hours=3)
  artifact_time = timedelta(seconds=3)
  longest_time = timedelta(hours=24)
  start_time = datetime(1899,12,30)

class TimeHelper:
  @staticmethod
  def sec_time_of_day(time):
    return time.second + time.minute * 60 + time.hour * 3600

  @staticmethod
  def weekday_sleep(time):
    return (time + timedelta(hours = 12)).weekday()
    
  @staticmethod
  def remove_days(t):
    if(type(t) == datetime):
      return time(t)
    elif(type(t) == timedelta):
      return timedelta(seconds=t.seconds)
  
  @staticmethod
  def hours_toff(t):
    seconds = t.total_seconds()
    hours = seconds // 3600
    seconds -= hours * 3600
    minutes = seconds // 60
    seconds -= minutes * 60
    return "{:0>2}:{:0>2}:{:0>2}".format(str(int(hours)), str(int(minutes)), str(int(seconds)))
      
    
  
class DataPoint:
  def __init__(self, line=["1","2","3","4","5","6","7"]):
    try:
      splitline = line
      time = splitline[0].split(".")
      self.activity = int(splitline[3])
      if(len(time) == 1):
        time.append("0")
      self.time = Rules.start_time + timedelta(days=int(time[0]), milliseconds=(24.0*3600.0*1000.0) * float("0." + time[1]))
      self.interval = timedelta(seconds=float(splitline[2]))
      self.time_stop = self.time + self.interval
    except Exception as E:
      print E
      print "Line error: " + line
  
  def mid_time(self):
    return self.time + (self.interval // 2)

  def __str__(self):
    return "Time: " + self.time.strftime("%H:%M") + " to " + self.time_stop.strftime("%H:%M") + " Duration: " + str(TimeHelper.hours_toff(self.interval)) + " Activity: " + str(self.activity)
      
class Patient:
  def __init__(self, id):
    self.id = id
    self.weeks = dict()
	
class Week:
  def __init__(self, num):
    self.num = num
    self.datapoints = list()
    self.sleep = list()
    
  def find_sleep(self):
    if not self.datapoints:
      return self.sleep
    while(self.remove_artifacts() > 0):
      print "Removal not done.."
    current_window = deque()
    current_day = None
    current_start = self.datapoints[0].time
    current_end = self.datapoints[0].time_stop
    longest_sleep_for_day = 0
    return_days = list()
    for ele in self.datapoints:
      if ele.activity == 0:
        if Rules.longest_time > ele.interval > Rules.shortest_time:
          return_days.append(ele)
    if len(return_days) < 1:
      return []
    return_days.sort(key=lambda k: k.time)
    return_real = [return_days[0]]
    for ele in return_days:
      if (ele.time - timedelta(hours=12)).day == (return_real[-1].time - timedelta(hours=12)).day:
        print "Comparing: " + str(return_real[-1].time) + " to " + str(ele.time)
        return_real[-1] = max(return_real[-1], ele, key=lambda k: k.interval)
      elif(ele.time + timedelta(hours=12)).weekday() == (return_real[0].time + timedelta(hours=12)).weekday():
        print "Removing item: " + str(ele)
        print "Keeping item: " + str(return_real[0])
        continue
      else:
        return_real.append(ele)
    #while(len(return_real) > 7):
    #  return_real.pop()
    self.sleep = return_real
    self.datapoints = []
    return return_real
   

  def remove_artifacts(self):
    removals = list()
    additions = list()
    for i in range(len(self.datapoints)):
      dp = self.datapoints[i]
      if dp.activity != 0:
        continue
      start_time = dp.time_stop
      elapsed_time = timedelta(seconds=0)
      a = 1
      while a + i < len(self.datapoints):
        next = self.datapoints[i+a]
        elapsed_time = next.time - start_time
        if elapsed_time > Rules.artifact_time:
          break
        if next.activity == 2:
          break
        if(next.activity == dp.activity):
          additions.append(self.combine_datapoints(dp, next))
          removals.extend(self.datapoints[d] for d in range(i,i+a))
          break
        a += 1
    for elem in removals:
      if elem in self.datapoints:
        self.datapoints.remove(elem)
    for elem in additions:
      self.datapoints.append(elem)
    self.datapoints.sort(key=lambda k: k.time)
    return len(removals)
          
  def combine_datapoints(self, dp1, dp2):
    ret_dp = DataPoint()
    ret_dp.time = min(dp1.time, dp2.time)
    ret_dp.stop_time = min(dp1.time_stop, dp2.time_stop)
    ret_dp.interval = ret_dp.stop_time - ret_dp.time
    ret_dp.activity = dp1.activity
    return ret_dp
    
  def get_total_means(self, wd=0):
    bedtimes = list()
    waketimes = list()
    midtimes = list()
    sleeptimes = list()
    if len(self.sleep) < 1:
      return ("","","","")
    
    for d in self.sleep:
      time_set = range(7)
      if(wd == 1): #Weekdays
        time_set = [0,1,2,3,6,7]
      elif(wd == 2): #Weekend
        time_set = [4,5]
      if((d.time - timedelta(hours=12)).weekday() not in time_set):
        continue
      start_day = d.time - timedelta(hours=12)
      start_day = start_day.replace(microsecond=0,second=0,minute=0,hour=0)
      time_since_start = (d.time - start_day).total_seconds()
      time = time_since_start
      waketime = time + d.interval.total_seconds()
      sleeptimes.append(d.interval.total_seconds())
      waketimes.append(waketime)
      bedtimes.append(time)
      midtimes.append(time + (d.interval.total_seconds() / 2))
    if(len(waketimes) < 1 or len(sleeptimes) < 1 or len(midtimes) < 1 or len(bedtimes) < 1):
      return ("","","","")
    mean_bed = TimeHelper.hours_toff(timedelta(seconds=(sum(bedtimes) / len(bedtimes))))
    mean_wake = TimeHelper.hours_toff(timedelta(seconds=(sum(waketimes) / len(waketimes))))
    mean_mid = TimeHelper.hours_toff(timedelta(seconds=(sum(midtimes) / len(midtimes))))
    mean_sleep = TimeHelper.hours_toff(timedelta(seconds=(sum(sleeptimes) / len(sleeptimes))))
    
    return (mean_bed, mean_wake, mean_mid, mean_sleep)
    
class Study:
  def __init__(self):
    self.patients = dict()
    
  def add_file(self, filename, path):
    last_part = filename.split("/")[-1]
    print last_part
    middle = last_part.split(".")[2]
    trimmed = middle.split("_")[0]
    id = trimmed[:4]
    uke = "1"
    if(not id in self.patients):
      self.patients[id] = Patient(id)
    if(not uke in self.patients[id].weeks):
      self.patients[id].weeks[uke] = Week(uke)
    for l in open(join(path,filename)):
      if l.strip() == "":
        continue
      if not l.startswith("\""):
        line = l.split(",")
        if(line[3] != "1"):
          dp = DataPoint(line)
          self.patients[id].weeks[uke].datapoints.append(dp)
    self.patients[id].weeks[uke].find_sleep()
        
  def print_summary(self):
    for patient in self.patients.values():
      print "Patient: " + patient.id
      for week in patient.weeks.values():
        print "Week: " + week.num
        print "Datapoints: " + str(len(week.datapoints))
        for e in week.find_sleep():
#          print e
          pass
          
  def print_time(self, file, pretty_print=False):
    f = open(file, 'w')
    fl = "Pasient id,Uke,"
    weekdays = ["Man", "Tir", "Ons", "Tors", "Fre", "Lor", "Son"]
    for d in range(7):
      fl += weekdays[d] + " lights off, " + weekdays[(d+1) % 7] + " lights on, Time in bed, Mid sleep,"
    
    totals = ["Total", "Weekday", "Weekend"]
    for d in range(3):    
      fl += totals[d] + " mean lights off, " + totals[d] + " mean mid-sleep, " + totals[d] +" mean lights on, "+ totals[d] +" mean time in bed,"
    #f.write("Pasient-ID,Uke,Man lights off, Tir light on,Time in bed,Mid sleep,Tir lights off,onon,tib,onoff,toon,tib,tooff,fron,tib,froff,loon,tib,looff,soon,tib,sooff,maon,tib,mean_loff,mean_mid,mean_lon,mean_sleep\n")
    f.write(fl[0:-1] + "\n")
    for patient in sorted(self.patients.values(),key=lambda k: int(k.id)):
      output = patient.id + ","
      for week in patient.weeks.values():
        output += week.num + ","
        dp = defaultdict(lambda: ",,,,")
        for datapoint in week.sleep:
          real_weekday = (datapoint.time-timedelta(hours=12)).weekday()
          start_day = datapoint.time-timedelta(hours=12)
          start_day = start_day.replace(microsecond=0, second=0, minute=0, hour=0)
          lights_off = TimeHelper.hours_toff(datapoint.time - start_day)
          lights_on = TimeHelper.hours_toff(datapoint.time_stop - start_day)
          time_in_bed = TimeHelper.hours_toff(datapoint.interval)
          mid_sleep = TimeHelper.hours_toff((datapoint.time - start_day) + (datapoint.interval // 2))
          dp[real_weekday] = ""
          dp[real_weekday] += str(lights_off) + ","
          dp[real_weekday] += str(lights_on) + ","
          dp[real_weekday] += str(time_in_bed) + ","
          dp[real_weekday] += str(mid_sleep)+ ","
        for i in range(7):
          output += dp[i]
        for i in range(3):
          (mean_bed, mean_wake, mean_mid, mean_sleep) = week.get_total_means(i)
          output += str(mean_bed) + "," + str(mean_mid) + "," + str(mean_wake) + "," + str(mean_sleep) + ","
      f.write(output[0:-1] + "\n")
      if(pretty_print):
        self.pretty_print(fl[:-1],output[:-1])
    
  def pretty_print(self, header, string):
    data = string.split(",")
    head = header.split(",")
    
    for i in range(len(head)):
      print "{:<30}".format(head[i]) + ": " + data[i]
  
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-f", "--files", dest="files", help="Data files to parse")
  parser.add_argument("-p", action="store_const", const=True, dest="pretty", default=False)
  
  args = parser.parse_args()
  
  study = Study()
  
  files = [f for f in listdir(args.files) if isfile(join(args.files,f))]
  
  for f in files:
    if(f.endswith(".csv") or f.endswith(".xls")):
      study.add_file(f,args.files)
  
  study.print_summary()
  study.print_time("output.csv", args.pretty)