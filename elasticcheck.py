import requests
import json
import argparse
import sys

parser = argparse.ArgumentParser(description='Check Elasticsearch Pipelines against testcases')
parser.add_argument('--prepare', action='store_true', help='send specified pipelines to elasticsearch')
parser.add_argument('elasticurl', metavar='ELASTICURL', help='URL to elasticsearch server')
parser.add_argument('pipefile', metavar='FILE', help='URL to elasticsearch server')
cmdline = parser.parse_args()

with open(cmdline.pipefile, 'r') as f:
    jsonInput = json.load(f)

if cmdline.prepare:
    # input file should have been a pipeline -> send it to elasticsearch
    pipeName = jsonInput["name"]
    pipelineDefinition = jsonInput["pipeline"]
    url = f'{cmdline.elasticurl}/_ingest/pipeline/{pipeName}'
    r = requests.put(url, json=pipelineDefinition)
    if r.status_code >= 200 and r.status_code < 300:
        print(f'SUCCESS: {cmdline.pipefile} Creating pipeline {pipeName} returned {r.status_code} - {r.json()}')
        sys.exit(0)
    else:
        print(f'FAILED: {cmdline.pipefile} Creating pipeline {pipeName} returned {r.status_code} - {r.json()}')
        sys.exit(1)
else:
    # run actual tests - json input must be a testcase
    # We must have "pipeline", "assertions" and "input" in the file
    pipeName = jsonInput["pipeline"]
    assertions = jsonInput["assertions"]
    testdoc = jsonInput["input"]
    url = f'{cmdline.elasticurl}/_ingest/pipeline/{pipeName}/_simulate'

    elasticinput = {}
    elasticinput["docs"] = []
    elasticinput["docs"].append(testdoc)
    r = requests.post(url, json=elasticinput)
    if r.status_code >= 200 and r.status_code < 300:
        print(f'SUCCESS: {cmdline.pipefile} Simulating pipeline {pipeName} returned {r.status_code}')
    else:
        print(f'FAILED: {cmdline.pipefile} Simuating pipeline {pipeName} returned {r.status_code} - {r.json()}')
        sys.exit(1)

    # We'll only pass in one doc, so we will only get one doc out
    response = r.json()["docs"][0]["doc"]["_source"]

    for key in assertions:
        # Check for existence of asserted key
        if key not in response:
            print(f'FAILED: {cmdline.pipefile} Asserted key "{key}" was not found in response.')
        else:
            # check that key value exactly matches the assertion
            if response[key] != assertions[key]:
                print(f'FAILED: {cmdline.pipefile} Content of asserted key "{key} does not match: Asserted: "{assertions[key]}", found: "{response[key]}"')
            else:
                print(f'SUCCESS: {cmdline.pipefile} Assertion for key {key} matched.')

