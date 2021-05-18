#!/usr/bin/env python
import argparse
import boto3
import os

from time import sleep


os.chdir(os.path.dirname(os.path.realpath(__file__)))

PROJECT_CODE = 'ledger-support'
LEDGER_CREATION_POLL_PERIOD_SEC = 10
ACTIVE_STATE = "ACTIVE"

# =======================================================================
# Read input parameters
# =======================================================================
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region', required=False,
                    default='us-east-1', help='AWS CLI region to use')
parser.add_argument('-s', '--stage',
                    help='Stage name or environment such as dev, stage, uat, etc.', required=True)
args = parser.parse_args()

# =======================================================================
# Initialize boto3
# =======================================================================
session = boto3.Session(region_name=args.region)

# =======================================================================
# Set variables
# =======================================================================
stage = args.stage

qldb_client = session.client('qldb')

# Create the ledger for use
ledger_name = f'{PROJECT_CODE}-{stage}-audit-trail'

print(f'Creating the ledger {ledger_name}')
result = qldb_client.create_ledger(Name=ledger_name, PermissionsMode='ALLOW_ALL')
print('Success; ledger state: {}'.format(result.get('State')))

print('Waiting for ledger to become active...')
while True:
    result = qldb_client.describe_ledger(Name=ledger_name)
    if result.get('State') == ACTIVE_STATE:
        print('Success. Ledger is active and ready to use.')
        break
    else:
        print('The ledger is still creating. Please wait...')
        sleep(LEDGER_CREATION_POLL_PERIOD_SEC)

