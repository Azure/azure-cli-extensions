from ._constants import DELIMITER, SYSTEM_PROMPT
from .template_utils import get_template
import openai
import json

def get_completion_from_messages(messages, 
                                 model="gpt-35-turbo", 
                                 temperature=0, max_tokens=800):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
        engine="gpt-35-turbo",
        
    )
    return response.choices[0].message["content"]

def get_sub_prompts(user_prompt):
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
    sub_prompts = get_completion_from_messages(messages)
    sub_prompts = json.loads(sub_prompts)
    return sub_prompts

def fill_in_templates(category, resources_types, subscription_id):
    if len(resources_types) == 1:
      return get_template[category][resources_types[0]](subscription_id)
    elif len(resources_types) == 2:
      pass
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

def process_prompt(prompt, subscription_id):
    sub_prompts = get_sub_prompts(prompt)
    # print(sub_prompts)
    payloads = []
    for sub_prompt in sub_prompts:
        action = sub_prompt["action"]
        resources_types = sub_prompt["resources_types"]
        assistant_template = fill_in_templates(action, resources_types, subscription_id)
        # print(assistant_template)
        payload = get_payload(assistant_template, sub_prompt['sub_prompt'])
        payloads.append(payload)
        # print(payload)
