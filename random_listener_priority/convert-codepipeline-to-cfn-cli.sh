#!/bin/bash
test ! -z $1 || echo -e "\n#### Convert a CF Pipeline Parameters json file to generate a CFN CLI Parameters json file ####"
test ! -z $1 || echo -e "#### ./convert-codepipeline-to-cfn-cli.sh cfn-codepipeline-parameters.json > parameters.json ####\n"
test -z $1 || \
    cat $1 | \
        jq .Parameters | \
        jq -r 'to_entries[] | try "{\"ParameterKey\":\"\(.key)\",\"ParameterValue\":\"\(.value)\"},"' | \
        tr -d '\n' |
        sed 's/^/[/g; s/,$/]/g' | \
        jq

## json to env vars
## env -i $(cat cfn-codepipeline-parameters.json | jq .Parameters | jq -r 'to_entries[] | try "\(.key)=\(.value)"') bash

## CF CLI
# ./convert-codepipeline-to-cfn-cli.sh cfn-codepipeline-parameters.json > parameters.json
# aws cloudformation update-stack \
#     --stack-name dev-spider \
#     --template-body file://cf-ecs-deploy.yaml \
#     --parameters file://parameters.json \
#     --capabilities CAPABILITY_IAM \
#     --profile default \
#     --role-arn arn:aws:iam::111111111111:role/CloudFormationRole