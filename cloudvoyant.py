import argparse
import json

import requests as r

parser = argparse.ArgumentParser(description='Enumerate Azure AD Accounts.')
parser.add_argument('-u', '--upn',      help='Check if user exists.')
parser.add_argument('-l', '--list',     help='Check if users exist.')
parser.add_argument('-v', '--verbose',  action='store_true', help='Return valid and invalid users')
parser.add_argument('-vv','--vverbose', action='store_true', help='Return full response from GetCredentialType')
args = parser.parse_args()

endpoint = 'https://login.microsoftonline.com/common/GetCredentialType'

def callGetCredentialType(targets, mode=None):

    for t in targets:
        req = r.post(endpoint, data=f'{{"Username":"{t}"}}')
        d = json.loads(req.text)

        if mode is None:
            if (d['IfExistsResult'] == 0):
                print(t)
        elif (mode == 'full'):
            print(req.text)
        elif (mode == 'verbose'):
            if (d['IfExistsResult'] == 0):
                v = 'Exists'
            else:
                v = 'DNE'

            print(f'{t},{v}')

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

    callGetCredentialType(targets, mode)

if __name__ == "__main__":
    main()
