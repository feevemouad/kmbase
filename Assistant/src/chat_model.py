import requests
import yaml

class ChatModel:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)["chat_model"]
        
        self.endpoint = config['endpoint']
        self.model = config['model_name']
        self.stream = config['stream']
        
    def generate_response(self, system_prompt, context, user_input, relevant_chunks_with_sources):
        # context = self.get_context()
        relevant_text = "\n".join([f"{chunk['chunk']} (Source: {chunk['source']})" for chunk in relevant_chunks_with_sources])
        # Constructing a more effective prompt
        
        prompt = f"""
System prompt: {system_prompt}

Previous dialogue or context : {context}

Use the provided information to assist the user effectively (if it helps).
 
Relevant information:  
{relevant_text}
              
user: {user_input}

assistant:
        """
        print(prompt)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": self.stream
            }
        response = requests.post(self.endpoint, json=payload)
        response_data = response.json()
        if response_data and 'response' in response_data and response_data['response']:
            bot_response = response_data['response'].strip()
            # self.add_to_history(user_input, bot_response)
            return bot_response
        else:
            return "Error: No response from chat model."