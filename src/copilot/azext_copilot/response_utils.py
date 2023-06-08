from ._constants import DELIMITER, SYSTEM_PROMPT
from .template_utils import get_template
import openai
import json

def get_completion_from_messages(messages, 
                                 model="gpt-35-turbo", 
                                 temperature=0, max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
        engine="gpt-35-turbo",
        
    )
    return response.choices[0].message["content"]

def get_category_and_resource_type(user_prompt):
    messages =  [  
        {
            'role':'system', 
            'content': SYSTEM_PROMPT
        },    
        {
            'role':'user', 
            'content': f"{DELIMITER}{user_prompt}{DELIMITER}"
        },  
    ] 
    category_and_resource_response = get_completion_from_messages(messages)
    category_and_resource_response = json.loads(category_and_resource_response)[0]
    return category_and_resource_response

def fill_in_templates(category_and_resource_type):
    category = category_and_resource_type['category']
    resources_types = category_and_resource_type['resources_types']
    if len(resources_types) == 1:
      return get_template[category][resources_types[0]]()
    elif len(resources_types) == 2:
      return get_template[category](resources_types[0], resources_types[1])
    else:
       print("too many resources types")
       return None

def get_payload(assistant_template, user_prompt):
    messages =  [  
        {
            'role':'system', 
            'content': assistant_template
        },    
        {
            'role':'user', 
            'content': f"{DELIMITER}{user_prompt}{DELIMITER}"
        },  
    ] 
    payload = get_completion_from_messages(messages)
    return payload

def process_prompt(prompt):
    category_and_resource_type = get_category_and_resource_type(prompt)
    assistant_template = fill_in_templates(category_and_resource_type)
    payload = get_payload(assistant_template, prompt)
    return payload