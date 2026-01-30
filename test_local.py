#!/usr/bin/env python3
"""
Test script to run the Moltbook bot locally without posting to Twitter.
This will scrape posts, rank them, and show what would be posted.
"""

import json
import os
from datetime import datetime

from src.generator import generate_tweet
from src.ranker import explain_score, select_best_posts
from src.scraper import scrape_moltbook


def main():
    print(f"\n{'='*60}")
    print(f"🦞 MOLTBOOK BOT - LOCAL TEST (NO POSTING)")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    print("\n📡 Scraping Moltbook...")
    try:
        result = scrape_moltbook(include_stats=True, include_agents=True, visit_posts=True)
        posts = result['posts']
        stats = result.get('stats', {})
        agents = result.get('agents', [])
        print(f"✅ Scraped {len(posts)} posts")
        if stats:
            print(f"📊 Site stats: {stats}")
        if agents:
            print(f"🤖 Recent agents: {len(agents)}")
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return
    
    if not posts:
        print("⚠️  No posts found!")
        return
    
    print("\n🎯 Ranking posts...")
    best_posts = select_best_posts(posts, limit=5)
    
    print(f"\n🏆 Top 5 posts:")
    for i, post in enumerate(best_posts, 1):
        print(f"\n{i}. Score: {post['score']}")
        print(f"   Title: {post['title']}")
        print(f"   Author: u/{post['author']}")
        print(f"   Submolt: {post['submolt']}")
        print(f"   Upvotes: {post['upvotes']} | Comments: {post['comments']}")
        print(f"   URL: {post['url']}")
        
        # Show score breakdown for top 3
        if i <= 3:
            explain_score(post)
    
    # Show what would be posted
    if best_posts:
        print(f"\n{'='*60}")
        print(f"🐦 TWEET THAT WOULD BE POSTED:")
        print(f"{'='*60}")
        
        top_post = best_posts[0]
        tweet = generate_tweet(top_post)
        print(f"\n{tweet}\n")
        print(f"Length: {len(tweet)} characters")
        print(f"{'='*60}")
    
    # Save to data file for inspection
    os.makedirs('data', exist_ok=True)
    with open('data/test_scrape.json', 'w') as f:
        json.dump(posts, f, indent=2)
    print(f"\n💾 Saved all posts to data/test_scrape.json")

if __name__ == '__main__':
    main()
