#!/usr/env python

# To install dependencies, run `pip install -r requirements.txt`
# run with `python main.py`

import numpy as np
import csv

# Parses the behavior file into a dictionary
# To add more behaviours, just append them to the behaviour file, no modifying of code needed
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
                mod_list = list(map(lambda n: float(n), raw_dev.strip().split('-')))
                dev.append({
                    "median": mod_list[0],
                    "std": mod_list[1]
                })
            behaviours.append({
                "name": cat[0],
                "values": {
                    "standard": dev[0],
                    "ethnicity": dev[1],
                    "gender": dev[2]
                }
            })

# Parses the demographics file into a dictionary
# Every entry in input.csv must have an associated department,
# and every department must have an associated demographics entry
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

# a dictionary of every column name (taken from the header) to every index, allowing indexes to not be hard-coded
indexMap = {}
# a dictionary of all the input rows with demographic data generated and emails as the key, allowing
# a manager's entry to be looked up be email
rowMap = {}
# the rows to be written to the output csv file
outRows = []


# Randomly generates demographic data for an entry using the parameters from the demographics file
# To add more categories, the demographic parser, this function,
# and the generate_behaviours function will need to be modified
def generate_demographics(row):
    dep = demographics[row[indexMap['department_name']].lower().strip()]
    if np.random.random() < dep['gender']:
        row.append('Male')
    else:
        row.append('Female')
    if np.random.random() < dep['ethnicity']:
        row.append("White")
    else:
        row.append("Ethnic Minority")
    # generates leadership skills value which is added to the provided median value for a behaviour
    # (90% of the time a value between 0 and 0.5 is generated, 10% a value between -1.5 and -0.5 is generated)
    if np.random.random() > 0.1:
        row.append(np.random.random()*0.5)
    else:
        row.append(np.random.random()-1.5)


# generates a score for a behaviour on a 1-7 scale using a provided median and standard deviation
def generate_score(median, std):
    while True:
        rand = np.random.normal(loc=np.clip(median, 1, 7), scale=std)
        if 1 <= rand <= 7:
            return int(np.round(rand))


# find the leadership modifier that is added to the median of all scores generated
# this works by looking up a boss's leadership value by their email,
# then recursively finding their boss's leadership value
# every level up, the leadership value's effect is reduced by half, so an indirect boss's leadership value
# will propagate down the company, but at a reduced amount each level removed
# exit case when a boss either has no boss, or they are their own boss
def get_modifier(email):
    if email in rowMap:
        row = rowMap[email]
        if email != row[indexMap['manager_email']]:
            return row[indexMap['leadership_skills']] + 0.5*get_modifier(indexMap['manager_email'])
    return 0


# Generates behaviours for all behaviours in the behaviours file
def generate_behaviours(row):
    modifier = get_modifier(row[indexMap['manager_email']])
    # add the effective modifier that we calculate to the output
    row.append(modifier)
    for behaviour in behaviours:
        val = behaviour['values']
        median = val['standard']['median']
        # med_dif is the effective modifier to be applied to a behavior based off demographic modifiers
        # and leadership modifiers
        med_dif = 0
        if row[indexMap['gender']].strip().lower() != "male":
            med_dif += val['gender']['median']-median
        if row[indexMap['ethnicity']].strip().lower() != "white":
            med_dif += val['ethnicity']['median']-median
        median += med_dif + modifier
        # standard deviation is max of all modifiers, so not compounding
        spread = np.max([val['standard']['std'], val['gender']['std'], val['ethnicity']['std']])
        row.append(generate_score(median, spread))


# opens the input file, generates demographic data, and populates rowMap
with open('input.csv', 'r', encoding='utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file)
    for i, row in enumerate(csv_reader):
        if row and i == 0:
            # first row is header, generate modified header
            row.append("gender")
            row.append("ethnicity")
            row.append("leadership_skills")
            row.append("leadership_modifier")
            for behaviour in behaviours:
                row.append(behaviour['name'])
            # populate indexMap
            for j, name in enumerate(row):
                indexMap[name.lower()] = j
            outRows.append(row)
        elif row:
            generate_demographics(row)
            rowMap[row[indexMap['email']]] = row

# generates scores for each entry
for row in rowMap.values():
    generate_behaviours(row)
    outRows.append(row)

with open('output.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(outRows)
