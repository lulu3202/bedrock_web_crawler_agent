
# Amazon Bedrock Agent to Webscrape

This is an implementation of https://github.com/build-on-aws/bedrock-agents-webscraper?tab=readme-ov-file#step-1-aws-lambda-function-configuration

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Library dependencies](#library-dependencies)
4. [Diagram](#diagram)
5. [Grant Model Access](#grant-model-access)
6. [Deploy Resources via AWS CloudFormation for the Amazon Bedrock Agent](#deploy-resources-via-aws-cloudformation-for-the-amazon-bedrock-agent)
7. [Step-by-step Setup for the Amazon Bedrock Agent](#step-by-step-setup-for-the-amazon-bedrock-agent)
   - [Step 1: AWS Lambda Function Configuration](#step-1-aws-lambda-function-configuration)
   - [Step 2: Create & Attach an AWS Lambda Layer](#step-2-create--attach-an-aws-lambda-layer)
   - [Step 3: Setup Bedrock Agent and Action Group](#step-3-setup-bedrock-agent-and-action-group)
   - [Step 4: Create an Alias](#step-4-create-an-alias)
8. [Step 5: Testing the Setup](#step-5-testing-the-setup)
   - [Testing the Bedrock Agent](#testing-the-bedrock-agent)
9. [Step 6: Setup and Run Streamlit App on EC2 (Optional)](#step-6-setup-and-run-streamlit-app-on-ec2-optional)
10. [Cleanup](#cleanup)

