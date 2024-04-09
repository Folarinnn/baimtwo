# Setup Amazon Bedrock agent to call various models.

## Introduction
This project is intended to be a baseline for developers to extend there use cases with Amazon Bedrock agents across most available models in Bedrock. This README will guide you through setting this up step by step to empower you to further explore the capabilities of Bedrock agents. 

## Use cases for this project
- Multiple model result comparison
- Text generation 
- Summarization
- Text-to-sql
- Text-to-image
- Image-to-text
- Image scoring
- Problem solving
- Q&A
- RAG (optional)


## Prerequisites
- An active AWS Account.
- Familiarity with AWS services like Amazon Bedrock, S3, Lambda, Athena and Cloud9 , and Docker.

## Models this project currently supports:

### Anthropic: Claude
- anthropic.claude-3-haiku-20240307-v1:0
- anthropic.claude-3-sonnet-20240229-v1:0
- anthropic.claude-v2:1
- anthropic.claude-v2
- anthropic.claude-instant-v1

### Mistral: models
- mistral.mistral-large-2402-v1:0
- mistral.mistral-7b-instruct-v0:2
- mistral.mixtral-8x7b-instruct-v0:1

### Amazon: Titan Models
- amazon.titan-text-lite-v1
- amazon.titan-text-express-v1
- amazon.titan-image-generator-v1 (in preview)

### Meta: Llama models
- meta.llama2-13b-chat-v1
- meta.llama2-70b-chat-v1

### Cohere: Command Models
- cohere.command-text-v14
- cohere.command-light-text-v14

### Stability AI: SDXL Models
- stability.stable-diffusion-xl-v0
- stability.stable-diffusion-xl-v1

### AI21labs: Jurassic models
- ai21.j2-ultra-v1
- ai21.j2-mid-v1


## Diagram

![Diagram](images/diagram.png)

## Configuration and Setup

### Step 1: Setup ECR:

- The first thing we will do is setup a container registry in [ECR (Elastic Container registry)](https://aws.amazon.com/ecr/). This will be used to store our Docker container image for our Lambda function. 

-Log into the management console, and search ECR in the search bar at the top. Select the service, then `Create repository`.

![ecr btn](streamlit_app/images/ecr_create_btn.png)


### Step 2: Download project. Setup & run Docker
- We will need to run Docker in order to create a docker container image that will be used for our Lambda function. This function will be used with the action group of the agent in order to infer models. 

- Download the project from [here](https://github.com/jossai87/bedrock-agent-call-multiple-models/archive/refs/heads/main.zip). Once downloaded, please open up the project in your IDE of choice. For this project, I will be using [Visual Studio code](https://code.visualstudio.com/docs/sourcecontrol/intro-to-git)

- Navigate to the root directory of the project `bedrock-agent-call-multiple-models` in your IDE. Open a terminal here is well. 



### Step 2: Creating an S3 Bucket
- This step will be required in order to do image-to-text and text-to-image inference calls to certain models.
- Please make sure that you are in the **us-west-2** region. If another region is required, you will need to update the region in the `InvokeAgent.py` file on line 22 of the code. 
- Create an S3 bucket, and call it `agent-model-calls-alias`. We will use the default settings.
- Next, upload the image from [here](https://), to this S3 bucket


### Step 3: Create an Amazon ECR (Elastic Container Registry)
-


### Step 4: Lambda Function Configuration
- Create a Lambda function (Python 3.12) for the Bedrock agent's action group. We will call this Lambda function `agent-model-call-action`. 

### Step 5: Create Bedrock agent


### Step 6: Test various models



## Step 7: Setting Up and Running the Streamlit App
-  **Obtain the Streamlit App ZIP File**: Download the zip file of the project [here](https://github.com/build-on-aws/bedrock-agents-streamlit/archive/refs/heads/main.zip).



-  **Upload to Cloud9**:
   - In your Cloud9 environment, upload the ZIP file.

![Upload file to Cloud9](Streamlit_App/images/upload_file_cloud9.png)

   - Before going to the next step, make sure that the project finished uploading.
     
![Load wait](Streamlit_App/images/load_wait.png)


-  **Unzip the File**:
   - Use the following command  to extract the contents:
  
     ```bash
     unzip bedrock-agents-streamlit-main.zip
     ```
     
-  **Navigate to Streamlit_App Folder**:
   - Change to the directory containing the Streamlit app. Use this command
     ``` bash
     cd ~/environment/bedrock-agents-streamlit-main/Streamlit_App
     ```
     
-  **Update Configuration**:
   - Open the `InvokeAgent.py` file.
   - Update the `agentId` and `agentAliasId` variables with the appropriate values, then save it.

![Update Agent ID and alias](Streamlit_App/images/update_agentId_and_alias.png)

-  **Install Streamlit** (if not already installed):
   - Run the following command to install all of the dependencies needed:

     ```bash
     pip install streamlit boto3 pandas
     ```

-  **Run the Streamlit App**:
   - Execute the command:
     ```bash
     streamlit run app.py --server.address=0.0.0.0 --server.port=8080
     ```
   - Streamlit will start the app, and you can view it by selecting **Preview** within the Cloud9 IDE at the top, then **Preview Running Application**.
  
     ![Preview button](Streamlit_App/images/preview_btn.png)
     
     
   - Once the app is running, please test some of the sample prompts provided. (On 1st try, if you receive an error, try again.)

![Running App ](Streamlit_App/images/running_app.png)


   - Optionally, you can review the [trace events](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html) in the left toggle of the screen. This data will include the **Preprocessing, Orchestration**, and **PostProcessing** traces.

![Trace events ](Streamlit_App/images/trace_events.png)



## What we're doing here

1. create ECR
2. containerize application, then push to ECR
3. Configure Lamda resource policy, CPU & timeout from console
4. Create S3 & store API schema
5. Create agent & provide instruction
6. Create action group in agent using Lambda and api schema(in S3)


