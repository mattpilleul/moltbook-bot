#!/usr/bin/env python3
"""Test viral tweet generation with actual scraped data"""

import json
from datetime import datetime

from src.viral_generator import generate_thread_tweets, generate_viral_tweet


def main():
    print(f"\n{'='*60}")
    print(f"🦞 MOLTBOOK BOT - VIRAL TWEET GENERATOR")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    # Load scraped data
    try:
        with open('data/hybrid_test_scrape.json', 'r') as f:
            data = json.load(f)
        posts = data['ranked_posts'][:5]  # Get top 5 posts
    except FileNotFoundError:
        print("❌ No scraped data found. Run test_hybrid_scraper.py first!")
        return
    
    print(f"\n📱 Generating viral tweets for top {len(posts)} posts...\n")
    
    for i, post in enumerate(posts, 1):
        print(f"\n{'='*60}")
        print(f"POST #{i}: {post['title'][:60]}...")
        print(f"Author: {post['author']} | ↑{post['upvotes']} 💬{post['comments']}")
        print(f"{'='*60}")
        
        # Generate single viral tweet
        viral_tweet = generate_viral_tweet(post)
        print(f"\n🐦 VIRAL TWEET ({len(viral_tweet)} chars):")
        print("-" * 60)
        print(viral_tweet)
        
        # Generate thread option
        print(f"\n🧵 THREAD OPTION:")
        print("-" * 60)
        thread_tweets = generate_thread_tweets(post)
        for j, tweet in enumerate(thread_tweets, 1):
            print(f"\nTweet {j}/{len(thread_tweets)} ({len(tweet)} chars):")
            print(tweet)
        
        print("\n" + "="*60)
    
    print(f"\n✅ Viral tweets generated!")
    print(f"\n💡 Tips for going viral:")
    print(f"   • Use threads for complex topics")
    print(f"   • Post when AI community is active (9-11 AM EST)")
    print(f"   • Include relevant hashtags: #AI #ArtificialIntelligence #Future")
    print(f"   • Reply to big AI accounts (OpenAI, Anthropic, etc.)")
    print(f"   • Use questions to drive engagement")


if __name__ == "__main__":
    main()
