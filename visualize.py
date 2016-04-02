from bokeh.charts import BoxPlot,output_file,Bar
from bokeh.plotting import show
from bokeh.models.formatters import NumeralTickFormatter
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
              entry[self.headers[i]] = (int(times[0]) * 3600 + int(times[1]) * 60 + int(times[2])) - 24*3600
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
    num = -7
    num2 = -3
    app = list()
    for item in self.data:
      if(int(item[self.headers[0]]) < 2000):
        item[self.headers[0]] = "Sick - Weekday"
        if self.headers[num2] in item.keys():
          app.append(item.copy())
          app[-1][self.headers[num]] = app[-1][self.headers[num2]]
          app[-1][self.headers[0]] = "Sick - Weekend"
      else:
        item[self.headers[0]] = "Healthy"
        if self.headers[num2] in item.keys():
          app.append(item.copy())
          app[-1][self.headers[num]] = app[-1][self.headers[num2]]
          app[-1][self.headers[0]] = "Healthy - Weekend"
  
    self.data.extend(app)
    output_file(self.ofile)
    pl = BoxPlot(self.data, values=self.headers[num],label=self.headers[0])
    pl.left[0].formatter = NumeralTickFormatter(format="00:00:00")
    show(pl)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-f", "--file", dest="file", help="Data file to parse")
  parser.add_argument("-o", "--output", dest="output", help="Outut filename")
  parser.add_argument("-i", "--id", dest="id", help="ID for patient, \"all\" to get a summary", default="all")
  
  args = parser.parse_args()
  pl = Plotter(args.file, args.output, args.id)
  pl.plot()