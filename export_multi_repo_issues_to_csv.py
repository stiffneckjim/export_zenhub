#!/usr/bin/python
import csv
import json
import requests

"""
Usage:

Add the following to config.ini with appropriate values:
[DEFAULT]
AUTH_TOKEN =
ZEN_ACCESS =
QUERY = # See https://developer.github.com/v3/issues/#list-repository-issues
FILENAME = 


Exports Issues from a list of repositories to individual CSV files
Uses basic authentication (Github API Token and Zenhub API Token)
to retrieve Issues from a repository that token has access to.
Supports Github API v3 and ZenHubs current working API.
Derived from https://gist.github.com/Kebiled/7b035d7518fdfd50d07e2a285aff3977
@PinnaclePSM Author Jamie Belcher
"""


def write_issues(r, csvout, gh_repo, zen_board, zen_access):
    if not r.status_code == 200:
        raise Exception("Request returned status of:" + str(r.status_code))

    r_json = r.json()
    print(str(len(r_json)) + " issues loaded. Loading ZenHub data...")
    for issue in r_json:
        print(gh_repo + " issue: " + str(issue["number"]))

        zenhub_issue_url = (
            "https://api.zenhub.io/p1/repositories/"
            + zen_board
            + "/issues/"
            + str(issue["number"])
            + "?access_token="
            + zen_access
        )
        zen_r = requests.get(zenhub_issue_url).json()
        DateCreated = issue["created_at"][:-10]
        DateUpdated = issue["updated_at"][:-10]
        if "pull_request" not in issue:
            global ISSUES
            ISSUES += 1
            assignees, tag, category, priority, labels = "", "", "", "", ""
            for i in issue["assignees"] if issue["assignees"] else []:
                assignees += i["login"] + ","

            for x in issue["labels"] if issue["labels"] else []:
                if "Category" in x["name"]:
                    category = x["name"][11 : 11 + len(x["name"])]
                elif "Tag" in x["name"]:
                    tag = x["name"][6 : 6 + len(x["name"])]
                elif "Priority" in x["name"]:
                    priority = x["name"][11 : 11 + len(x["name"])]
                else:
                    labels += x["name"] + ","

            estimate = zen_r.get("estimate", dict()).get("value", "")

            if issue["state"] == "closed":
                Pipeline = "Closed"
            else:
                Pipeline = zen_r.get("pipeline", dict()).get("name", "")

            if not issue.get("body"):
                issue["body"] = ""

            csvout.writerow(
                [
                    gh_repo,
                    issue["number"],
                    issue["title"].encode("utf-8"),
                    issue["body"].encode("utf-8"),
                    assignees[:-1],
                    issue["state"],
                    Pipeline,
                    DateCreated,
                    DateUpdated,
                    labels[:-1],
                    category,
                    tag,
                    priority,
                    estimate,
                ]
            )


def get_issues(gh_repo, query, gh_access, zen_board, fileoutput, zen_access):
    issues_for_repo_url = "https://api.github.com/repos/%s/issues?%s" % (
        gh_repo,
        query,
    )
    print("Retrieving issues... " + issues_for_repo_url)
    r = requests.get(issues_for_repo_url, auth=("token", gh_access))
    write_issues(
        r=r,
        csvout=fileoutput,
        gh_repo=gh_repo,
        zen_board=zen_board,
        zen_access=zen_access,
    )
    # more pages? examine the 'link' header returned
    if "link" in r.headers:
        pages = dict(
            [
                (rel[6:-1], url[url.index("<") + 1 : -1])
                for url, rel in [
                    link.split(";") for link in r.headers["link"].split(",")
                ]
            ]
        )
        while "last" in pages and "next" in pages:
            pages = dict(
                [
                    (rel[6:-1], url[url.index("<") + 1 : -1])
                    for url, rel in [
                        link.split(";") for link in r.headers["link"].split(",")
                    ]
                ]
            )
            r = requests.get(pages["next"], auth=gh_access)
            write_issues(r, FILEOUTPUT, gh_repo, zen_board)
            if pages["next"] == pages["last"]:
                break


with open("config.json", "r") as config_file:
    CONFIG = json.load(config_file)
    print("Read config file successfully")
    print(CONFIG)


# See https://developer.github.com/v3/issues/#list-repository-issues


ISSUES = 0
OPENFILE = open(CONFIG["FILENAME"], "w")
FILEOUTPUT = csv.writer(OPENFILE)

FILEOUTPUT.writerow(
    (
        "Repository",
        "Issue Number",
        "Issue Title",
        "Description",
        "Category",
        "Tag",
        "Assigned To",
        "Priority",
        "State",
        "Pipeline",
        "Issue Author",
        "Created At",
        "Updated At",
        "Labels",
        "Estimate",
    )
)

get_issues(
    gh_access=CONFIG["GH_ACCESS"],
    gh_repo=CONFIG["GH_REPO"],
    zen_board=CONFIG["ZEN_BOARD"],
    query=CONFIG["QUERY"],
    zen_access=CONFIG["ZEN_ACCESS"],
    fileoutput=FILEOUTPUT,
)

OPENFILE.close()
