import os
import time
import shutil
import logging
import yaml
import re
from pathlib import Path

# Root path setup
script_dir = Path(__file__).resolve().parent.parent
vault_path = script_dir / "AI_Employee" / "vault"
approved_dir = vault_path / "Approved"
done_dir = vault_path / "Done"

logger = logging.getLogger(__name__)

def parse_post(file_path: Path):
    """
    Parses metadata and content from an approved social post.
    """
    content = file_path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        metadata = yaml.safe_load(match.group(1))
        body = match.group(2).strip()
        return metadata, body
    return None, content

def execute_social_action(metadata: dict, body: str):
    """
    Simulates calling the MCP server for a specific social action.
    """
    platform = metadata.get("platform", "unknown")
    logger.info(f"Publishing approved post to {platform.capitalize()}...")
    
    # Simulate MCP Call
    time.sleep(1)
    return True

def monitor_approvals():
    """
    Watch /Approved for social_post types.
    """
    approved_files = list(approved_dir.glob("*.md"))
    if not approved_files:
        return

    for post_file in approved_files:
        try:
            metadata, body = parse_post(post_file)
            if not metadata or metadata.get("type") != "social_post":
                continue

            logger.info(f"Processing approved social post: {post_file.name}")
            
            # Execute
            if execute_social_action(metadata, body):
                # Move to Done
                shutil.move(str(post_file), str(done_dir / post_file.name))
                logger.info(f"Post {post_file.name} published and moved to Done.")
            
        except Exception as e:
            logger.error(f"Failed to publish {post_file.name}: {e}")

def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Social Post Scheduler started...")
    while True:
        monitor_approvals()
        time.sleep(30) # Poll every 30 seconds

if __name__ == "__main__":
    main()
