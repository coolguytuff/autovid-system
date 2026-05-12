#!/usr/bin/env python3

import os
import json
import csv
import random
import datetime
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("output")

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
    "This was hidden from the public.",
    "This discovery terrified researchers.",
    "This place should not exist.",
    "This is one of history's strangest events.",
    "People still debate whether this was real.",
    "This changed everything.",
]

BACKGROUND_COLORS = [
    "0x050505",
    "0x0b0b12",
    "0x101018",
    "0x080d14",
    "0x120909",
    "0x0b1110",
]

def ensure_dirs():
    for folder in [
        "scripts",
        "metadata",
        "trends",
        "premium",
        "videos",
        "captions",
        "logs",
        "packages",
        "temp",
    ]:
        (OUTPUT_DIR / folder).mkdir(parents=True, exist_ok=True)

def generate_hook():
    return random.choice(HOOK_TEMPLATES)

def generate_trend_score(topic):
    base_score = NICHE_TOPICS.get(topic, 70)
    novelty = random.randint(70, 100)
    curiosity = random.randint(75, 100)
    retention = random.randint(70, 100)
    emotional_pull = random.randint(70, 100)

    total = round(
        base_score * 0.35
        + novelty * 0.15
        + curiosity * 0.25
        + retention * 0.15
        + emotional_pull * 0.10
    )

    return {
        "topic": topic,
        "base_score": base_score,
        "novelty_score": novelty,
        "curiosity_score": curiosity,
        "predicted_retention_score": retention,
        "emotional_pull_score": emotional_pull,
        "total_score": total,
    }

def save_trend_rankings():
    rankings = [generate_trend_score(topic) for topic in NICHE_TOPICS]
    rankings.sort(key=lambda x: x["total_score"], reverse=True)

    with open(OUTPUT_DIR / "trends" / "trend_scores.json", "w", encoding="utf-8") as f:
        json.dump(rankings, f, indent=2)

    return rankings

def generate_script(topic, hook):
    return [
        {
            "scene": 1,
            "text": hook,
            "duration": 3,
            "role": "hook",
            "keywords": [topic, "mystery"],
        },
        {
            "scene": 2,
            "text": f"Most people have never heard about {topic}.",
            "duration": 4,
            "role": "setup",
            "keywords": [topic],
        },
        {
            "scene": 3,
            "text": "But once you learn the truth, it becomes impossible to forget.",
            "duration": 4,
            "role": "curiosity",
            "keywords": ["dark", "truth", topic],
        },
        {
            "scene": 4,
            "text": "Researchers still debate what really happened.",
            "duration": 4,
            "role": "authority",
            "keywords": ["research", "history", "mystery"],
        },
        {
            "scene": 5,
            "text": "And the strangest part has never been explained.",
            "duration": 5,
            "role": "payoff",
            "keywords": ["unknown", "creepy", topic],
        },
        {
            "scene": 6,
            "text": "Follow for more strange stories.",
            "duration": 3,
            "role": "cta",
            "keywords": ["follow", "cta"],
        },
    ]

def script_to_text(scenes):
    return "\n".join([f"{s['scene']}. {s['text']}" for s in scenes])

def generate_metadata(topic, trend_score):
    title_options = [
        f"{topic.title()} You Probably Didn't Know",
        f"The Strange Truth About {topic.title()}",
        f"This {topic.title()} Story Sounds Fake",
    ]

    return {
        "title": random.choice(title_options),
        "description": f"A short mystery-style story about {topic}.",
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
        "recommended_length_seconds": 23,
        "style": "dark documentary + fast curiosity pacing",
    }

def write_caption_file(index, scene):
    path = OUTPUT_DIR / "captions" / f"video_{index}_scene_{scene['scene']}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(scene["text"])
    return path

def render_scene(video_index, scene, scene_path):
    caption_file = write_caption_file(video_index, scene)
    color = random.choice(BACKGROUND_COLORS)

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s=1080x1920:d={scene['duration']}",
        "-vf",
        (
            f"drawbox=x=0:y=0:w=1080:h=1920:color=black@0.15:t=fill,"
            f"drawtext=textfile='{caption_file}':"
            "fontcolor=white:"
            "fontsize=64:"
            "borderw=5:"
            "bordercolor=black:"
            "box=1:"
            "boxcolor=black@0.35:"
            "boxborderw=28:"
            "x=(w-text_w)/2:"
            "y=h-620"
        ),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(scene_path),
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_video(index, scenes):
    temp_dir = OUTPUT_DIR / "temp" / f"video_{index}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    scene_files = []

    for scene in scenes:
        scene_path = temp_dir / f"scene_{scene['scene']}.mp4"
        render_scene(index, scene, scene_path)
        scene_files.append(scene_path)

    concat_file = temp_dir / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for scene_file in scene_files:
            f.write(f"file '{scene_file.resolve()}'\n")

    output_path = OUTPUT_DIR / "videos" / f"video_{index}.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(output_path),
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output_path

def save_package(index, metadata):
    package_path = OUTPUT_DIR / "packages" / f"video_{index}_platform_package.json"

    with open(package_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "youtube_shorts": {
                    "title": metadata["title"],
                    "description": metadata["description"],
                    "hashtags": metadata["hashtags"],
                },
                "tiktok": {
                    "caption": metadata["title"] + " " + " ".join(metadata["hashtags"]),
                },
                "instagram_reels": {
                    "caption": metadata["description"] + " " + " ".join(metadata["hashtags"]),
                },
            },
            f,
            indent=2,
        )

def save_content(index, scenes, metadata):
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    script_json_path = OUTPUT_DIR / "scripts" / f"video_{index}_{timestamp}.json"
    script_txt_path = OUTPUT_DIR / "scripts" / f"video_{index}_{timestamp}.txt"
    metadata_path = OUTPUT_DIR / "metadata" / f"video_{index}_{timestamp}.json"

    with open(script_json_path, "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=2)

    with open(script_txt_path, "w", encoding="utf-8") as f:
        f.write(script_to_text(scenes))

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    save_package(index, metadata)

    if metadata["trend_score"]["total_score"] >= 90:
        premium_path = OUTPUT_DIR / "premium" / f"video_{index}_{timestamp}.json"

        with open(premium_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "reason": "High trend score. Consider InVideo or Sora enhancement.",
                    "script_data": scenes,
                    "metadata": metadata,
                },
                f,
                indent=2,
            )

def write_performance_template():
    path = OUTPUT_DIR / "logs" / "performance_tracking_template.csv"

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "video_file",
            "topic",
            "platform",
            "views",
            "likes",
            "comments",
            "shares",
            "saves",
            "avg_watch_time",
            "completion_rate",
            "notes",
        ])

def run():
    ensure_dirs()
    rankings = save_trend_rankings()
    write_performance_template()

    selected_topics = [item["topic"] for item in rankings[:5]]

    for i, topic in enumerate(selected_topics):
        hook = generate_hook()
        trend_score = next(item for item in rankings if item["topic"] == topic)

        scenes = generate_script(topic, hook)
        metadata = generate_metadata(topic, trend_score)

        save_content(i + 1, scenes, metadata)
        render_video(i + 1, scenes)

        print(
            f"[autovid] generated video {i + 1}: "
            f"{topic} | score {trend_score['total_score']}"
        )

if __name__ == "__main__":
    run()
