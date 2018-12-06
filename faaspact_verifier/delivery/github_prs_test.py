import pytest

import responses

from faaspact_verifier.delivery.github_prs import GithubPrError, fetch_feature_pacts


class TestFetchFeaturePacts:

    @responses.activate  # type: ignore
    def test_fetches_feature_pacts(self) -> None:
        responses.add(responses.GET, 'https://api.github.com/repos/zhammer/morning-cd/pulls/1337',
                      json={'body': 'new pacts\r\nfeature-pacts: zh-feature-a eh-feature-b'})

        feature_pacts = fetch_feature_pacts('https://github.com/zhammer/morning-cd/pull/1337')

        expected_feature_pacts = frozenset({'zh-feature-a', 'eh-feature-b'})
        assert feature_pacts == expected_feature_pacts

    @responses.activate  # type: ignore
    def raises_exception_on_github_failure(self) -> None:
        responses.add(responses.GET, 'https://api.github.com/repos/zhammer/morning-cd/pulls/1337',
                      status_code=500)

        with pytest.raises(GithubPrError):
            fetch_feature_pacts('https://github.com/zhammer/morning-cd/pull/1337')
