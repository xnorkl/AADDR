#!/usr/bin/env python

import argparse
import json
import requests as r

# TODO -t -vv output should output JSON.

parser = argparse.ArgumentParser(description='Enumerate Azure AD Accounts.')

parser.add_argument(
    '-u', '--upn',
    help='Check if user exists.'
)

parser.add_argument(
    '-l', '--list',
    help='Check if users exist.'
)

parser.add_argument(
    '-t', '--tenantID',
    action='store_true',
    help='Return tenantID information.'
)

parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='Return valid and invalid users'
)

parser.add_argument(
    '-vv', '--vverbose',
    action='store_true',
    help='Return full response from GetCredentialType'
)

args = parser.parse_args()


def getDomains(targets):

    return set([t.split('@')[1] for t in targets if t])


def getOpenIDConfig(domains):

    def getRequest(d):
        endpoint = f'https://login.microsoftonline.com/{d}'
        endpoint = endpoint + '/v2.0/.well-known/openid-configuration'
        req = r.get(endpoint)
        tokenEndpoint = json.loads(req.text)['token_endpoint']
        return tokenEndpoint.split("/")[3]

    return {d: getRequest(d) for d in domains}


def getCredentialType(targets, mode):

    targets = [t for t in targets if t]

    def postRequest(target):

        endpoint = 'https://login.microsoftonline.com/common/GetCredentialType'
        response = r.post(endpoint, data=f'{{"Username":"{target}"}}')
        return response.text

    def ifExists(resp):
        d = json.dumps(resp)
        if d['IfExistsResult'] != 1:
            return 'Exists'
        else:
            return 'DNE'

    if mode is None:
        return [t for t in targets if ifExists(postRequest(t)) == 'Exists']
    elif mode == 'verbose':
        return [f'{t},{ifExists(postRequest(t))}' for t in targets]
    elif mode == r'full':
        return [postRequest(t) for t in targets]


def main():

    if args.verbose is not False:
        mode = 'verbose'
    elif args.vverbose is not False:
        mode = 'full'
    else:
        mode = None

    if args.list is not None:
        with open(args.list) as f:
            targets = f.read().splitlines()

    elif args.upn is not None:
        targets = [args.upn]

    if args.tenantID:
        print(getOpenIDConfig(getDomains(targets)))

    print(*getCredentialType(targets, mode), sep='\n')


if __name__ == "__main__":
    main()
