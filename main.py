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

rowMap = {}
outRows = []


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
    if np.random.random() > 0.1:
        row.append(np.random.random()*0.5)
    else:
        row.append(np.random.random()-1.5)


def generate_score(median, std):
    while True:
        rand = np.random.normal(loc=np.clip(median, 1, 7), scale=std)
        if 1 <= rand <= 7:
            return int(np.round(rand))


def get_modifier(email):
    if email in rowMap:
        row = rowMap[email]
        if email != row[9]:
            return row[13] + 0.5*get_modifier(row[9])
    return 0


def generate_behaviours(row):
    modifier = get_modifier(row[9])
    row.append(modifier)
    for behaviour in behaviours:
        val = behaviour['values']
        median = val['standard'][0]
        med_dif = 0
        if row[11].strip().lower() != "male":
            med_dif += val['gender'][0]-median
        if row[12].strip().lower() != "white":
            med_dif += val['ethnicity'][0]-median
        median += med_dif + modifier
        spread = np.max([val['standard'][1], val['gender'][1], val['ethnicity'][1]])
        row.append(generate_score(median, spread))


with open('input.csv', 'r', encoding='utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file)
    for i, row in enumerate(csv_reader):
        if row and i == 0:
            row.append("Gender")
            row.append("Ethnicity")
            row.append("Leadership Skills")
            row.append("Leadership Modifier")
            for behaviour in behaviours:
                row.append(behaviour['name'])
            outRows.append(row)
        elif row:
            generate_demographics(row)
            rowMap[row[0]] = row

for row in rowMap.values():
    generate_behaviours(row)
    outRows.append(row)

with open('output.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(outRows)
