#!/usr/bin/python
import csv
import json
import requests
import configparser

"""
Usage:
`touch config.ini`

Add the following to newly created config.ini with appropriate values:
[DEFAULT]
AUTH_TOKEN =
ZEN_ACCESS =


Exports Issues from a list of repositories to individual CSV files
Uses basic authentication (Github API Token and Zenhub API Token)
to retrieve Issues from a repository that token has access to.
Supports Github API v3 and ZenHubs current working API.
Derived from https://gist.github.com/Kebiled/7b035d7518fdfd50d07e2a285aff3977
@PinnaclePSM Author Jamie Belcher
"""

def write_issues(r, csvout, repo_name, repo_ID):
    if not r.status_code == 200:
        raise Exception("Request returned status of:"+str(r.status_code))

    r_json = r.json()
    for issue in r_json:
        print(repo_name + ' issue Number: ' + str(issue['number']))
        zenhub_issue_url = 'https://api.zenhub.io/p1/repositories/' + str(repo_ID) + '/issues/' + str(issue['number']) + '?access_token=' + ACCESS_TOKEN
        zen_r = requests.get(zenhub_issue_url).json()
        DateCreated = issue['created_at'][:-10]
        if 'pull_request' not in issue:
            global ISSUES
            ISSUES += 1
            assignees, tag, category, priority = '', '', '', ''
            for i in issue['assignees'] if issue['assignees'] else []:
                assignees += i['login'] + ','
            for x in issue['labels'] if issue['labels'] else []:
                if "Category" in x['name']:
                    category = x['name'][11:11 + len(x['name'])]
                if "Tag" in x['name']:
                    tag = x['name'][6:6 + len(x['name'])]
                if "Priority" in x['name']:
                    priority = x['name'][11:11 + len(x['name'])]
            estimate = zen_r.get('estimate', dict()).get('value', "")
            if category != 'BUG':
                Pipeline = zen_r.get('pipeline', dict()).get('name', "")

                csvout.writerow([repo_name, issue['number'], issue['title'].encode('utf-8'), category,
                                tag, assignees[:-1],
                                priority, Pipeline, DateCreated,
                                estimate])

def get_issues(repo_data):
    repo_name = repo_data[0]
    repo_ID = repo_data[1]
    issues_for_repo_url = 'https://api.github.com/repos/%s/issues?since=2017-05-01&state=closed' % repo_name
    r = requests.get(issues_for_repo_url, auth=AUTH)
    write_issues(r, FILEOUTPUT, repo_name, repo_ID)
    # more pages? examine the 'link' header returned
    if 'link' in r.headers:
        pages = dict(
            [(rel[6:-1], url[url.index('<') + 1:-1]) for url, rel in
             [link.split(';') for link in
              r.headers['link'].split(',')]])
        while 'last' in pages and 'next' in pages:
            pages = dict(
                [(rel[6:-1], url[url.index('<') + 1:-1]) for url, rel in
                 [link.split(';') for link in
                  r.headers['link'].split(',')]])
            r = requests.get(pages['next'], auth=AUTH)
            write_issues(r, FILEOUTPUT, repo_name, repo_ID)
            if pages['next'] == pages['last']:
                break


REPO_LIST = [("*GITHUB REPO*", "*ZENHUB REPOID*")]

config = configparser.ConfigParser()
config.read('config.ini')

AUTH = ('token', config['DEFAULT']['AUTH_TOKEN'])
ACCESS_TOKEN = config['DEFAULT']['ZEN_ACCESS']

ISSUES = 0
FILENAME = 'output.csv'
OPENFILE = open(FILENAME, 'wb')
FILEOUTPUT = csv.writer(OPENFILE)

FILEOUTPUT.writerow(('Repository', 'Issue Number', 'Issue Title', 'Category',
                     'Tag', 'Assigned To',
                     'Priority', 'Pipeline',
                     'Issue Author',
                     'Created At', 'Estimate Value'
                     ))

for repo_data in REPO_LIST:
    get_issues(repo_data)

OPENFILE.close()
