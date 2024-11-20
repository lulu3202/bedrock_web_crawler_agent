# Amazon Bedrock Agent to Web scrape

## About

A beginner friendly project showcasing Bedrock agent's capability to perform web scraping inspired by [web-scraper build-on-AWS github repo](https://github.com/build-on-aws/bedrock-agents-webscraper?tab=readme-ov-file#step-1-aws-lambda-function-configuration). 

## Table of Contents
#### 1 - Introduction
In this project, we will set up an Amazon Bedrock agent with an action group that will enable the agent to web scrape a specific URL provided by the user. 
This README will guide you through the step-by-step process of setting up the Amazon Bedrock agent manually using the AWS Console.

I was inspired by this tutorial on from build-on-AWS GitHub repo: [https://github.com/build-on-aws/bedrock-agents-webscraper?tab=readme-ov-file#step-1-aws-lambda-function-configuration](https://github.com/build-on-aws/bedrock-agents-webscraper?tab=readme-ov-file#step-1-aws-lambda-function-configuration)
#### 2 -  Prerequisites

Grant Model Access to **Anthropic: Claude 3.5 Sonnet** model.
#### 3 -  Amazon Bedrock Agent Configuration 

- Step 1: AWS Lambda Function Configuration - Create a lambda function in language of your choice for the Bedrock agent's action group called 'bedrock-agent-webscrape'. To set up the webscrape Lambda function:
	    - Copy paste code -  takes the url from the event passed in from the bedrock agent, then uses the **urllib.request** library to call, then scrape the webpage. The **beatifulsoup** library is used to clean up the scraped data. The scraped data is saved to the `/tmp` directory of the Lambda function, then passed into the response back to the agent. Review the code, then **Deploy** the Lambda before moving to the next step.
	    - apply a resource policy to the Lambda to grant Bedrock agent access. To do this, we will switch the top tab from **code** to **configuration** and the side tab to **Permissions**. Then, scroll to the **Resource-based policy statements** section and click the **Add permissions** button.
	    - adjust the configuration on the Lambda so that it has enough time, and CPU to handle the request. Navigate back to the Lambda function screen, go to the Configurations tab, then General configuration and select Edit.

  High-Level Flow Summary of lambda - webcrawler python function :

	-  Entry Point (lambda_handler) : Receives event and context, Routes based on API path, Formats and returns response

	-  Request Processing (handle_search) : Extracts URL from parameters, Validates and formats URL, Manages content retrieval and storage

	- Web Scraping (get_page_content) : Fetches webpage content, Parses HTML, Extracts text content

  	- Storage Management : empty_tmp_folder(): Cleans temporary storage and save_to_tmp(): Saves scraped content

- Step 2: Create & Attach an AWS Lambda Layer
	    - For this step you will need, .zip file of dependencies for the Lambda function that are not natively provided (such as) **urllib.request** and **beautiful soup(not native)** libraries for web scraping. The dependencies are already packaged, and can be download from [here](https://github.com/build-on-aws/bedrock-agents-webscraper/raw/main/lambda-layer/layer-python-requests-googlesearch-beatifulsoup.zip) - referenced from build-on-AWS github repo
	    - Name your lambda layer `googlesearch_requests_layer`. Select **Upload a .zip file** and choose the .zip file of dependencies. Choose **x86_64** for your Compatible architectures, and Python 3.12 for your runtime
	    - Navigate back to Lambda function `bedrock-agent-webscrape`, with **Code** tab selected. Scroll to the Layers section and select **Add a Layer**
	    - You are now done creating and adding the dependencies needed via Lambda layer for your webscrape function.

- Step 3: Setup Bedrock Agent and Action Group

	- Step 3A - To set up Bedrock Agent 
	    - Navigate to the Bedrock console. Go to the toggle on the left, and under **Builder tools** select _**Agents**_, then _**Create Agent**_. Provide an agent name, like `athena-agent` then _**Create**_.
	    - For the model, select **Anthropic Claude 3.5 Sonnet**. Next, provide the following instruction for the agent: You are a research analyst that webscrapes the internet when provided a {question}. You use a webscraper to retrieve the content of individual webpages for review. Some websites will block the webscraper, you should try alternative sources. If you can't determine a relatable response based on the request provided, answer false. Your output should be a JSON document that includes the URL name, a yes/no answer, and a summary of your explanation. If your output is an error, you should also respond with a JSON document that includes the error.
	    - Set up action group: - Next, we will add an action group. Scroll down to `Action groups` then select _**Add**_.

	- Step 3B - To set up Bedrock Action Group     
Call the action group `webscrape`. In the `Action group type` section, select _**Define with API schemas**_. For `Action group invocations`, set to _**Select an existing Lambda function**_. For the Lambda function, select `bedrock-agent-webscrape`.
    
For the `Action group Schema`, we will choose _**Define with in-line OpenAPI schema editor**_. Replace the default schema in the **In-line OpenAPI schema** editor with the schema provided below. You can also retrieve the schema from the repo [here](https://github.com/build-on-aws/bedrock-agents-webscraper/blob/main/schema/webscrape-schema.json). After, select _**Add**_.(This API schema is needed so that the bedrock agent knows the format structure and parameters needed for the action group to interact with the Lambda function.)

**This schema (webscrape-schema.json) is needed for Amazon Bedrock Agents and is used to define how your API should work**

User Query → Bedrock Agent → Schema Check → Lambda Function → Response

1. User: "Scrape content from example.com"
2. Agent (using schema): 
   - Identifies intent
   - Validates URL
   - Calls correct endpoint (/search)
3. Lambda: 
   - Receives validated request
   - Returns response matching schema

Think of it as:
	- JSON WEBSCRAPE Schema = Contract
	- Agent = Contract enforcer
	- Lambda = Contract implementer
				
Click **Create** and **Save and exit**. You are now done setting up the webscrape action group.
			
- Step 4: Create an Alias
	    - At the top, select **Save**, then **Prepare**. After, select **Save and exit**. Then, scroll down to the **Alias** section and select _**Create**_. Choose a name of your liking, then create the alias. Make sure to copy and save your **AliasID**. Also, scroll to the top and save the **Agent ID** located in the **Agent overview** section.
 
#### 4 - Test the bedrock agent set up 
Use  Console to test out webscaping functionality 
 ![image](https://github.com/user-attachments/assets/911507cd-ec5e-4b4c-90d9-4e83b7875975)

#### 5 - Setup and Run Streamlit App on EC2 

1. **Obtain CF template to launch the streamlit app**: Download the Cloudformation template from [here](https://github.com/build-on-aws/bedrock-agents-streamlit/blob/main/ec2-streamlit-template.yaml). This template will be used to deploy an EC2 instance that has the Streamlit code to run the UI.
    
2. **Deploy template via Cloudformation**:
    
    - In your mangement console, search, then go to the AWS CloudFormation service.
    - Create a stack with new resources (standard).

 Next, Provide a stack name like _**ec2-streamlit**_. Keep the instance type on the default of t3.small, then go to Next
 
3. **Edit the app to update agent IDs**:

- Navigate to the EC2 instance management console. Under instances, you should see `EC2-Streamlit-App`. Select the checkbox next to it, then connect to it via `EC2 Instance Connect`.

- Next, use the following command to edit the invoke_agent.py file:
    
    ```shell
    sudo vi app/streamlit_app/invoke_agent.py
    ```
    
- Press _**i**_ to go into edit mode. Then, update the _**AGENT ID**_ and _**Agent ALIAS ID**_ values.
- After updating the IDs, press`Esc`, then save the file changes with the following command:

  ```shell
  :wq!
  ```

    - Now, start the streamlit app by running the following command:
        
        ```shell
        streamlit run app/streamlit_app/app.py
        ```
        
    - You should see an external URL. Copy & paste the URL into a web browser to start the streamlit application.

![image](https://github.com/user-attachments/assets/ddeaf250-2999-4f73-b061-da840e24acd0)

App.py code file will help with:

- A. Streamlit App Setup: Configures the app layout and interactive elements like text input, buttons, and a sidebar.
- B. Image Handling: Processes images (e.g., human and robot icons) into circular shapes for better UI presentation.
- C. Session State Management: Maintains a session history for questions and answers using st.session_state.
- D. Agent Integration: Sends user queries to an external lambda_handler function for processing and handles the response.
- E. Display History: Dynamically generates a conversation-like history display, associating user queries with responses.
- F. Example Prompts: Provides users with pre-defined prompts to test the scraping functionality.

#### 6 - Cleanup

After completing the setup and testing of the Bedrock agent, follow these steps to clean up your AWS environment and avoid unnecessary charges:

1. Delete S3 Buckets:

- Navigate to the S3 console.
- Select the buckets "artifacts-bedrock-agent-webscrape-alias". Make sure that this bucket is empty by deleting the files.
- Choose 'Delete' and confirm by entering the bucket name.

2. Remove the Lambda Functions and Layers:

- Go to the Lambda console.
- Select the "bedrock-agent-internet-search" function.
- Click 'Delete' and confirm the action. Do the same for the webscraper function
- Be sure to navigate to the layers tab in the Lambda console, and delete "googlesearch_requests_layer"

3. Delete Bedrock Agent:

- In the Bedrock console, navigate to 'Agents'.
- Select the created agent, then choose 'Delete'.

 4. Delete the EC2 instance 
### Resources

https://github.com/build-on-aws/bedrock-agents-webscraper?tab=readme-ov-file#step-6-setup-and-run-streamlit-app-on-ec2-optional

#### 7 - Approximate Cost Estimation 

Ranges between 0.25 cents to 1 dollar (provided you delete resources and perform clean up activities after your session)

### License

 [MIT-0 license](https://github.com/lulu3202/bedrock_web_crawler_agent#MIT-0-1-ov-file)

