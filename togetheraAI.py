import requests
from test import get_prompt

def generate_output(user_query):
    # API endpoint
    endpoint = 'https://api.together.xyz/inference'

    # API parameters
    payload = {
        "model": "togethercomputer/llama-2-13b-chat",
        "max_tokens": 512,
        "prompt": user_query,
        "request_type": "language-model-inference",
        "temperature": 0.12,
        "top_p": 0.9,
        "top_k": 30,
        "repetition_penalty": 1,
        "stop": ["[/INST]", "</s>"],
        "negative_prompt": "Avoid asking questions. Provide direct answers to user queries.",
        "sessionKey": "1b0eae1873c43ee4a4bb16a4348338d200c218b8",
        "type": "chat"
    }

    headers = {
        "Authorization": "Bearer 1cecf43792b1187b044ab0293853353cc45caf8fdfe0a82e049d53cbf5954d26",
    }

    # Make the POST request
    response = requests.post(endpoint, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the final output text
        output_text = response.json().get('output', {}).get('choices', [{}])[0].get('text', '')
        return output_text
    else:
        return f"Error: {response.status_code}, {response.text}"

combined_text = get_prompt()

model_output = generate_output(combined_text)

# Print the entire conversation history
print(model_output)

