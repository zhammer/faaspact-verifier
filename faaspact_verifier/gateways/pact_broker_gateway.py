import re
from typing import Dict, List, Optional, cast

import requests

from faaspact_verifier import abc
from faaspact_verifier.definitions import Pact, VerificationResult
from faaspact_verifier.exceptions import PactBrokerError


class PactBrokerGateway(abc.PactBrokerGateway):
    """Gateway to a pact broker."""

    def __init__(self, host: str, username: str, password: str) -> None:
        self.host = host
        self.username = username
        self.password = password

    def fetch_provider_pacts(self, provider: str) -> List[Pact]:
        all_pacts = self._fetch_latest_provider_pacts(provider)
        master_pacts = self._fetch_latest_provider_pacts(provider, tag='master')
        return all_pacts + master_pacts

    def provide_verification_results(self,
                                     provider_version: str,
                                     pact: Pact,
                                     verification_results: List[VerificationResult]) -> None:
        success = all(verification_result.verified for verification_result in verification_results)
        url = (f'{self.host}/pacts/provider/{pact.provider_name}/consumer/{pact.consumer_name}'
               f'/pact-version/{pact.pact_version}/verification-results')
        data = {
            'success': success,
            'providerApplicationVersion': provider_version
        }
        r = requests.post(url, json=data, auth=(self.username, self.password))

        if not r.status_code == requests.codes.created:
            raise PactBrokerError(f'{r.status_code}: {r.text}')

    def _fetch_latest_provider_pacts(self, provider: str, tag: Optional[str] = None) -> List[Pact]:
        url = f'{self.host}/pacts/provider/{provider}/latest' + (f'/{tag}' if tag else '')
        r = requests.get(url, auth=(self.username, self.password))
        pact_hrefs = [pact['href'] for pact in r.json()['_links']['pb:pacts']]
        return [self._fetch_pact_by_href(pact_href) for pact_href in pact_hrefs]

    def _fetch_pact_by_href(self, href: str) -> Pact:
        r = requests.get(href, auth=(self.username, self.password))
        raw_pact = r.json()

        consumer_version_href = raw_pact['_links']['pb:consumer-version']['href']
        r = requests.get(consumer_version_href, auth=(self.username, self.password))
        raw_consumer_version = r.json()
        return _pluck_pact(raw_pact, raw_consumer_version)


def _pluck_pact(raw_pact: Dict, raw_consumer_version: Dict) -> Pact:
    tags = [tag['name'] for tag in raw_consumer_version['_embedded']['tags']]
    consumer_version = raw_consumer_version['number']
    pact_json = {field: value for field, value in raw_pact.items()
                 if field not in ('createdAt', '_links')}
    return Pact(
        consumer_version=consumer_version,
        pact_version=_pluck_pact_version(raw_pact),
        tags=frozenset(tags),
        pact_json=pact_json
    )


def _pluck_pact_version(raw_pact: Dict) -> str:
    publish_href = raw_pact['_links']['pb:publish-verification-results']['href']
    match = re.search(r'/pact-version/(?P<provider_version>\w+)/verification-results', publish_href)
    if not match:
        raise RuntimeError(f'Failed to pluck pact version from pact {raw_pact}')

    return cast(str, match.group('provider_version'))


# i didn't realize that 'pact versions' existed while making this. maybe pacts can be merged
# on pact version, where multiple tags _and_ multiple consumer versions can be part of one pact.
#
# def _merge_tagged_pacts(pacts: List[Pact]) -> List[Pact]:
#     """
#     >>> a = Pact(consumer_version='x', pact_json={}, tags=frozenset(['feature-a']))
#     >>> b = Pact(consumer_version='y', pact_json={}, tags=frozenset(['feature-b']))
#     >>> c = Pact(consumer_version='x', pact_json={}, tags=frozenset(['master']))
#     >>> _merge_tagged_pacts([a, b, c]) == (
#     ... [Pact(consumer_version='y', pact_json={}, tags=frozenset({'feature-b'})),
#     ... Pact(consumer_version='x', pact_json={}, tags=frozenset({'feature-a', 'master'}))])
#     True
#     """
#     pact_by_version: Dict[str, Pact] = {}

#     for pact in pacts:
#         if pact.consumer_version not in pact_by_version:
#             pact_by_version[pact.consumer_version] = pact

#         else:
#             existing_pact = pact_by_version.pop(pact.consumer_version)
#             merged_pact = Pact(
#                 consumer_version=pact.consumer_version,
#                 tags=pact.tags | existing_pact.tags,
#                 pact_json=pact.pact_json
#             )
#             pact_by_version[pact.consumer_version] = merged_pact

#     return list(pact_by_version.values())
