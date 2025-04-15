import base64
import json
import requests
import os
from prompts_to_json import regex_search,convert_keys_to_camel_case,rename_degree_key
from dotenv import load_dotenv
from openai import OpenAI
import time

load_dotenv()
api_key = os.getenv("api_key")

def process(image_path, prompt,additional_data=None):
    with open(image_path, "rb") as image:
        base64_image = base64.b64encode(image.read()).decode("utf-8")

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role" : "system",
            "content" : prompt
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": f"""ocr_extracted_text = "{additional_data} "  """
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    var = response.json()['choices'][0]['message']['content']
    # print(var)
    # board_name,line_of_business,license_number,issue_date, issued_to = regex_search_pli(var)
    # print("***************")
    # print(board_name,line_of_business,license_number,issue_date, issued_to)
    # return board_name,line_of_business,license_number,issue_date, issued_to
    try:
        result =  regex_search(var)
    except:
        result = var
    converted_data = convert_keys_to_camel_case(result)
    if len(converted_data["documentInfo"][0].keys())>1:
        print(len(converted_data["documentInfo"][0].keys()))
        converted_data["documentInfo"][0]["validationType"]='yes'
    else:
        converted_data
    return converted_data


def process_other(image_path,user_input):
    with open(image_path, "rb") as image:
        base64_image = base64.b64encode(image.read()).decode("utf-8")

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role" : "system",
            "content" : f"""You are document extractor. A user sends you an image of a document and you tell them the required information.
            is this {user_input} ? 
            if yes use the
            following JSON format: {{
            "document_info":[
            {{
            "key":"value"
            }}
            ],
            }}
           else "document_info":[
                {{
                    'validation_type':"no"
                }}
                ]
                **When extracting the dates, ensure it is in the yyyy-mm-dd format.**
                """
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "find first_name, last_name, expiration_date, issue_date, business_name, validation_type"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    var = response.json()['choices'][0]['message']['content']
    # print(var)
    # board_name,line_of_business,license_number,issue_date, issued_to = regex_search_pli(var)
    # print("***************")
    # print(board_name,line_of_business,license_number,issue_date, issued_to)
    # return board_name,line_of_business,license_number,issue_date, issued_to
    try:
        result =  regex_search(var)
    except:
        result = var
    converted_data = convert_keys_to_camel_case(result)
    if len(converted_data["documentInfo"][0].keys())>1:
        print(len(converted_data["documentInfo"][0].keys()))
        converted_data["documentInfo"][0]["validationType"]='yes'
    else:
        converted_data
    return converted_data

def assistant(image_path,prompt,additional_data=None):
    client = OpenAI(api_key=api_key)
    with open(image_path, 'rb') as f:
        file = client.files.create(
            file=f,
            purpose="assistants"
        )
    
    print(additional_data)

    print(file)    

    thread = client.beta.threads.create()

    vector_store = client.vector_stores.create(
        name="Support FAQ",  # Optional name for the vector store
        file_ids=[file.id],  # Replace with your file IDs
        expires_after={"anchor": "last_active_at", "days": 1},  # Optional expiration policy (set as needed)
        chunking_strategy={"type": "auto"},  # Optional, example chunking strategy
        metadata={"description": "Vector store for support FAQs"}  # Optional metadata
    )
    assistant = client.beta.assistants.create(
        name="PDF Helper",
        instructions=f"""You are my assistant who can answer questions from the given PDF.  Note : Document should be your priority if don't get anything out of that than only use this Tesseract OCR based extracted text -   ocr_extracted_text = "{additional_data} "  """,
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        model="gpt-4o-mini"
    ) 


    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = "user",
        content = prompt
    )

    run = client.beta.threads.runs.create(
        thread_id = thread.id,
        assistant_id= assistant.id
    )

    while True:
    # Retrieve the run status
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
        
        if run_status.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            break
        else:
            ### sleep again
            time.sleep(2)

    answer = messages.data[0].content[0].text.value
    print(answer)
    try:
        result =  regex_search(answer)
    except:
        result = answer
    print(result)
    converted_data = convert_keys_to_camel_case(result)
    print(converted_data)
    if len(converted_data["documentInfo"][0].keys())>1:
        print(len(converted_data["documentInfo"][0].keys()))
        converted_data["documentInfo"][0]["validationType"]='yes'
    else:
        converted_data
    
    print(file.id)
    print(vector_store.id)

    client.vector_stores.delete(vector_store.id)  # Deletes the vector store
    client.files.delete(file.id)
    print(file.id)
    print(vector_store.id)
    
    return converted_data

def assistant_other(image_path,user_input):
    client = OpenAI(api_key=api_key)
    with open(image_path, 'rb') as f:
        file = client.files.create(
            file=f,
            purpose="assistants"
        )
    

    print(file)    

    thread = client.beta.threads.create()

    vector_store = client.vector_stores.create(
        name="Support FAQ",  # Optional name for the vector store
        file_ids=[file.id],  # Replace with your file IDs
        expires_after={"anchor": "last_active_at", "days": 1},  # Optional expiration policy (set as needed)
        chunking_strategy={"type": "auto"},  # Optional, example chunking strategy
        metadata={"description": "Vector store for support FAQs"}  # Optional metadata
    )
    assistant = client.beta.assistants.create(
        name="PDF Helper",
        instructions="You are my assistant who can answer questions from the given PDF",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        model="gpt-4o-mini"
    ) 


    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = "user",
        content = f"""You are document extractor. A user sends you a document and you tell them the required information.
            is this a {user_input} certificate/Document ?  
            if yes extract follwoing Information
            find first_name, last_name, expiration_date, issue_date, business_name, validation_type
            And use following JSON format: {{
            "document_info":[
            {{
            "key":"value"
            }}
            ],
            }}
            else "document_info":[
                {{
                    'validation_type':"no"
                }}
                ]
                
                **When extracting the dates, ensure it is in the yyyy-mm-dd format.**
                """
    )

    run = client.beta.threads.runs.create(
        thread_id = thread.id,
        assistant_id= assistant.id
    )

    while True:
    # Retrieve the run status
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
        
        if run_status.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            break
        else:
            ### sleep again
            time.sleep(2)

    answer = messages.data[0].content[0].text.value
    print(answer)
    try:
        result =  regex_search(answer)
    except:
        result = answer
    print(result)
    converted_data = convert_keys_to_camel_case(result)
    print(converted_data)
    if len(converted_data["documentInfo"][0].keys())>1:
        print(len(converted_data["documentInfo"][0].keys()))
        converted_data["documentInfo"][0]["validationType"]='yes'
    else:
        converted_data
    
    return converted_data



    


