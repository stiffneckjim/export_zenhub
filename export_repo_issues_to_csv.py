"""
Exports Issues from a specified repository to a CSV file

Uses basic authentication (Github username + password) to retrieve Issues
from a repository that username has access to. Supports Github API v3.

Derived from https://gist.github.com/unbracketed/3380407
"""
import csv
import requests
import json

GITHUB_USER = ''
GITHUB_PASSWORD = ''
REPO = ''  # format is username/repo
ISSUES_FOR_REPO_URL = 'https://api.github.com/repos/%s/issues' % REPO
AUTH = (GITHUB_USER, GITHUB_PASSWORD)

txtout = open('data.json', 'w')

def write_issues(response):
    "output a list of issues to csv"
    if not r.status_code == 200:
        raise Exception(r.status_code)
    
    json.dump(r.json(), txtout, indent=4)
    
    for issue in r.json():
        print issue['number']
        if 'pull_request' not in issue:
            global issues
            issues += 1
            csvout.writerow([issue['number'], issue['title'].encode('utf-8'), issue['body'].encode('utf-8'), issue['created_at'], issue['updated_at']])
        else:
            print '%s is PR' % issue['number']


issues = 0
r = requests.get(ISSUES_FOR_REPO_URL, auth=AUTH)
csvfilename = '%s-issues.csv' % (REPO.replace('/', '-'))
csvfile = open(csvfilename, 'wb')
csvout = csv.writer(csvfile)
csvout.writerow(('id', 'Title', 'Body', 'Created At', 'Updated At'))
write_issues(r)

#more pages? examine the 'link' header returned
if 'link' in r.headers:
    pages = dict(
        [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
            [link.split(';') for link in
                r.headers['link'].split(',')]])
    while 'last' in pages and 'next' in pages:
        print pages['next']
        r = requests.get(pages['next'], auth=AUTH)
        write_issues(r)
        if pages['next'] == pages['last']:
            break

csvout.writerow(['Total', issues])
csvfile.close()
txtout.close()
