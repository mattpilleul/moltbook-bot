#!/usr/bin/env python3
"""Test the API-based scraper"""

import json
from datetime import datetime

from src.api_scraper import get_post_details, scrape_moltbook_api
from src.generator import generate_tweet
from src.ranker import select_best_posts


def main():
    print(f"\n{'='*60}")
    print(f"🦞 MOLTBOOK BOT - API SCRAPER TEST")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    print("\n📡 Scraping Moltbook via API...")
    try:
        result = scrape_moltbook_api(
            include_stats=True,
            include_agents=True,
            limit=25,
            sort="top",
            fetch_details=True,
            details_limit=5
        )
        posts = result['posts']
        stats = result.get('stats', {})
        agents = result.get('agents', [])
        print(f"✅ Scraped {len(posts)} posts via API")
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
    
    # Show sample post with all fields
    print("\n📄 Sample post data:")
    sample = posts[0]
    for key, value in sample.items():
        if key == "content":
            print(f"  {key}: {value[:100]}...")
        else:
            print(f"  {key}: {value}")
    
    print("\n🎯 Ranking posts...")
    best_posts = select_best_posts(posts, limit=5)
    
    print("\n🏆 Top 5 posts:")
    for i, post in enumerate(best_posts, 1):
        print(f"\n{i}. Score: {post.get('score', 0)}")
        print(f"   Title: {post['title']}")
        print(f"   Author: {post['author']} (Karma: {post.get('author_karma', 'N/A')})")
        print(f"   Submolt: {post['submolt']}")
        print(f"   Upvotes: {post['upvotes']} | Comments: {post['comments']}")
        print(f"   URL: {post['url']}")
        if 'scoring_details' in post:
            print(f"   📊 Scoring: {post['scoring_details']}")
    
    # Test getting detailed post information
    if best_posts:
        print("\n🔍 Testing detailed post fetch...")
        post_id = best_posts[0]['id']
        detailed_post = get_post_details(post_id)
        if detailed_post:
            print(f"✓ Fetched detailed post: {detailed_post['title'][:50]}...")
            if 'comments_data' in detailed_post:
                print(f"  Comments: {len(detailed_post['comments_data'])}")
        else:
            print("⚠️  Failed to fetch detailed post")
    
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
    
    with open('data/api_test_scrape.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved results to data/api_test_scrape.json")
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
