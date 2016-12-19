import re
import csv
import time
import requests
import requests_cache
from bs4 import BeautifulSoup

requests_cache.install_cache('course_cache')

def make_throttle_hook(timeout=5.0):
    """
    Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached
    """
    def hook(response, *args, **kwargs):
        if not getattr(response, 'from_cache', False):
            print('sleeping')
            time.sleep(timeout)
        return response
    return hook

def getDepartment(course_code):
    """Isolates department from course code
    Returns None if a valid department is not found
    """
    # TODO: Validate the department
    return filter(lambda x: x.isalpha(), course_code)

def getCourseDataUW(course):
    url = 'http://www.ucalendar.uwaterloo.ca/{}/COURSE/course-{}.html'.format(1617, getDepartment(course))

    # s = requests_cache.CachedSession()
    # s.hooks = {'response': make_throttle_hook()}

    r = requests.get(url)
    print r.from_cache

    soup = BeautifulSoup(r.text, 'html.parser')
    for table in soup.find_all('table'):
        if table.tr is None: continue
        if table.tr.td.b.a is None: continue
        if table.tr.td.b.a['name'] == course.replace(' ', ''):
            # print table.prettify()
            data = {}
            td = table.find_all('td')
            data['name'] = td[2].text
            data['description'] = td[3].text
            # Add on data if it is in adjacent cell
            if 'Offered' in td[4].text: data['description'] += td[4].text

            if 'Offered' in data['description']:
                m = re.search('\Offered:(.*)]', data['description'])
                offered = m.group(1).strip().split(',')
            else:
                offered = ''

            data['offered_w'] = 'W' in offered
            data['offered_s'] = 'S' in offered
            data['offered_f'] = 'F' in offered
            return data

def getCourseDataFlow(course_code):
    """Get UWFlow ratings"""
    url = 'https://uwflow.com/api/v1/courses/{}'.format(course_code.lower().replace(' ', ''))

    r = requests.get(url)
    print r.from_cache

    data = {}
    for rating in r.json()['ratings']:
        # data[rating['name']] = {
        #     'count': rating['count'],
        #     'rating': rating['rating']
        # }
        data['{}_count'.format(rating['name'])] = rating['count']
        data['{}_rating'.format(rating['name'])] = rating['rating']
    return data

# list1 = {}
# with open('nse_intensive.html', 'r') as f:
#     html_doc = f.read()
# # print html_doc
# soup = BeautifulSoup(html_doc, 'html.parser')
#
# for row in soup.find(id='list1').find_all('tr'):
#     if row.td == None: continue
#     list1[row.td.a.text] = {
#         'url': row.td.a['href']
#     }
#     print('{}\t{}'.format(row.td.a.text, row.td.a['href']))


# getCourseDataFlow('ECE404')
# getCourseDataFlow('ECE327')

with open('list_1.txt', 'r') as f:
    courses = f.read().splitlines()

output = []
for course in courses:
    print 'Processing {}'.format(course)
    data = {}
    data['course'] = course
    data.update(getCourseDataUW(course))
    data.update(getCourseDataFlow(course))
    print data
    output.append(data)
    # import time; time.sleep(5)

# Dump csv
# TODO: use https://docs.python.org/3/library/csv.html#csv.DictWriter to preserve ordering
with open('output.csv', 'w') as f:
    fieldnames = [
        'course',
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
