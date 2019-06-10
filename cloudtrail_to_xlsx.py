import boto3
import glob
import gzip
import io
import json
import logging
import os
import sys
import argparse
import pandas as pd
import numpy as np
from progress.bar import IncrementalBar


"""
Parses CloudTrail log files, combines them, and writes them to an XLSX file

Sync the relevant files to your local filesystem
Pass in the path to the .json.gz files as a "globular" express in quotes
Provide a results file name

"""


parser = argparse.ArgumentParser(description='Parse CloudTrail JSON files.')
parser.add_argument('-r', '--resultfile', type=str,
                    help=('Result File.  A ".csv" extension will create'
                          'a CSV file. An ".xlsx" or no extension will'
                          ' generate an .xlsx file.'))
parser.add_argument('jsfile', metavar="path", type=str,
                    help='JSON file(s) to be analyzed. Expects a glob: "AWSLogs/*/CloudTrail/*/*/*/*/*gz"')
parser.add_argument('--verbose', '-v', action='count')
args = parser.parse_args()

if args.verbose is not None:
    logging.basicConfig(level=logging.DEBUG)

if args.resultfile is not None:
    resFileExt = os.path.splitext(args.resultfile)[1]
    if resFileExt != ".xlsx" and resFileExt != ".csv":
        resultfile = args.resultfile + ".xlsx"
    else:
        resultfile = args.resultfile
else:
    resultfile = 'results.xlsx'
logging.debug('args.jsfile: ' + args.jsfile)
logging.debug('resultfile: ' + resultfile)
files = glob.glob(args.jsfile)
global myDf
myDf = []
if not files:
    print('File does not exist: ' + args.jsfile, file=sys.stderr)
    print(files)
    exit()

bar = IncrementalBar('Processing CloudTrail Files', max=len(files))
for file in files:
    bar.next()
    if args.verbose is not None:
        print('File exists: ' + file)
    extension = os.path.splitext(file)[1]
    if extension == ".gz":
        with gzip.open(file, 'rt', encoding='utf-8') as f:
            myLogsJson = json.load(f)
    else:
        with open(file, 'rt', encoding='utf8') as jsfile:
            myLogsJson = json.loads(jsfile.read())
    myDf.append(pd.io.json.json_normalize(myLogsJson['Records']))
bar.finish()
logging.debug("myDf List Size: " + str(len(myDf)))
print("Combining records. This may take a minute. {:.1f} KB".format(sys.getsizeof(myDf)/1024))
unsortedDf = pd.concat(myDf, sort=False)
print("Sorting {:,} records. This may take a minute. {:,} KB".format(len(unsortedDf), int(sys.getsizeof(unsortedDf)/1024)))
myDf = unsortedDf.sort_values(by=['eventTime'])
if args.verbose is not None:
    print(myDf.shape)
logging.debug('Result File: ' + resultfile)
logging.debug('Extension: ' + resFileExt)

dangerList = ['AddUserToGroup', 'CreateAccessKey', 'CreateLoginProfile',
              'UpdateLoginProfile', 'AttachUserPolicy', 'AttachGroupPolicy',
              'AttachRolePolicy', 'PutUserPolicy', 'PutGroupPolicy',
              'PutRolePolicy', 'CreatePolicy', 'CreatePolicyVersion',
              'SetDefaultPolicyVersion', 'PassRole', 'CreateInstanceProfile',
              'AddRoleToInstanceProfile', 'UpdateAssumeRolePolicy']
logging.debug(dangerList)

dangerousDf = myDf[myDf.eventName.isin(dangerList)]
logging.debug(dangerousDf.shape)

if (resFileExt == ".csv"):
    myDf.to_csv(resultfile, index=False)
    if not dangerousDf.empty:
        dangerousDf.to_csv('dangerous.csv', index=False)
    logging.debug('Inside if extension == csv')
else:
    logging.debug('Inside if extension false')
    myDf.to_excel(resultfile, index=False, sheet_name='RawCloudTrailLogs')
    if not dangerousDf.empty:
        dangerousDf.to_excel(resultfile, index=False, sheet_name='DangerCalls')
