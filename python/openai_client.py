import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
conversation_history = []
history_length = 3

def get_openai_response(prompt):
    global conversation_history

    conversation_history.append(f"Usuário: {prompt}")

    if len(conversation_history) > history_length:
        conversation_history = conversation_history[-history_length:]
        
    full_prompt = "\n".join(conversation_history) + "\nIA:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um espelho mágico, seu nome é Mastigador."},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=50,
        temperature=0.7
    )

    response_text = response.choices[0].message['content'].strip()
    conversation_history.append(f"IA: {response_text}")
    return response_text
