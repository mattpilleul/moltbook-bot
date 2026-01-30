#!/usr/bin/env python3
"""Generate tweet summaries for manual posting"""

import json
import os
# Add src to path for imports
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.claude_generator import generate_viral_tweet_with_image
from src.hybrid_scraper import scrape_moltbook
from src.ranker import select_best_posts


def generate_summary():
    """Generate a summary with tweet and image for manual posting"""
    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y-%m-%d_%H-%M")
    
    # Create directories
    summaries_dir = Path("summaries")
    summaries_dir.mkdir(exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"📱 MOLTBOOK BOT - SUMMARY GENERATOR")
    print(f"{'='*60}")
    print(f"Timestamp: {timestamp}")
    
    # Step 1: Scrape posts
    print(f"\n📡 Scraping Moltbook posts...")
    scrape_result = scrape_moltbook(visit_posts=True)
    posts = scrape_result['posts']
    
    if not posts:
        print("❌ No posts found!")
        return
    
    print(f"✅ Found {len(posts)} posts")
    
    # Step 2: Rank posts
    print(f"\n📊 Ranking posts by engagement potential...")
    ranked_posts = select_best_posts(posts, limit=1)
    
    # Step 3: Generate tweet for top post
    top_post = ranked_posts[0]
    print(f"\n🎯 Selected top post: {top_post['title'][:60]}...")
    
    # Generate tweet and image
    tweet, image_path = generate_viral_tweet_with_image(top_post)
    
    if not tweet:
        print("❌ Failed to generate tweet!")
        return
    
    # Step 4: Save summary
    summary_file = summaries_dir / f"{date_str}.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# Moltbook Bot Summary\n\n")
        f.write(f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Post Details\n\n")
        f.write(f"- **Title:** {top_post['title']}\n")
        f.write(f"- **Author:** {top_post['author']}\n")
        f.write(f"- **Upvotes:** {top_post['upvotes']}\n")
        f.write(f"- **Comments:** {top_post['comments']}\n")
        f.write(f"- **URL:** {top_post['url']}\n\n")
        f.write(f"## Generated Tweet\n\n")
        f.write(f"```\n{tweet}\n```\n\n")
        f.write(f"## Image\n\n")
        f.write(f"- **Path:** {image_path}\n")
        f.write(f"- **Size:** {os.path.getsize(image_path) / 1024:.1f} KB\n\n")
        f.write(f"## Posting Instructions\n\n")
        f.write(f"1. Copy the tweet text above\n")
        f.write(f"2. Upload the image: `{image_path}`\n")
        f.write(f"3. Post on X/Twitter\n")
    
    # Step 5: Save tweet separately for easy access
    tweet_file = summaries_dir / f"{date_str}_tweet.txt"
    with open(tweet_file, 'w', encoding='utf-8') as f:
        f.write(tweet)
    
    print(f"\n✅ Summary generated!")
    print(f"   📄 Summary: {summary_file}")
    print(f"   🐦 Tweet: {tweet_file}")
    print(f"   📸 Image: {image_path}")
    
    # Also save latest summary
    latest_summary = summaries_dir / "latest.md"
    latest_tweet = summaries_dir / "latest_tweet.txt"
    
    with open(summary_file, 'r', encoding='utf-8') as src, \
         open(latest_summary, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    
    with open(tweet_file, 'r', encoding='utf-8') as src, \
         open(latest_tweet, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    
    print(f"\n📁 Also saved as 'latest' for quick access")
    
    # Save stats
    stats = {
        "timestamp": timestamp.isoformat(),
        "posts_scraped": len(posts),
        "top_post": {
            "title": top_post['title'],
            "upvotes": top_post['upvotes'],
            "comments": top_post['comments']
        },
        "tweet_generated": bool(tweet),
        "image_generated": bool(image_path)
    }
    
    stats_file = summaries_dir / f"{date_str}_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    return {
        "summary": str(summary_file),
        "tweet": str(tweet_file),
        "image": image_path,
        "stats": str(stats_file)
    }


if __name__ == "__main__":
    result = generate_summary()
    if result:
        print(f"\n🚀 Ready to post! Check the summaries directory.")
