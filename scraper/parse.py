import re
import csv
import time
import requests
import requests_cache
from bs4 import BeautifulSoup

requests_cache.install_cache('course_cache')

def getCourseDataFlow(course_code):
    """Get UWFlow ratings"""
    url = 'https://uwflow.com/api/v1/courses/{}'.format(course_code.lower().replace(' ', ''))

    r = requests.get(url)
    print('Got result from cache: {}'.format(r.from_cache))

    if 'Offered' in r.json()['description']:
        m = re.search('Offered:?(.*)', r.json()['description'])
        offered = m.group(1).strip().split(',')
    else:
        offered = ''

    data = {
        'name': r.json()['name'],
        'description': r.json()['description'],
        'offered_w': 'W' in offered,
        'offered_s': 'S' in offered,
        'offered_f': 'F' in offered
    }

    for rating in r.json()['ratings']:
        data['{}_count'.format(rating['name'])] = rating['count']
        data['{}_rating'.format(rating['name'])] = rating['rating']
    return r.from_cache, data

output = []
with open('ece_courses.csv', 'r') as f:
    reader = csv.reader(f)
    for [course_list, course] in reader:
        print('Processing {}'.format(course))
        data = {}
        data['list'] = course_list
        data['course'] = course
        cached, flow_course_data = getCourseDataFlow(course)
        data.update(flow_course_data)
        print(data)
        output.append(data)

        # Only sleep between network requests
        if not cached: time.sleep(5)

# Cleanup formattting
for row in output:
    row['description'] = row['description'].encode('utf-8')

# Dump csv
# TODO: use https://docs.python.org/3/library/csv.html#csv.DictWriter to preserve ordering
with open('output.csv', 'w') as f:
    fieldnames = [
        'course',
        'list',
        'name',
        'offered_w',
        'offered_s',
        'offered_f',
        'easiness_rating',
        'easiness_count',
        'usefulness_rating',
        'usefulness_count',
        'interest_rating',
        'interest_count',
        'description'
    ]
    w = csv.DictWriter(f, fieldnames)
    w.writeheader()
    w.writerows(output)
