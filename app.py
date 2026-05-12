#!/usr/bin/env python3

import os
import json
import csv
import random
import datetime
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("output")

SERIES_TYPES = [
    "forbidden places",
    "unsolved mysteries",
    "terrifying discoveries",
    "ancient secrets",
]

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
    {
        "text": "THIS SOUNDS FAKE, BUT IT'S REAL.",
        "strength": 97,
        "emotion": "curiosity",
    },
    {
        "text": "NOBODY EXPECTED THIS TO HAPPEN.",
        "strength": 92,
        "emotion": "shock",
    },
    {
        "text": "THIS MYSTERY STILL HASN'T BEEN SOLVED.",
        "strength": 98,
        "emotion": "mystery",
    },
    {
        "text": "THIS PLACE SHOULD NOT EXIST.",
        "strength": 99,
        "emotion": "fear",
    },
    {
        "text": "THIS WAS HIDDEN FROM THE PUBLIC.",
        "strength": 96,
        "emotion": "curiosity",
    },
]

NARRATIVE_PATTERNS = [
    {
        "type": "forbidden_truth",
        "middle": "What they discovered was never meant to be public.",
        "ending": "And people still debate what really happened.",
    },
    {
        "type": "unsolved_mystery",
        "middle": "Researchers still cannot explain the evidence.",
        "ending": "And the mystery remains unsolved today.",
    },
    {
        "type": "terrifying_discovery",
        "middle": "The discovery shocked everyone involved.",
        "ending": "And nobody fully understands it.",
    },
]

BACKGROUND_COLORS = [
    "0x050505",
    "0x0b0b12",
    "0x101018",
    "0x080d14",
    "0x120909",
    "0x0b1110",
    "0x161616",
    "0x1b0f0f",
]

SOUNDTRACK_STYLES = [
    "dark_ambient",
    "cinematic_tension",
    "mystery_pulse",
    "deep_documentary",
]

TRANSITION_STYLES = [
    "shock_cut",
    "slow_fade",
    "quick_flash",
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
        "analytics",
    ]:
        (OUTPUT_DIR / folder).mkdir(parents=True, exist_ok=True)

def weighted_hook_choice():
    weighted = []

    for hook in HOOK_TEMPLATES:
        weighted.extend([hook] * hook["strength"])

    return random.choice(weighted)

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

    rankings.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )

    with open(
        OUTPUT_DIR / "trends" / "trend_scores.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(rankings, f, indent=2)

    return rankings

def build_series():
    series_name = random.choice(SERIES_TYPES)

    return {
        "series_name": series_name,
        "visual_style": "dark_cinematic",
        "soundtrack_style": random.choice(SOUNDTRACK_STYLES),
    }

def generate_script(topic, hook_data, series_data):
    pattern = random.choice(NARRATIVE_PATTERNS)

    return [
        {
            "scene": 1,
            "text": hook_data["text"],
            "duration": 2,
            "role": "hook",
            "emotion": hook_data["emotion"],
            "visual_energy": "extreme",
            "transition_style": "shock_cut",
            "keywords": [topic, "mystery"],
            "visual_style": "dark_cinematic",
            "emphasis": True,
        },
        {
            "scene": 2,
            "text": f"Most people have never heard about {topic}.",
            "duration": 3,
            "role": "setup",
            "emotion": "curiosity",
            "visual_energy": "medium",
            "transition_style": "quick_flash",
            "keywords": [topic],
            "visual_style": "dark_cinematic",
            "emphasis": False,
        },
        {
            "scene": 3,
            "text": pattern["middle"],
            "duration": 4,
            "role": "middle",
            "emotion": "fear",
            "visual_energy": "high",
            "transition_style": "slow_fade",
            "keywords": ["dark", "truth", topic],
            "visual_style": "dark_cinematic",
            "emphasis": True,
        },
        {
            "scene": 4,
            "text": pattern["ending"],
            "duration": 5,
            "role": "payoff",
            "emotion": "mystery",
            "visual_energy": "high",
            "transition_style": "slow_fade",
            "keywords": ["unknown", "creepy"],
            "visual_style": "dark_cinematic",
            "emphasis": True,
        },
        {
            "scene": 5,
            "text": "FOLLOW FOR MORE STRANGE STORIES.",
            "duration": 2,
            "role": "cta",
            "emotion": "curiosity",
            "visual_energy": "medium",
            "transition_style": "quick_flash",
            "keywords": ["follow"],
            "visual_style": "dark_cinematic",
            "emphasis": False,
        },
    ]

def script_to_text(scenes):
    return "\n".join(
        [f"{scene['scene']}. {scene['text']}" for scene in scenes]
    )

def generate_metadata(topic, trend_score, hook_data, series_data):
    title_options = [
        f"{topic.title()} You Probably Didn't Know",
        f"The Strange Truth About {topic.title()}",
        f"This {topic.title()} Story Sounds Fake",
    ]

    return {
        "title": random.choice(title_options),
        "description": (
            f"A short mystery-style story about {topic}."
        ),
        "hashtags": [
            "#strangefacts",
            "#weirdhistory",
            "#mystery",
            "#shorts",
            "#facts",
            "#viral",
        ],
        "platform_fit": [
            "TikTok",
            "YouTube Shorts",
            "Instagram Reels",
        ],
        "trend_score": trend_score,
        "predicted_hook_strength": hook_data["strength"],
        "predicted_rewatchability": random.randint(75, 98),
        "recommended_length_seconds": 16,
        "style": "dark documentary + fast curiosity pacing",
        "voice_style": "dark_documentary",
        "narration_priority": "high",
        "caption_style": "cinematic_large",
        "soundtrack_style": series_data["soundtrack_style"],
        "series_name": series_data["series_name"],
        "thumbnail_focus": topic,
        "thumbnail_style": "high_curiosity",
    }

def write_caption_file(index, scene):
    path = (
        OUTPUT_DIR
        / "captions"
        / f"video_{index}_scene_{scene['scene']}.txt"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(scene["text"])

    return path

def render_scene(video_index, scene, scene_path):
    caption_file = write_caption_file(
        video_index,
        scene
    )

    color = random.choice(BACKGROUND_COLORS)

    font_size = (
        "90"
        if scene.get("emphasis")
        else "70"
    )

    box_opacity = (
        "0.45"
        if scene.get("emphasis")
        else "0.35"
    )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        (
            f"color=c={color}:"
            f"s=1080x1920:"
            f"d={scene['duration']}"
        ),
        "-vf",
        (
            "scale=1200:2133,"
            "crop=1080:1920:"
            "x='(iw-1080)/2 + sin(t*0.3)*20':"
            "y='(ih-1920)/2 + cos(t*0.2)*20',"

            "drawbox=x=0:y=0:w=1080:h=1920:"
            "color=black@0.25:t=fill,"

            f"drawtext=textfile='{caption_file}':"
            "fontcolor=white:"
            f"fontsize={font_size}:"
            "borderw=6:"
            "bordercolor=black:"
            "box=1:"
            f"boxcolor=black@{box_opacity}:"
            "boxborderw=35:"
            "x=(w-text_w)/2:"
            "y=h-620"
        ),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(scene_path),
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def render_video(index, scenes):
    temp_dir = (
        OUTPUT_DIR
        / "temp"
        / f"video_{index}"
    )

    temp_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    scene_files = []

    for scene in scenes:
        scene_path = (
            temp_dir
            / f"scene_{scene['scene']}.mp4"
        )

        render_scene(
            index,
            scene,
            scene_path
        )

        scene_files.append(scene_path)

    concat_file = temp_dir / "concat.txt"

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:
        for scene_file in scene_files:
            f.write(
                f"file '{scene_file.resolve()}'\n"
            )

    output_path = (
        OUTPUT_DIR
        / "videos"
        / f"video_{index}.mp4"
    )

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

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return output_path

def save_package(index, metadata):
    package_path = (
        OUTPUT_DIR
        / "packages"
        / f"video_{index}_platform_package.json"
    )

    with open(
        package_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            {
                "youtube_shorts": {
                    "title": metadata["title"],
                    "description": metadata["description"],
                    "hashtags": metadata["hashtags"],
                },
                "tiktok": {
                    "caption": (
                        metadata["title"]
                        + " "
                        + " ".join(metadata["hashtags"])
                    ),
                },
                "instagram_reels": {
                    "caption": (
                        metadata["description"]
                        + " "
                        + " ".join(metadata["hashtags"])
                    ),
                },
            },
            f,
            indent=2,
        )

def save_content(index, scenes, metadata):
    timestamp = datetime.datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    script_json_path = (
        OUTPUT_DIR
        / "scripts"
        / f"video_{index}_{timestamp}.json"
    )

    script_txt_path = (
        OUTPUT_DIR
        / "scripts"
        / f"video_{index}_{timestamp}.txt"
    )

    metadata_path = (
        OUTPUT_DIR
        / "metadata"
        / f"video_{index}_{timestamp}.json"
    )

    with open(
        script_json_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(scenes, f, indent=2)

    with open(
        script_txt_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(script_to_text(scenes))

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(metadata, f, indent=2)

    save_package(index, metadata)

    if (
        metadata["trend_score"]["total_score"]
        >= 90
    ):
        premium_path = (
            OUTPUT_DIR
            / "premium"
            / f"video_{index}_{timestamp}.json"
        )

        with open(
            premium_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                {
                    "reason":
                        "High trend score. "
                        "Consider InVideo or "
                        "Sora enhancement.",
                    "script_data": scenes,
                    "metadata": metadata,
                },
                f,
                indent=2,
            )

def write_performance_template():
    path = (
        OUTPUT_DIR
        / "logs"
        / "performance_tracking_template.csv"
    )

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
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

    series_data = build_series()

    selected_topics = [
        item["topic"]
        for item in rankings[:5]
    ]

    for i, topic in enumerate(selected_topics):
        hook_data = weighted_hook_choice()

        trend_score = next(
            item
            for item in rankings
            if item["topic"] == topic
        )

        scenes = generate_script(
            topic,
            hook_data,
            series_data
        )

        metadata = generate_metadata(
            topic,
            trend_score,
            hook_data,
            series_data
        )

        save_content(
            i + 1,
            scenes,
            metadata
        )

        render_video(
            i + 1,
            scenes
        )

        print(
            f"[autovid] generated "
            f"video {i + 1}: "
            f"{topic} | "
            f"score "
            f"{trend_score['total_score']}"
        )

if __name__ == "__main__":
    run()
