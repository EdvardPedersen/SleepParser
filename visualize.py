from bokeh.charts import BoxPlot,output_file,Bar
from bokeh.plotting import show
import argparse
from datetime import datetime

class Plotter:
  def __init__(self,ifile, ofile, id):
    self.ofile = ofile
    f = open(ifile)
    self.headers = f.readline().split(",")
    self.data = list()
    for l in f:
      if(id == "all"):
        split = l.split(",")
        entry = dict()
        for i in range(len(self.headers)):
          if i < 2:
            entry[self.headers[i]] = split[i]
          else:
            if i >= len(split):
              print split
              continue
            if not split[i]:
              continue
            times = split[i].split(":")
            if len(times) < 3:
              continue
            try:
              entry[self.headers[i]] = float(int(times[0]) * 3600 + int(times[1]) * 60 + int(times[2]))
            except ValueError:
              print times
        self.data.append(entry)
      else:
        if l.startswith(id):
          split = l.split(",")
          entry = dict()
          for i in range(len(self.headers)):
            entry[self.headers[i]] = split[i]
          self.data.append(entry)
    f.close()
          
  def plot(self):
    for item in self.data:
      if(int(item[self.headers[0]]) < 2000):
        item[self.headers[0]] = "Sick"
      else:
        item[self.headers[0]] = "Healthy"
  
    output_file(self.ofile)
    pl = BoxPlot(self.data, values=self.headers[-11],label=self.headers[0])
    show(pl)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-f", "--file", dest="file", help="Data file to parse")
  parser.add_argument("-o", "--output", dest="output", help="Outut filename")
  parser.add_argument("-i", "--id", dest="id", help="ID for patient, \"all\" to get a summary", default="all")
  
  args = parser.parse_args()
  pl = Plotter(args.file, args.output, args.id)
  pl.plot()