import json
import os
import base64
import logging
import boto3
import io
import time
from PIL import Image
from botocore.exceptions import ClientError
from langchain.llms.bedrock import Bedrock
#from langchain_community.chat_models import BedrockChat

s3 = boto3.client('s3')
logger = logging.getLogger(__name__)
bucket_name = 'bedrock-agent-images'  # Replace with the name of your bucket
object_name = 'mypic.png' 

def lambda_handler(event, context):
    print(event)
    
    def get_named_parameter(event, name):
        return next(item for item in event['parameters'] if item['name'] == name)['value']

    model_id = get_named_parameter(event, 'modelId')
    prompt = get_named_parameter(event, 'prompt')
    #encoded_image = get_named_parameter(event, 'image')
    print("MODE ID: " + model_id)
    print("PROMPT: " + prompt)

    def get_image_response(client, prompt_content): #text-to-text client function
        
        if(model_id.startswith('stability')):
            request_body = json.dumps({"text_prompts": 
                                    [ {"text": prompt_content} ], #prompts to use
                                    "cfg_scale": 9, #how closely the model tries to match the prompt
                                    "steps": 50, }) #number of diffusion steps to perform
            try:
                response = client.invoke_model(body=request_body, modelId=model_id) #call the Bedrock endpoint
                payload = json.loads(response.get('body').read()) #load the response body into a json object 
                images = payload.get('artifacts') #extract the image artifacts
                
                # Check if images is None or empty
                if not images or 'base64' not in images[0]:
                    logging.error("No images found or 'base64' key is missing.")
                    return "No image data found in the response."
                
                image_data = base64.b64decode(images[0].get('base64')) #decode image
                image = io.BytesIO(image_data) #return a BytesIO object for client app consumption
                                
                return image

            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                return (f"An error occurred processing the image response:  {str(e)}")
        
        elif(model_id == 'amazon.titan-image-generator-v1'):           
            request_body = json.dumps({
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": prompt_content
                },
                "imageGenerationConfig": {
                    "numberOfImages": 2,
                    "height": 1024,
                    "width": 1024,
                    "cfgScale": 8.0,
                    "seed": 0
                }
            })

            def generate_image(model_id, body):
                """
                Generate an image using Amazon Titan Image Generator G1 model on demand.
                Args:
                    model_id (str): The model ID to use.
                    body (str) : The request body to use.
                Returns:
                    image_bytes (bytes): The image generated by the model.
                """

                logger.info("Generating image with Amazon Titan Image Generator G1 model %s", model_id)
                bedrock = boto3.client(service_name='bedrock-runtime')
                accept = "application/json"
                content_type = "application/json"

                response = bedrock.invoke_model(
                    body=body, modelId=model_id, accept=accept, contentType=content_type
                )
                response_body = json.loads(response.get("body").read())
                base64_image = response_body.get("images")[0]
                base64_bytes = base64_image.encode('ascii')
                image_bytes = base64.b64decode(base64_bytes)
                finish_reason = response_body.get("error")

                if finish_reason is not None:
                    raise ImageError(f"Image generation error. Error is {finish_reason}")

                logger.info(
                    "Successfully generated image with Amazon Titan Image Generator G1 model %s", model_id)

                return image_bytes

            try:
                image_bytes = generate_image(model_id=model_id, body=request_body)
                image = Image.open(io.BytesIO(image_bytes))
                image.show()

                return image

            except ClientError as err:
                message = err.response["Error"]["Message"]
                logger.error("A client error occurred: %s", message)
                print("A client error occured: " +
                    format(message))
            except ImageError as err:
                logger.error(err.message)
                print(err.message)

        else:
            print(
                f"Finished generating image with Amazon Titan Image Generator G1 model {model_id}.")


        
    class Claude3Wrapper:
        """Encapsulates Claude 3 model invocations using the Amazon Bedrock Runtime client."""
        def __init__(self, client=None):
            self.client = client or boto3.client(
                service_name="bedrock-runtime", region_name=os.environ.get("BWB_REGION_NAME")
            )

        def invoke_claude_3_with_text(self, prompt):
            """
            Invokes Anthropic Claude 3 Sonnet to run an inference using the input provided in the request body.
            """
            try:
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(
                        {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 1024,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [{"type": "text", "text": prompt}],
                                }
                            ],
                        }
                    ),
                )

                result = json.loads(response.get("body").read())
                input_tokens = result["usage"]["input_tokens"]
                output_tokens = result["usage"]["output_tokens"]
                output_list = result.get("content", [])
                

                print("Invocation details:")
                print(f"- The input length is {input_tokens} tokens.")
                print(f"- The output length is {output_tokens} tokens.")
                
                return output_list

            except ClientError as err:
                logger.error("Couldn't invoke Claude 3 with text. Error: %s", err)
                raise

        def invoke_claude_3_multimodal(self, prompt, base64_image_data):
            """
            Invokes Anthropic Claude 3 Haiku to run a multimodal inference using the input provided in the request body.
            """

            try:
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2048,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": base64_image_data,
                                    },
                                },
                            ],
                        }
                    ],
                }

                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(request_body),
                )

                result = json.loads(response.get("body").read())
                input_tokens = result["usage"]["input_tokens"]
                output_tokens = result["usage"]["output_tokens"]
                output_list = result.get("content", [])
                

                print("Invocation details:")
                print(f"- The input length is {input_tokens} tokens.")
                print(f"- The output length is {output_tokens} tokens.")
                
                return output_list

            except ClientError as err:
                logger.error("Couldn't invoke Claude 3 multimodally. Error: %s", err)
                raise

    class ImageError(Exception):
        "Custom exception for errors returned by Amazon Titan Image Generator G1"

        def __init__(self, message):
            self.message = message

    def get_inference_parameters(model): #return a default set of parameters based on the model's provider
        bedrock_model_provider = model.split('.')[0] #grab the model provider from the first part of the model id
        
        if (bedrock_model_provider == 'mistral'):
            #example modelID: mistral.gpt-3.5-turbo
            #example modelID: mistral.mistral-large-2402-v1:0
            return {
                "max_tokens": 200,
                "temperature": 0.5,
                "top_k": 50,
                "top_p": 0.9,
            }
        elif (bedrock_model_provider == 'ai21'): #AI21
            #example modelID: ai21.j2-ultra-v1
            return { #AI21
                "maxTokens": 512, 
                "temperature": 0, 
                "topP": 0.5, 
                "stopSequences": [], 
                "countPenalty": {"scale": 0 }, 
                "presencePenalty": {"scale": 0 }, 
                "frequencyPenalty": {"scale": 0 } 
            }    
        elif (bedrock_model_provider == 'cohere'): #COHERE
            #example modelID: cohere.command-text-v14
            return {
                "max_tokens": 512,
                "temperature": 0,
                "p": 0.01,
                "k": 0,
                "stop_sequences": [],
                "return_likelihoods": "NONE"
            }   
        elif (bedrock_model_provider == 'meta'): #META
            #example modelID: meta.llama2-70b-chat-v1
            return {
                "temperature": 0,
                "top_p": 0.9,
                "max_gen_len": 512
            }  
        elif (bedrock_model_provider == 'stability'): #META
            #example modelID: stability.stable-diffusion-xl-v0
            return {
                "weight": 1,
                "cfg_scale": 10,
                "seed": 0,
                "steps": 50,
                "width": 512,
                "height": 512
            }         
        elif(bedrock_model_provider == 'anthropic'): #Anthropic
            #example modelID: openai.gpt-3.5-turbo
            return { 
                "max_tokens_to_sample": 300,
                "temperature": 0.5, 
                "top_k": 250, 
                "top_p": 1, 
                "stop_sequences": ["\n\nHuman:"],
                "anthropic_version": "bedrock-2023-05-31" 
            }
        elif(model_id == 'amazon.titan-image-generator-v1'):
            #example modelID: anthropic.claude-3-haiku-20240307-v1:0
            return {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": "string",      
                    "negativeText": "string"
                },
                "imageGenerationConfig": {
                    "numberOfImages": int,
                    "height": int,
                    "width": int,
                    "cfgScale": float,
                    "seed": int
                }
            }
        else: #Amazon
            #For the LangChain Bedrock implementation, these parameters will be added to the 
            #textGenerationConfig item that LangChain creates for us
            return { 
                "maxTokenCount": 512, 
                "stopSequences": [], 
                "temperature": 0, 
                "topP": 0.9 
            }
        
    def get_text_response(model_id, prompt):
        client = boto3.client(service_name="bedrock-runtime", region_name=os.environ.get("BWB_REGION_NAME"))
        encoded_image = None

        try:
            # Check if the file exists in S3
            s3.head_object(Bucket=bucket_name, Key=object_name)
            file_exists = True
        except ClientError as e:
            # If a ClientError is thrown, check if it was a 404 error
            # which means the object does not exist.
            if e.response['Error']['Code'] == '404':
                file_exists = False
            else:
                # Reraise the exception if it was a different error
                raise

        if file_exists:
            # Create a BytesIO object to store image data from S3
            file_stream = io.BytesIO()
            s3.download_fileobj(bucket_name, object_name, file_stream)

            # Reset the file pointer to the beginning after download
            file_stream.seek(0)

            # Directly encode the downloaded image data to base64
            encoded_image = base64.b64encode(file_stream.getvalue()).decode('utf-8')
            # Here you can use encoded_image as needed
            print("File exists and has been encoded.")
        else:
            print("File does not exist in the bucket.")

            # Load the image file into a variable
            #fetched_image = Image.open(file_stream)   

        if model_id == 'anthropic.claude-3-haiku-20240307-v1:0' or model_id == 'anthropic.claude-3-sonnet-20240229-v1:0':
            # Invoke Claude 3 with text to text
            wrapper = Claude3Wrapper(client)
            if not encoded_image:
                return wrapper.invoke_claude_3_with_text(prompt)
            else:
                # Invoke Claude 3 with image to text
                return wrapper.invoke_claude_3_multimodal(prompt, encoded_image)
            
        # Conditional check for model_id starting with 'stability'
        elif model_id.startswith('stability'):
            def save_image_to_s3(image_bytes_io, bucket, object_name):
                """
                Saves an image (provided as a BytesIO object) to an S3 bucket for 'stability' models.
                """
                image = Image.open(image_bytes_io)
                output_image_bytes = io.BytesIO()
                image.save(output_image_bytes, format='PNG')
                output_image_bytes.seek(0)
                s3.put_object(Bucket=bucket, Key=object_name, Body=output_image_bytes.getvalue())
                print(f"Image successfully saved to s3://{bucket}/{object_name}")

            image_response = get_image_response(client, prompt)
            generated_object_name = 'generated_images/image_{}.png'.format(int(time.time()))      
            save_image_to_s3(image_response, bucket_name, generated_object_name)
            return "Stability image created and saved successfully"

        # Conditional check for model_id equal to 'amazon.titan-image-generator-v1'
        elif model_id == 'amazon.titan-image-generator-v1':
            def save_image_to_s3(image, bucket, object_name):
                """
                Saves an image (provided as a PIL Image object) to an S3 bucket for 'amazon.titan-image-generator-v1' models.
                """
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='PNG')
                image_bytes.seek(0)
                s3.put_object(Bucket=bucket, Key=object_name, Body=image_bytes)
                print(f"Image successfully saved to s3://{bucket}/{object_name}")

            # Your existing code to get and process the image
            image_response = get_image_response(client, prompt)  # Assuming this returns a PIL Image object
            generated_object_name = 'generated_images/image_{}.png'.format(int(time.time()))      
            save_image_to_s3(image_response, bucket_name, generated_object_name)
            return "Amazon image created and saved successfully"


        else:
            model_kwargs = get_inference_parameters(model_id)
            llm = Bedrock(
                credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"),
                region_name=os.environ.get("BWB_REGION_NAME"),
                endpoint_url=os.environ.get("BWB_ENDPOINT_URL"),
                model_id=model_id,
                model_kwargs=model_kwargs
            )
            return llm.predict(prompt)

    try:
        # Main execution
        response = get_text_response(model_id, prompt)
        print(response)
    except ClientError as e:
        response = (f"An error occurred processing the text response:  {str(e)}")
        # Prepare a response indicating a request error



    #----------Below code is for the action group response----------#

    response_code = 200
    action_group = event['actionGroup']
    api_path = event['apiPath']

    if api_path == '/callModel':
        result = get_text_response(model_id, prompt)
    else:
        response_code = 404
        result = f"Unrecognized api path: {action_group}::{api_path}"

    response_body = {
        'application/json': {
            'body': result
        }
     }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': response_code,
        'responseBody': response_body
    }

    api_response = {'messageVersion': '1.0', 'response': action_response}
    return api_response
