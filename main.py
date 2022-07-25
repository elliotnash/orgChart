import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import csv

with open('behaviours', 'r') as file:
    inp = file.read().split('\n\n')
    behaviours = []
    for dem_str in inp:
        cat = []
        for line in dem_str.split('\n'):
            if line.strip() != "" and not line.strip().startswith('#'):
                cat.append(line)
        if len(cat) == 2:
            dev = []
            for raw_dev in cat[1].split(","):
                dev.append(list(map(lambda n: float(n), raw_dev.strip().split('-'))))
            behaviours.append({
                "name": cat[0],
                "values": {
                    "standard": dev[0],
                    "ethnicity": dev[1],
                    "gender": dev[2]
                }
            })

with open('demographics', 'r') as file:
    inp = file.read().split('\n\n')
    demographics = {}
    for dem_str in inp:
        dem = []
        for line in dem_str.split('\n'):
            if line.strip() != "" and not line.strip().startswith('#'):
                dem.append(line)
        if len(dem) == 2:
            dev = []
            for raw_dev in dem[1].split(","):
                dev.append(raw_dev.strip())
            demographics[dem[0].lower()] = {"ethnicity": float(dev[0]), "gender": float(dev[1])}


def generate_demographics(row):
    dep = demographics[row[4].lower().strip()]
    if np.random.random() < dep['gender']:
        row.append('Male')
    else:
        row.append('Female')
    if np.random.random() < dep['ethnicity']:
        row.append("White")
    else:
        row.append("Ethnic Minority")


def generate_score(median, std):
    while True:
        rand = np.random.normal(loc=median, scale=std)
        if 1 <= rand <= 7:
            return int(np.round(rand))


def generate_behaviours(row):
    for behaviour in behaviours:
        val = behaviour['values']
        median = val['standard'][0]
        med_dif = 0
        if row[11].strip().lower() != "male":
            med_dif += val['gender'][0]-median
        if row[12].strip().lower() != "white":
            med_dif += val['ethnicity'][0]-median
        median += med_dif
        spread = np.max([val['standard'][1], val['gender'][1], val['ethnicity'][1]])
        row.append(generate_score(median, spread))


with open('input.csv', 'r', encoding='utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file)
    with open('output.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        for i, row in enumerate(csv_reader):
            if row and i == 0:
                row.append("Gender")
                row.append("Ethnicity")
                for behaviour in behaviours:
                    row.append(behaviour['name'])
                csv_writer.writerow(row)
            elif row:
                generate_demographics(row)
                generate_behaviours(row)
                csv_writer.writerow(row)
