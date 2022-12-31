import csv

f = "StrategyReports_AAPL_122222.csv"

data = []
with open(f, mode='r') as fd:
    csvFile = csv.reader(fd)

    i = 0
    for lines in csvFile:
        if i >= 6 and i <= 228:
            data.append(lines[0].split(';') + lines[1].split(';'))
        i += 1

profit = 0
for line in data:
    profit += float(line[3]) * float(line[4][1:]) * -1

print(profit)

