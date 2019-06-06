import boto3
import glob
import gzip
import io
import json
import os
import sys
import argparse
import pandas as pd
import numpy as np

"""
Parses CloudTrail log files, combines them, and writes them to an XLSX file

Sync the relevant files to your local filesystem
Pass in the path to the .json.gz files as a "globular" express in quotes
Provide a results file name

"""

parser = argparse.ArgumentParser(description='Parse CloudTrail JSON files.')
parser.add_argument('-r', '--resultfile', metavar="path", type=str, help='JSON file to be analyzed ')
parser.add_argument('jsfile', metavar="path", type=str, help='JSON file(s) to be analyzed. Expects a glob: AWSLogs/*/CloudTrail/*/*/*/*/*gz')
parser.add_argument('--verbose', '-v', action='count')
args = parser.parse_args()
if args.resultfile is not None:
    extension = os.path.splitext(args.resultfile)[1]
    if extension != ".xlsx":
        resultfile = args.resultfile + ".xlsx"
    else:
        resultfile = args.resultfile
else:
    resultfile = 'results.xlsx'
files = glob.glob(args.jsfile)
global myDf
myDf = []
if not files:
    print('File does not exist: ' + args.jsfile, file=sys.stderr)
for file in files:
    if args.verbose is not None:
        print('File exists: ' + file)
    extension = os.path.splitext(file)[1]
    if extension == ".gz":
        with gzip.open(file, 'rt', encoding='utf-8') as f:
            myLogsJson  = json.load(f)
    else:
        with open(file, 'rt', encoding='utf8') as jsfile:
            myLogsJson = json.loads(jsfile.read())

    myDf.append(pd.io.json.json_normalize(myLogsJson['Records']))
unsortedDf = pd.concat(myDf, sort=False)
myDf = unsortedDf.sort_values(by=['eventTime'])
if args.verbose is not None:
    print(myDf.shape)
myDf.to_excel(resultfile, index=False,sheet_name='RawCloudTrailLogs')
