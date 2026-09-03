import json 
import random 
from pathlib import Path   # file ka path acess ke liye

TOPIC_FILE=Path('data/topics.json')

def get_topic(state):
    with open(TOPIC_FILE,'r',encoding='utf-8') as f:
        topics=json.load(f)
    topic=random.choice(topics)

    return {
        "topic":topic,
        "audience":"developers and technology enthusiasts",
        "tone":"educational, interesting and slightly conversational"
    }    