# Setup Amazon Bedrock agent, knowledge base, and action group with Streamlit

## Introduction
This project is intended to be a baseline for developers to extend there use cases with Amazon Bedrock agents across most available models in Bedrock. This README will guide you through setting this up step by step to empower you to further explore the capabilities of Bedrock agents. 


## Prerequisites
- An active AWS Account.
- Familiarity with AWS services like Amazon Bedrock, S3, Lambda, Athena and Cloud9 , and Docker.

## Models this project currently supports:

### Anthropic: Claude
anthropic.claude-3-haiku-20240307-v1:0
anthropic.claude-3-sonnet-20240229-v1:0
anthropic.claude-v2:1
anthropic.claude-v2
anthropic.claude-instant-v1

### Mistral: models
mistral.mistral-large-2402-v1:0
mistral.mistral-7b-instruct-v0:2
mistral.mixtral-8x7b-instruct-v0:1

### Meta: Llama models
meta.llama2-13b-chat-v1
meta.llama2-70b-chat-v1

### Amazon: Titam Models
amazon.titan-text-lite-v1
amazon.titan-text-express-v1
amazon.titan-image-generator-v1 (in preview)

### Cohere: Command Models
cohere.command-text-v14
cohere.command-light-text-v14

### AI21labs: Jurassic models
ai21.j2-ultra-v1
ai21.j2-mid-v1


## What we're doing here

1. create ECR
2. containerize application, then push to ECR
3. Configure Lamda resource policy, CPU & timeout from console
4. Create S3 & store API schema
5. Create agent & provide instruction
6. Create action group in agent using Lambda and api schema(in S3)


