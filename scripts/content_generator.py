import os
import time
import logging
from pathlib import Path
from datetime import datetime

# Root path setup
script_dir = Path(__file__).resolve().parent.parent
vault_path = script_dir / "AI_Employee" / "vault"

def get_context():
    """
    Reads context from Business_Goals.md and Done tasks.
    """
    goals = (vault_path / "Business_Goals.md").read_text(encoding='utf-8')
    done_tasks = list((vault_path / "Done").glob("*.md"))
    recent_tasks = "\n".join([t.name for t in done_tasks[-5:]])
    
    # Simulating revenue context
    revenue_context = "Revenue is up 15% this month due to Silver Tier launch."
    
    return {
        "goals": goals,
        "tasks": recent_tasks,
        "revenue": revenue_context
    }

def generate_social_post(platform: str, context: dict):
    """
    Simulates AI content generation for a specific platform.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if platform == "twitter":
        content = f"🚀 Big news! {context['revenue'].split('.')[0]}. Our recent work on {context['tasks'].split('.')[0]} is paying off. Ready to automate? #AI #Efficiency"
        hashtags = "#Automation #FutureOfWork"
    elif platform == "facebook":
        content = f"We are excited to share our progress this week. {context['revenue']} We've been busy with: {context['tasks']}. Our goal remains: {context['goals'].split('##')[1][:100]}..."
        hashtags = "#BusinessGrowth #AIEmployee"
    else: # Instagram
        content = f"Visualizing a more efficient future. ✨ {context['revenue']} #AutonomousFTE"
        hashtags = "#TechInnovation #InstagramBusiness"

    post_template = f"""---
type: social_post
platform: {platform}
status: pending
created_at: {timestamp}
---

# Content
{content}

# Hashtags
{hashtags}

# Suggested Image
A high-tech dashboard showing business growth metrics and AI interactions.
"""
    return post_template

def main():
    ctx = get_context()
    platforms = ["twitter", "facebook", "instagram"]
    pending_dir = vault_path / "Pending_Approval"
    pending_dir.mkdir(parents=True, exist_ok=True)

    for plat in platforms:
        post = generate_social_post(plat, ctx)
        filename = f"SOCIAL_POST_{plat.upper()}_{int(time.time())}.md"
        (pending_dir / filename).write_text(post, encoding='utf-8')
        print(f"Generated {plat} post draft: {filename}")

if __name__ == "__main__":
    main()
