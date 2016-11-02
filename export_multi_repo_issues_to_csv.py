import csv
import requests
import json


def write_issues(r, csvout, repo_name, repo_ID):
	if not r.status_code == 200:
		raise Exception(r.status_code)

	r_json = r.json()
	for issue in r_json:
		print repo_name+' issue Number: '+str(issue['number'])
		zenhub_issue_url = 'https://api.zenhub.io/p1/repositories/'+str(repo_ID)+'/issues/'+str(issue['number'])+ACCESS_TOKEN
		zen_r = requests.get(zenhub_issue_url).json()

		if 'pull_request' not in issue:
			sAssigneeList = ''
			sLabelList = ''
			sMilestoneList = ''
			for i in issue['assignees'] if issue['assignees'] else []:
				sAssigneeList += i['login']+'|'
			for x in issue['labels'] if issue['labels'] else []:
				sLabelList += x['name']+'|'

			EstimateValue = zen_r.get('estimate', dict()).get('value', "")
			Pipeline = zen_r.get('pipeline', dict()).get('name', "")
			csvout.writerow([repo_name, issue['number'], issue['title'].encode('utf-8'), sLabelList, issue['user']['login'], issue['created_at'],
			 issue['milestone']['title'] if issue['milestone'] else "", sAssigneeList, issue['body'].encode('utf-8'), EstimateValue, Pipeline])

def get_issues(repo_data):
	repo_name = repo_data[0]
	repo_ID = repo_data[1]
	issues_for_repo_url = 'https://api.github.com/repos/%s/issues' % repo_name
	r = requests.get(issues_for_repo_url, auth=AUTH)
	write_issues(r, csvout, repo_name, repo_ID)
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
			r = requests.get(pages['next'], auth=AUTH)
			write_issues(r, csvout, repo_name, repo_ID)
			if pages['next'] == pages['last']:
				break

REPO_LIST = [('***USER***/***REPO***', '***repoID***')]

AUTH = ('token', '*GithubAPIToken*')
ACCESS_TOKEN = '?access_token=***ZenHubAPIToken***'
csvfilename = 'PinnaclePSM-issues.csv'
csvfile = open(csvfilename, 'wb')
csvout = csv.writer(csvfile)
csvout.writerow(('Repository', 'Issue Number', 'Issue Title', 'Labels', 'Issue Author', 'Created At', 'Milestone', 'Assigned To', 'Issue Content', 'Estimate Value', 'Pipeline Name'))
for repo_data in REPO_LIST:
	get_issues(repo_data)
csvfile.close()
