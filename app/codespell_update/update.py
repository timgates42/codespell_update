"""
Scan closed PRs to work out common spelling errors
"""

import os
import pathlib
import re
import sys

import github


def get_basedir():
    """
    Locate the current directory of this file
    """
    return pathlib.Path(sys.modules[__name__].__file__).resolve().parent.parent


def get_api():
    """
    Open GitHub API
    """
    api_token = os.environ["GITHUB_ACCESS_TOKEN"]
    api = github.Github(api_token)
    return api


def get_pulls(api):
    """
    Quickly iter all open PRs by orguser scans
    """
    current_user = api.get_user().login
    orgusers = set()
    with open(get_basedir() / "orguser.txt") as fobj:
        orgusers.update(line.strip() for line in fobj)
    resp = api.search_issues(
        " ".join(
            [
                "is:pr",
                "is:merged",
                f"author:{current_user}",
            ]
            + [f"-user:{orguser}" for orguser in orgusers]
        ),
    )
    for issue in resp:
        yield issue.as_pull_request()


def run_update():
    """
    Scan closed PRs to work out common spelling errors
    """
    regex = re.compile("Should read `[^`]+` rather than `([^`]+)`")
    title_re = re.compile("fix simple typo, [^-]+ -> (.*)$")
    for pull in get_pulls(get_api()):
        matches = regex.findall(pull.body, re.M)
        if not matches:
            matches = title_re.findall(pull.title)
        print(repr(matches))
        if not matches:
            print(f"Failed {pull!r} {pull.base.repo.full_name} {pull.body}")
            break
