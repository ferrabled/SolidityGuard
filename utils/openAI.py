import os
import sys
import openai
import json

base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
json_path = os.path.join(base_path, "utils", "secrets.json")
data = json.load(open(json_path, "r"))

openai.api_key = data["openai_api_key"]

# Define the function that will be called from the main script
def get_vulnerability_recommendation(contract, vulnerability):

    prompt = ("You're an advanced solidity smart contract auditor, here's the code that's being reviewed: " 
        + str(contract) + " After a deep analysis, our programm has found the following vulnerability: "
        + str(vulnerability[0]) + " at the line " + str(vulnerability[2]) 
        + ". Could you explain me why this happens and how to fix it? \n\n\n")


    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\"\"\""]
    )

    text = response['choices'][0]['text']
    return text