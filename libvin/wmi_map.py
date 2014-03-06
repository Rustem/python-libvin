import csv
import os

def load_make_sheet(pfile):
    rv = {}
    with open(pfile, 'rb') as f:
        reader = csv.reader(f)
        _ = reader.next()

        for row in reader:
            vin_code, vin_model = row
            rv[vin_code] = vin_model

    return rv

WMI_MAP = load_make_sheet(os.path.join(os.path.abspath(
    os.path.dirname(__file__)), 'make.csv'))

