#!/usr/bin/env python3
import sys, os, json, datetime

ACTIONS = ["plan", "render", "package"]

def run(action: str) -> None:
    ts = datetime.datetime.utcnow().isoformat()
    outdir = os.path.join("output", action)
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"{action}_{ts.replace(':','-')}.txt")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(f"{action} generated at {ts}\n")
    print(f"[autovid] {action} done -> {outpath}")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "all":
        for action in ACTIONS:
            run(action)
    elif cmd in ACTIONS:
        run(cmd)
    else:
        print("Usage: python app.py [plan|render|package|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()
