#!/usr/bin/env python3
"""
Collect ServiceNowDocs GitHub traffic analytics daily.
Stores data in traffic-history/ with one file per day.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

def get_traffic_data(token: str, owner: str = "ServiceNow", repo: str = "ServiceNowDocs") -> dict:
    """Fetch traffic data from GitHub API."""
    headers = {"Authorization": f"token {token}"}
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        views_resp = requests.get(f"{base_url}/traffic/views", headers=headers)
        views_resp.raise_for_status()
        views = views_resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching views: {e}")
        views = {}
    
    try:
        clones_resp = requests.get(f"{base_url}/traffic/clones", headers=headers)
        clones_resp.raise_for_status()
        clones = clones_resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching clones: {e}")
        clones = {}
    
    return {"views": views, "clones": clones}

def save_traffic_snapshot(data: dict, history_dir: str = "traffic-history") -> str:
    """Save traffic snapshot with date-based filename."""
    Path(history_dir).mkdir(exist_ok=True)
    
    # Filename: YYYY-MM-DD.json (uses collection date)
    timestamp = datetime.utcnow()
    filename = timestamp.strftime("%Y-%m-%d.json")
    filepath = Path(history_dir) / filename
    
    # Include collection timestamp in the data
    data["collected_at"] = timestamp.isoformat()
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(filepath)

def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    
    print(f"[{datetime.utcnow().isoformat()}] Collecting traffic data...")
    
    data = get_traffic_data(token)
    filepath = save_traffic_snapshot(data)
    
    # Summary output
    views_count = data.get("views", {}).get("count", 0)
    views_unique = data.get("views", {}).get("uniques", 0)
    clones_count = data.get("clones", {}).get("count", 0)
    clones_unique = data.get("clones", {}).get("uniques", 0)
    
    print(f"✓ Saved to {filepath}")
    print(f"  Views: {views_count} total, {views_unique} unique")
    print(f"  Clones: {clones_count} total, {clones_unique} unique")
    
    # Also output JSON for GitHub Actions summary
    print(f"::notice::Traffic collected - Views: {views_count}, Clones: {clones_count}")

if __name__ == "__main__":
    main()
