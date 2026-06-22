#!/usr/bin/env python3
"""
Analyze accumulated traffic history from traffic-history/ directory.
Useful for trend analysis and reporting.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

def load_traffic_history(history_dir: str = "traffic-history") -> list:
    """Load all traffic snapshots from history directory."""
    history_path = Path(history_dir)
    if not history_path.exists():
        raise FileNotFoundError(f"Directory {history_dir} not found")
    
    snapshots = []
    for file in sorted(history_path.glob("*.json")):
        try:
            with open(file) as f:
                data = json.load(f)
                # Parse the date from filename (YYYY-MM-DD.json)
                date = file.stem
                data["date"] = date
                snapshots.append(data)
        except Exception as e:
            print(f"Warning: Failed to load {file}: {e}")
    
    return snapshots

def analyze_views(snapshots: list) -> dict:
    """Analyze views trend."""
    view_counts = []
    view_uniques = []
    dates = []
    
    for snap in snapshots:
        views = snap.get("views", {})
        if "views" in views and views["views"]:
            # Sum all daily views in this snapshot (14-day window)
            daily_views = [v["count"] for v in views["views"]]
            daily_uniques = [v["uniques"] for v in views["views"]]
            
            view_counts.append(sum(daily_views))
            view_uniques.append(sum(daily_uniques))
            dates.append(snap.get("date"))
    
    if not view_counts:
        return {}
    
    return {
        "total_views_avg": statistics.mean(view_counts),
        "total_views_max": max(view_counts),
        "total_views_min": min(view_counts),
        "unique_visitors_avg": statistics.mean(view_uniques),
        "unique_visitors_max": max(view_uniques),
        "unique_visitors_min": min(view_uniques),
        "peak_date": dates[view_counts.index(max(view_counts))],
        "low_date": dates[view_counts.index(min(view_counts))],
        "snapshots": len(view_counts),
    }

def analyze_clones(snapshots: list) -> dict:
    """Analyze clones trend."""
    clone_counts = []
    clone_uniques = []
    dates = []
    
    for snap in snapshots:
        clones = snap.get("clones", {})
        if "clones" in clones and clones["clones"]:
            # Sum all daily clones in this snapshot (14-day window)
            daily_clones = [c["count"] for c in clones["clones"]]
            daily_uniques = [c["uniques"] for c in clones["clones"]]
            
            clone_counts.append(sum(daily_clones))
            clone_uniques.append(sum(daily_uniques))
            dates.append(snap.get("date"))
    
    if not clone_counts:
        return {}
    
    return {
        "total_clones_avg": statistics.mean(clone_counts),
        "total_clones_max": max(clone_counts),
        "total_clones_min": min(clone_counts),
        "unique_cloners_avg": statistics.mean(clone_uniques),
        "unique_cloners_max": max(clone_uniques),
        "unique_cloners_min": min(clone_uniques),
        "peak_date": dates[clone_counts.index(max(clone_counts))],
        "low_date": dates[clone_counts.index(min(clone_counts))],
        "snapshots": len(clone_counts),
    }

def print_analysis(views_analysis: dict, clones_analysis: dict):
    """Pretty-print analysis results."""
    print("\n" + "="*60)
    print("SERVICENOWDOCS TRAFFIC ANALYSIS")
    print("="*60)
    
    if views_analysis:
        print("\n📊 VIEWS (14-day rolling windows)")
        print("-" * 60)
        print(f"  Average views per window:      {views_analysis['total_views_avg']:.0f}")
        print(f"  Peak views:                    {views_analysis['total_views_max']} ({views_analysis['peak_date']})")
        print(f"  Low views:                     {views_analysis['total_views_min']} ({views_analysis['low_date']})")
        print(f"  Average unique visitors:       {views_analysis['unique_visitors_avg']:.0f}")
        print(f"  Peak unique visitors:          {views_analysis['unique_visitors_max']}")
        print(f"  Snapshots analyzed:            {views_analysis['snapshots']}")
    
    if clones_analysis:
        print("\n📥 CLONES (14-day rolling windows)")
        print("-" * 60)
        print(f"  Average clones per window:     {clones_analysis['total_clones_avg']:.0f}")
        print(f"  Peak clones:                   {clones_analysis['total_clones_max']} ({clones_analysis['peak_date']})")
        print(f"  Low clones:                    {clones_analysis['total_clones_min']} ({clones_analysis['low_date']})")
        print(f"  Average unique cloners:        {clones_analysis['unique_cloners_avg']:.0f}")
        print(f"  Peak unique cloners:           {clones_analysis['unique_cloners_max']}")
        print(f"  Snapshots analyzed:            {clones_analysis['snapshots']}")
    
    print("\n" + "="*60 + "\n")

def main():
    try:
        snapshots = load_traffic_history()
        
        if not snapshots:
            print("No traffic history found. Run collect_traffic.py first.")
            return
        
        print(f"Loaded {len(snapshots)} snapshots")
        
        views_analysis = analyze_views(snapshots)
        clones_analysis = analyze_clones(snapshots)
        
        print_analysis(views_analysis, clones_analysis)
        
        # Save analysis as JSON
        analysis = {
            "analyzed_at": datetime.utcnow().isoformat(),
            "snapshots_count": len(snapshots),
            "views": views_analysis,
            "clones": clones_analysis,
        }
        
        with open("traffic-analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)
        
        print(f"✓ Full analysis saved to traffic-analysis.json")
    
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
