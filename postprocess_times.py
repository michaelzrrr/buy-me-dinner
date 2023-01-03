from tempfile import NamedTemporaryFile

import csv
import shutil

def post_process_csv(filename):
    tempfile = NamedTemporaryFile('w+t', delete=False)

    with open(filename, 'r') as csvFile, tempfile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='"')
        writer = csv.writer(tempfile, delimiter=',', quotechar='"')
        writer.writerow(["time","bid_price","ask_price","total_volume","open_price","quote_time"])

        for row in reader:
            if row[0].find('.') == -1:
                row[0] += '.000000'
            writer.writerow(row)

    shutil.move(tempfile.name, filename)
