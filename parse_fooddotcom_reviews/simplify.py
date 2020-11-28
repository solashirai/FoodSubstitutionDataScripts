import json
import csv

data = []
with open('RAW_interactions.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    skipfirst = True
    for line in reader:
        if skipfirst:
            skipfirst = False
            continue
        data.append(line[4])

print('number of reviews: ', len(data))
with open('only_review_data.json', 'w') as f:
    json.dump(data, f)

