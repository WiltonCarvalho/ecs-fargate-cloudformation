#!/usr/bin/python
import json
import os
import random
import uuid
import boto3
#from botocore.vendored import requests
SUCCESS = "SUCCESS"
FAILED = "FAILED"
# Member must have value less than or equal to 50000
LISTENER_RULE_PRIORITY_RANGE = 1, 5000

response_data = {}
elbv2_client = boto3.client('elbv2')
result = elbv2_client.describe_rules(ListenerArn=os.environ['LISTENER_ARN'])
in_use = list(filter(lambda s: s.isdecimal(), [r['Priority'] for r in result['Rules']]))
priority = None
while not priority or priority in in_use:
    priority = str(random.randint(*LISTENER_RULE_PRIORITY_RANGE))
data = {
    'current_listener_priorities': in_use,
    'new_listener_priority': priority
}
response_data = json.dumps(data)

print(response_data)
