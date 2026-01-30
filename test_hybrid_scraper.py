#!/usr/bin/env python3
"""Test the hybrid scraper (API + browser fallback)"""

import json
from datetime import datetime

from src.generator import generate_tweet
from src.hybrid_scraper import scrape_moltbook_hybrid
from src.ranker import select_best_posts


def main():
    print(f"\n{'='*60}")
    print(f"🦞 MOLTBOOK BOT - HYBRID SCRAPER TEST")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    print("\n📡 Scraping Moltbook (API first, browser fallback)...")
    try:
        result = scrape_moltbook_hybrid(
            include_stats=True,
            include_agents=True,
            visit_posts=False,  # Set to True if you want detailed post visits
            limit=15,
            sort="top"
        )
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
    
    print("\n🏆 Top 5 posts:")
    for i, post in enumerate(best_posts, 1):
        print(f"\n{i}. Score: {post.get('score', 0)}")
        print(f"   Title: {post['title']}")
        print(f"   Author: {post['author']}")
        print(f"   Submolt: {post['submolt']}")
        print(f"   Upvotes: {post['upvotes']} | Comments: {post['comments']}")
        print(f"   URL: {post['url']}")
        if 'scoring_details' in post:
            print(f"   📊 Scoring: {post['scoring_details']}")
    
    print("\n🐦 Generating tweet from top post...")
    if best_posts:
        tweet = generate_tweet(best_posts[0])
        print(f"\n{'='*60}")
        print(f"🐦 GENERATED TWEET:")
        print(f"{'='*60}")
        print(f"\n{tweet}")
        print(f"\nLength: {len(tweet)} characters")
    
    # Save results
    output = {
        "scraped_at": datetime.now().isoformat(),
        "posts": posts,
        "stats": stats,
        "agents": agents,
        "ranked_posts": best_posts
    }
    
    with open('data/hybrid_test_scrape.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved results to data/hybrid_test_scrape.json")
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
