import argparse
import importlib
import os
from typing import NoReturn

from faaspact_verifier import use_verifier
from faaspact_verifier.context import create_default_context


def cli() -> NoReturn:
    args = _parse_args()
    faasport_module = importlib.import_module(args.faasport_module)
    user_faasport = faasport_module.faasport.__globals__['user_faasport']  # type: ignore
    user_provider_state_fixture_by_descriptor = (
        faasport_module.provider_state.__globals__[  # type: ignore
            'user_provider_state_fixture_by_descriptor'
        ]
    )
    context = create_default_context(args.host, args.username, args.password)

    succeeded = use_verifier(
        context,
        args.provider,
        user_provider_state_fixture_by_descriptor,
        user_faasport,
        args.publish_results,
        failon=frozenset(args.failon),
        provider_version=args.provider_version
    )

    if succeeded:
        exit(0)
    else:
        exit(1)


def _parse_args() -> argparse.Namespace:
    """Helper function to create the command-line argument parser for faaspact_verifier.  Return the
    parsed arguments as a Namespace object if successful. Exits the program if unsuccessful or if
    the help message is printed.
    """
    description = ('Run pact verifier tests against a faas microservice.')
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--host',
                        default=os.environ.get('PACT_BROKER_HOST'),
                        help='Pact broker host. (default=env.PACT_BROKER_HOST)')

    parser.add_argument('--username',
                        default=os.environ.get('PACT_BROKER_USERNAME'),
                        help='Pact broker username. (default=env.PACT_BROKER_USERNAME)')

    parser.add_argument('--password',
                        default=os.environ.get('PACT_BROKER_PASSWORD'),
                        help='Pact broker password. (default=env.PACT_BROKER_PASSWORD)')

    parser.add_argument('-f', '--faasport-module',
                        default=os.environ.get('FAASPORT_MODULE'),
                        help='Python path to faasport module. (default=env.FAASPORT_MODULE)')

    parser.add_argument('-p', '--provider',
                        default=os.environ.get('PACT_PROVIDER'),
                        help='Name of the provider. (default=env.PACT_PROVIDER)')

    parser.add_argument('--publish-results',
                        action='store_true',
                        default=False,
                        help='If true, publish verification results to the broker.')

    parser.add_argument('--provider-version',
                        required=True,
                        help='The version of the provider. Should be the git sha.')

    parser.add_argument('--failon',
                        action='append',
                        default=['master'],
                        help=('If verification fails for a pact with one of these tags, this script'
                              ' will fail.'))

    args = parser.parse_args()

    if not args.host:
        raise parser.error('Missing host')

    if not args.username:
        raise parser.error('Missing username')

    if not args.password:
        raise parser.error('Missing password')

    if not args.faasport_module:
        raise parser.error('Missing faasport_module')

    if not args.provider:
        raise parser.error('Missing provider')

    return args
