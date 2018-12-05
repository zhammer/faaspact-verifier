from typing import Dict

import pytest

from faaspact_verifier.definitions import Error, Interaction, Request, Response
from faaspact_verifier.gateways.pactman_verifier import PactmanVerifier


class TestVerifyInteraction:

    @pytest.mark.parametrize('response, should_verify', [  # type: ignore
        pytest.param(Response({}, 200, {'hello': 'world'}), True, id='Body matches'),
        pytest.param(Response({}, 200, {'hello': 'there'}), False, id='Body doesnt match'),
        pytest.param(Response({}, 400, {'hello': 'world'}), False, id='Status doesnt match'),
        pytest.param(Response({'Auth': 'XYZ'}, 200, {'hello': 'world'}), True, id='Xtra headers ok')
    ])
    def test_response_equality(self, response: Response, should_verify: bool) -> None:
        # Given
        interaction_response = Response(
            headers={},
            status=200,
            body={'hello': 'world'},
            matching_rules=None
        )
        interaction = _make_interaction(interaction_response)
        emulator_result = response

        # When
        verification_result = PactmanVerifier()._verify_interaction(interaction, emulator_result)

        # Then
        assert verification_result.verified == should_verify
        if not should_verify:
            assert verification_result.reason

    def test_fails_if_emulator_result_is_error(self) -> None:
        # Given
        interaction_response = Response(
            headers={},
            status=200,
            body={'hello': 'world'},
            matching_rules=None
        )
        interaction = _make_interaction(interaction_response)
        emulator_result = Error(message='Provider errored during execution')

        # When
        verification_result = PactmanVerifier()._verify_interaction(interaction, emulator_result)

        # Then
        assert not verification_result.verified
        assert verification_result.reason == emulator_result.message

    @pytest.mark.parametrize('body, should_verify', [  # type: ignore
        pytest.param({
            'friends': ['gabe', 'yuval'],
            'score': 123,
            'joined': '2012-12-05'}, True, id='exact match'),
        pytest.param({
            'friends': ['chris', 'evan', 'shula'],
            'score': 456,
            'joined': '1994-04-26'}, True, id='not exact match but rules match'),
        pytest.param({
            'friends': ['gabe', 123],
            'score': 123,
            'joined': '2012-12-05'}, False, id='array element type mismatch'),
        pytest.param({
            'friends': ['gabe', 'yuval'],
            'score': '123',
            'joined': '2012-12-05'}, False, id='scalar elemnt type mismatch'),
        pytest.param({
            'friends': [],
            'score': 123,
            'joined': '2012-12-05'}, False, id='array length less than min'),
        pytest.param({
            'friends': ['gabe', 'yuval'],
            'score': 123,
            'joined': '2012-12-5'}, False, id='regex match fails')
    ])
    def test_body_matching_rules(self, body: Dict, should_verify: bool) -> None:
        # Given
        interaction_response = Response(
            headers={},
            status=200,
            body={
                'friends': ['gabe', 'yuval'],
                'score': 123,
                'joined': '2012-12-05'
            },
            matching_rules={
                'body': {
                    '$.friends': {
                        'matchers': [{
                            'min': 1,
                            'match': 'type'
                        }]
                    },
                    '$.score': {
                        'matchers': [{
                            'match': 'type'
                        }]
                    },
                    '$.joined': {
                        'matchers': [{
                            'regex': r'\d\d\d\d-\d\d-\d\d'
                        }]
                    }

                }
            }
        )
        interaction = _make_interaction(interaction_response)
        emulator_result = Response({}, 200, body)

        # When
        verification_result = PactmanVerifier()._verify_interaction(interaction, emulator_result)

        # Then
        assert verification_result.verified == should_verify
        if not should_verify:
            assert verification_result.reason

    @pytest.mark.parametrize('headers, should_verify', [  # type: ignore
        pytest.param({'Content-Type': 'application/json'}, True, id='exact match'),
        pytest.param({'Content-Type': 'application/xml'}, True, id='regex match'),
        pytest.param({'Content-Type': 'multipart/form-data'}, False, id='regex doesnt match')
    ])
    def test_header_matching_rules(self, headers: Dict, should_verify: bool) -> None:
        # Given
        interaction_response = Response(
            headers={'Content-Type': 'application/json'},
            status=200,
            matching_rules={
                'header': {
                    'Content-Type': {
                        'matchers': [{
                            'regex': r'application/(json|xml)'
                        }]
                    }
                }
            }
        )
        interaction = _make_interaction(interaction_response)
        emulator_result = Response(headers, 200)

        # When
        verification_result = PactmanVerifier()._verify_interaction(interaction, emulator_result)

        # Then
        assert verification_result.verified == should_verify
        if not should_verify:
            assert verification_result.reason


def _make_interaction(response: Response) -> Interaction:
    return Interaction(
        request=Request({}, '/', 'POST'),
        response=response,
        provider_states=tuple()
    )
