# cloudtrail_to_xlsx
Convert any number of CloudTrail log files into an XLSX file.

## Use Cases
* A first pass at collecting CloudTrail for Digital Forensics & Incident Response for Incidents in AWS
* Security Auditing, looking for Privilege Escalations

## Future Plans
I'm going to: 
1. extend this to search for known-bad behaviors, like Privilege Escalations
2. provide a CSV export option

## Usage
1. Download CloudTrail logs to your local filesystem
* `aws s3 sync s3://CLOUDTRAILBUCKET/KEY/ .`
2. Provide the path to the log files in a globular way:
* `AWSLogs/*/CloudTrail/*/*/*/*/*gz`
3. Provide an output filename
* `python3.7 cloudtrail_to_xlsx.py -r myResults.xlsx [-v] "AWSLogs/*/CloudTrail/*/*/*/*/*gz"`
4. You can filter by regions/date parts/account numbers by updating the path
* `python3.7 cloudtrail_to_xlsx.py -r myResults.xlsx [-v] "AWSLogs/*/CloudTrail/*/2019/06/*/*gz"`
