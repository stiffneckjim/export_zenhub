# export_zenhub

Exports Issues from a list of repositories to individual CSV files
Uses basic authentication (Github API Token and Zenhub API Token)
to retrieve Issues from a repository that token has access to.

Supports Github API v3 and ZenHub's current working API.

Forked from [ceresfairfood/export_zenhub](https://github.com/ceresfairfood/export_zenhub) which was forked from [a gist by Jammizzle](https://gist.github.com/Jammizzle/ad2a94008b56a6f9d17cfdddf5a6dd4d)

## Config

Add the following to config.json with appropriate values:

```json
{
    "GH_ACCESS": "your personal GitHub API token",
    "ZEN_ACCESS": "the personal token provided by Zenhub",
    "QUERY": "See https://developer.github.com/v3/issues/#list-repository-issues"
    "FILENAME": "/Users/$USER/Downloads/export_zenhub.csv"
    "GH_REPO": "your GitHub repo",
    "ZEN_BOARD": "the corresponding ZenHub board"
}
```

To build the query, you can use the web interface, but you need to translate some of the options). For example:

`https://github.com/my/repo/issues?q=is%3Aissue+updated%3A%3E%3D2021-01-01+sort%3Aupdated-asc+`

Is equivalent to

`QUERY = since=2021-01-01&state=all&sort=updated&direction=asc`

## Usage

Just execute the Python script:

```Shell
python export_multi_repo_issues_to_csv.py
```

## TODO

- [ ] Add back handling multiple GitHub repos and ZenHub boards
- [ ] Add command-line parameters, including for filtering by date
- [ ] Add a help message for those parameters
- [ ] Flag to output to STDOUT
- [x] Move repo list to config (REPO_LIST)
- [ ] Optional config to whitelist included fields (eg: "FIELDS": "number,title,assignees,description")
