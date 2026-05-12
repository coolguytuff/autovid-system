#!/usr/bin/env python3

import os
import json
import random
import datetime

OUTPUT_DIR = "output"

NICHE_TOPICS = {
    "creepy discoveries": 97,
    "unsolved mysteries": 96,
    "forbidden places": 95,
    "bizarre true stories": 94,
    "science mysteries": 93,
    "survival stories": 91,
    "strange history": 88,
    "ancient civilizations": 86,
    "dangerous places": 84,
    "weird geography": 82,
}

HOOK_TEMPLATES = [
    "This sounds fake, but it's real.",
    "Nobody expected this to happen.",
    "This mystery still hasn't been solved.",
    "The scariest part is what they found next.",
    "This was completely hidden from the public.",
    "This discovery terrified scientists.",
    "This place should not exist.",
    "This is one of history's strangest events.",
    "People still debate whether this was real.",
    "This changed everything.",
]

RETENTION_LINES = [
    "But here’s where it gets strange.",
    "And that is not even the weirdest part.",
    "Then something happened that nobody expected.",
    "The ending is what makes this so disturbing.",
    "This is why people still talk about it today.",
]

def ensure_dirs():
    os.makedirs(f"{OUTPUT_DIR}/scripts", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/metadata", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/trends", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/premium", exist_ok=True)

def weighted_topic_choice():
    weighted_topics = []
    for topic, score in NICHE_TOPICS.items():
        weighted_topics.extend([topic] * score)
    return random.choice(weighted_topics)

def generate_hook():
    return random.choice(HOOK_TEMPLATES)

def generate_trend_score(topic):
    base_score = NICHE_TOPICS.get(topic, 70)
    novelty = random.randint(70, 100)
    curiosity = random.randint(75, 100)
    retention = random.randint(70, 100)

    total = round(
        base_score * 0.45
        + novelty * 0.20
        + curiosity * 0.25
        + retention * 0.10
    )

    return {
        "topic": topic,
        "base_score": base_score,
        "novelty_score": novelty,
        "curiosity_score": curiosity,
        "predicted_retention_score": retention,
        "total_score": total,
    }

def save_trend_rankings():
    rankings = []

    for topic in NICHE_TOPICS:
        rankings.append(generate_trend_score(topic))

    rankings.sort(key=lambda x: x["total_score"], reverse=True)

    with open(f"{OUTPUT_DIR}/trends/trend_scores.json", "w", encoding="utf-8") as f:
        json.dump(rankings, f, indent=2)

    return rankings

def generate_script(topic, hook):
    retention_line = random.choice(RETENTION_LINES)

    return f"""HOOK:
{hook}

TOPIC:
{topic.title()}

SCRIPT:
Most people have never heard about {topic}.
But once you do, it becomes impossible to forget.

{retention_line}

Researchers still debate what really happened.
Some details are strange enough to sound made up.
But the evidence makes the story even crazier.

And the wildest part?
Nobody can fully explain it even today.

CTA:
Follow for more strange stories.
"""

def generate_metadata(topic, trend_score):
    return {
        "title": f"{topic.title()} You Probably Didn't Know",
        "description": f"A strange short story about {topic}.",
        "hashtags": [
            "#strangefacts",
            "#weirdhistory",
            "#mystery",
            "#shorts",
            "#facts",
            "#viral",
        ],
        "platform_fit": ["TikTok", "YouTube Shorts", "Instagram Reels"],
        "trend_score": trend_score,
        "recommended_length_seconds": random.choice([24, 28, 32, 35]),
    }

def save_content(index, script, metadata):
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    script_path = f"{OUTPUT_DIR}/scripts/video_{index}_{timestamp}.txt"
    metadata_path = f"{OUTPUT_DIR}/metadata/video_{index}_{timestamp}.json"

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    if metadata["trend_score"]["total_score"] >= 90:
        premium_path = f"{OUTPUT_DIR}/premium/video_{index}_{timestamp}.json"
        with open(premium_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "reason": "High trend score, consider InVideo or Sora upgrade.",
                    "script_file": script_path,
                    "metadata": metadata,
                },
                f,
                indent=2,
            )

def run():
    ensure_dirs()
    rankings = save_trend_rankings()

    selected_topics = [item["topic"] for item in rankings[:5]]

    for i, topic in enumerate(selected_topics):
        hook = generate_hook()
        trend_score = next(item for item in rankings if item["topic"] == topic)
        script = generate_script(topic, hook)
        metadata = generate_metadata(topic, trend_score)

        save_content(i + 1, script, metadata)

        print(
            f"[autovid] generated video package {i + 1}: "
            f"{topic} | score {trend_score['total_score']}"
        )

if __name__ == "__main__":
    run()
