import requests
import json
from dotenv import load_dotenv
import os
import time

# Load the .env file
dotenv = load_dotenv()

def make_prompt(user_message, objects, player):
    # Create a prompt
    prompt = f"""
    You are a cooking assisstant in charge of picking and dropping ingredients at various places in a 15x15 map.
    Those are some tips for the game:
    1/ The map is composed of cells on an orthogonal grid. Each cell can be occupied only by one agent, target or obstacle.
    2/ The bottom left corner of the map is the position (0,0). The x-axis is horizontal and the y-axis is vertical.

    Each object will be given through a tuple of 3 elements: (name, x, y). For example, ("apple", 1, 2) means that there is an apple at position (1, 2).
    The Objects are located at the following positions:
    {objects}
    The player is located at the following x and y positions:
    {player}

    You have access to three ACTIONS: "PICK", "DROP", "MOVE x,y".
    1/ "PICK": Pick up an object at the current position and stacks it on the player's inventory.
    2/ "DROP": Drop the last object in the stack created by the PICK action at the current position and removes it from the inventory.
    3/ "MOVE x,y": Move the player to a new position on the map. The new position is defined by the x and y coordinates.
    4/ It is IMPOSSIBLE to place multiple objects at the same place. You can't drop an object where one is already placed.
    
    Here is the user's message:
    {user_message}

    
    You should only respond in the format as described below:
    RESPONSE FORMAT:
    THOUGHTS: Based on the information I listed above, in 50 words, do reasoning about what the next task should be.
    COMMAND: The next COMMAND. A COMMAND can be composed of one or multiple actions, which are defined above. You can do as many actions as you want in a COMMAND, in any order. Split every action by a single ";" and no space.
    """
    return prompt

# Function to extract the thoughts and command from the text
def extract_thoughts_and_command(text):
    # Initialiser les variables pour stocker les thoughts et la commande
    thoughts = None
    action = None

    # Extraire les thoughts
    if "THOUGHTS:" in text:
        start_thoughts = text.index("THOUGHTS:") + len("THOUGHTS:")
        end_thoughts = text.index("COMMAND:")
        thoughts = text[start_thoughts:end_thoughts].strip()

    # Extraire la commande
    if "COMMAND:" in text:
        command_part = text.split("COMMAND:")[1].strip()
        action = command_part

    return thoughts, action

# Function to make a request to the API
def make_request(prompt):

    def send_request():
        # Make a request to the API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY')}",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat", # Optional
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        return response.json()

    
    # Send request 
    response = send_request()
    # print(response)

    # Check if the rate limit was reached
    while('error' in response and response['error']['code'] == 429): 
        # Wait for 30 seconds and try again
        print('Rate limit reached, waiting for 30 seconds')
        time.sleep(30)
        response = send_request()

    # Check if the request was successful
    if 'error' in response:
        raise Exception(f"Failed to make the request: {response}")

    # Get the answer from the response
    answer = response['choices'][0]['message']['content']
    return answer