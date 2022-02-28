import json
import os
import random
import uuid
import boto3
import requests
SUCCESS = "SUCCESS"
FAILED = "FAILED"
#
# Member must have value less than or equal to 50000
#
LISTENER_RULE_PRIORITY_RANGE = 1, 50000
def lambda_handler(event, context):
    try:
        _lambda_handler(event, context)
    except Exception as e:
        # Must raise, otherwise the Lambda will be marked as successful, and the exception
        # will not be logged to CloudWatch logs.
        # Always send a response otherwise custom resource creation/update/deletion will be stuck
        send(
            event,
            context,
            response_status=FAILED if event['RequestType'] != 'Delete' else SUCCESS,
            # Do not fail on delete to avoid rollback failure
            response_data=None,
            physical_resource_id=uuid.uuid4(),
            reason=e,
        )
        raise
def _lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    physical_resource_id = event.get('PhysicalResourceId', str(uuid.uuid4()))
    response_data = {}
    if event['RequestType'] == 'Create':
        elbv2_client = boto3.client('elbv2')
        result = elbv2_client.describe_rules(ListenerArn=os.environ['LISTENER_ARN'])
        in_use = list(filter(lambda s: s.isdecimal(), [r['Priority'] for r in result['Rules']]))
        priority = None
        while not priority or priority in in_use:
            priority = str(random.randint(*LISTENER_RULE_PRIORITY_RANGE))
        response_data = {
            'Priority': priority
        }
    send(event, context, SUCCESS, response_data, physical_resource_id)
def send(event, context, response_status, response_data, physical_resource_id, reason=None):
    response_url = event['ResponseURL']
    response_body = {
        'Status': response_status,
        'Reason': str(reason) if reason else 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
        'PhysicalResourceId': physical_resource_id,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': response_data,
    }
    json_response_body = json.dumps(response_body)
    headers = {
        'content-type': '',
        'content-length': str(len(json_response_body))
    }
    try:
        requests.put(
            response_url,
            data=json_response_body,
            headers=headers
        )
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))
