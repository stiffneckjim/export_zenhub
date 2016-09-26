"""
Exports Issues from a list of repositories to individual CSV files
Uses basic authentication (Github username + password) to retrieve Issues
from a repository that username has access to. Supports Github API v3.
Derived from https://gist.github.com/Billy-/96b16b7682a19a562b277c1ab52547a5
"""
import csv
import requests
import json

GITHUB_USER = ''
GITHUB_PASSWORD = ''
REPO_LIST = [''] # format is 'username/repo'
AUTH = (GITHUB_USER, GITHUB_PASSWORD)

txtout = open('data.json', 'w')
issues = 0

def write_issues(r, csvout):
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

def get_issues(repo_name):
    issues = 0
    issues_for_repo_url = 'https://api.github.com/repos/%s/issues' % repo_name
    r = requests.get(issues_for_repo_url, auth=AUTH)
    csvfilename = '%s-issues.csv' % (repo_name.replace('/', '-'))
    csvfile = open(csvfilename, 'wb')
    csvout = csv.writer(csvfile)
    csvout.writerow(('id', 'Title', 'Body', 'Created At', 'Updated At'))
    print 'Now exporting issues from %s' % (repo_name.split('/')[1])
    write_issues(r, csvout)

    # more pages? examine the 'link' header returned
    if 'link' in r.headers:
        pages = dict(
            [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
                [link.split(';') for link in
                    r.headers['link'].split(',')]])
        while 'last' in pages and 'next' in pages:
            pages = dict(
                [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
                    [link.split(';') for link in
                        r.headers['link'].split(',')]])
            print pages['next']
            r = requests.get(pages['next'], auth=AUTH)
            write_issues(r, csvout)
            if pages['next'] == pages['last']:
                break

    csvout.writerow(['Total', issues])
    csvfile.close()

for repo in REPO_LIST:
    get_issues(repo)
txtout.close()
