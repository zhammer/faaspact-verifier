import re
from typing import FrozenSet, NamedTuple, cast

import requests


class GithubPrError(Exception):
    """Exception raised upon encountering an issue fetching a github PR."""


class PullRequestInfo(NamedTuple):
    owner: str
    repo: str
    number: int


def fetch_feature_pacts(pull_request_url: str) -> FrozenSet[str]:
    """Fetch the feature-pacts for a given pull request on github. This is useful for CI builds
    that have access to their associated pull requests.
    Expects a pull_request_url like 'https://github.com/zhammer/morning-cd/pull/17' with a PR body
    that includes a line 'feature-pacts: zh-feature-a, eh-feature-b'. If there is no 'feature-pacts'
    line, this will return an empty set.
    """
    pr_info = _pluck_pull_request_info(pull_request_url)
    r = requests.get(
        f'https://api.github.com/repos/{pr_info.owner}/{pr_info.repo}/pulls/{pr_info.number}'
    )
    if not r.status_code == requests.codes.all_good:
        raise GithubPrError(f'Error fetching pr {pr_info} from github. Response: {r.text}.')

    body = cast(str, r.json()['body'])
    return _pluck_feature_pacts(body)


def _pluck_feature_pacts(pr_body: str) -> FrozenSet[str]:
    """
    # Returns set with one feature pact if specified
    >>> body = 'gitlab: mygitlaburl.com\\r\\nfeature-pacts: zh-feature-a'
    >>> _pluck_feature_pacts(body) == frozenset({'zh-feature-a'})
    True

    # Returns set with multiple feature pacts if specified
    >>> body = 'gitlab: mygitlaburl.com\\r\\nfeature-pacts: zh-feature-a eh-feature-b\\r\\nurgent!'
    >>> _pluck_feature_pacts(body) == frozenset({'zh-feature-a', 'eh-feature-b'})
    True

    # Returns empty set if no feature-pacts line
    >>> body = 'gitlab: mygitlaburl.com\\r\\n\\r\\nJust adding some documentation'
    >>> _pluck_feature_pacts(body)
    frozenset()

    # Returns empty set if feature-pacts line with no tags
    >>> body = 'gitlab: mygitlaburl.com\\r\\n\\r\\nfeature-pacts:\\r\\nJust adding some docs'
    >>> _pluck_feature_pacts(body)
    frozenset()

    # Raises a GithubPrError if multiple feature-pact lines found
    >>> body = 'feature-pacts: zh-feature-a\\r\\nfeature-pacts: eh-feature-b'
    >>> _pluck_feature_pacts(body)
    Traceback (most recent call last):
        ...
    faaspact_verifier.delivery.github_prs.GithubPrError: ...
    """
    feature_pact_lines = [line for line in pr_body.split('\r\n')
                          if line.startswith('feature-pacts:')]
    if not feature_pact_lines:
        return frozenset()
    if len(feature_pact_lines) > 1:
        raise GithubPrError(f'There should only be one feature-pacts line. "{feature_pact_lines}"')
    return frozenset(feature_pact_lines[0].split()[1:])


def _pluck_pull_request_info(pull_request_url: str) -> PullRequestInfo:
    """
    # Plucks a PullRequestInfo from  a valid
    >>> _pluck_pull_request_info('https://github.com/zhammer/morning-cd/pull/17')
    PullRequestInfo(owner='zhammer', repo='morning-cd', number=17)

    # Raises a GithubPrError on bad urls
    >>> _pluck_pull_request_info('bad url')
    Traceback (most recent call last):
        ...
    faaspact_verifier.delivery.github_prs.GithubPrError: ...
    """
    match = re.search(
        r'github\.com/(?P<owner>[\w-]+)/(?P<repo>[\w-]+)/pull/(?P<number>\d+)',
        pull_request_url
    )

    if not match:
        raise GithubPrError(f'Couldnt parse url: {pull_request_url}')

    return PullRequestInfo(
        owner=match.group('owner'),
        repo=match.group('repo'),
        number=int(match.group('number'))
    )
