#!/usr/bin/env python3

import os
import json
import random
import datetime

NICHE_TOPICS = [
    "strange history",
    "lost cities",
    "weird geography",
    "ancient mysteries",
    "dangerous places",
    "survival stories",
    "forgotten wars",
    "strange animals",
]

HOOK_TEMPLATES = [
    "This sounds fake, but it's real.",
    "Nobody talks about this anymore.",
    "This place should not exist.",
    "This happened in real history.",
    "The craziest part is what happened next.",
]

VIDEO_TEMPLATES = [
    {
        "format": "mini documentary",
        "length": "30s"
    },
    {
        "format": "fact list",
        "length": "20s"
    },
]

OUTPUT_DIR = "output"

def ensure_dirs():
    os.makedirs(f"{OUTPUT_DIR}/scripts", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/metadata", exist_ok=True)

def generate_topic():
    return random.choice(NICHE_TOPICS)

def generate_hook():
    return random.choice(HOOK_TEMPLATES)

def generate_script(topic, hook):
    return f'''
HOOK:
{hook}

TOPIC:
{topic.title()}

SCRIPT:
Scientists and historians still talk about this today.
Most people have never even heard about it.
And the strangest part is what happened at the end.

CTA:
Follow for more strange facts.
'''

def generate_metadata(topic):
    return {
        "title": f"{topic.title()} Facts",
        "hashtags": [
            "#history",
            "#facts",
            "#shorts",
            "#tiktokfacts",
            "#viral"
        ],
        "description": f"Strange facts about {topic}."
    }

def save_content(index, script, metadata):
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    script_path = f"{OUTPUT_DIR}/scripts/video_{index}_{timestamp}.txt"
    metadata_path = f"{OUTPUT_DIR}/metadata/video_{index}_{timestamp}.json"

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

def run():
    ensure_dirs()

    for i in range(5):
        topic = generate_topic()
        hook = generate_hook()

        script = generate_script(topic, hook)
        metadata = generate_metadata(topic)

        save_content(i + 1, script, metadata)

        print(f"[autovid] generated video package {i+1}")

if __name__ == "__main__":
    run()
