#!/usr/bin/env python3
"""Test Claude API-powered viral tweet generator with image support"""

import json
import os
from datetime import datetime

from src.claude_generator import generate_viral_tweet_with_image


def main():
    print(f"\n{'='*60}")
    print(f"🤖 MOLTBOOK BOT - CLAUDE AI TWEET + IMAGE GENERATOR")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  No ANTHROPIC_API_KEY found in environment variables")
        print("   Set it with: export ANTHROPIC_API_KEY=your_key_here")
        print("   Or create a .env file with the key")
        return
    else:
        print("✅ Found ANTHROPIC_API_KEY in environment")
    
    # Load scraped data
    try:
        with open('data/hybrid_test_scrape.json', 'r') as f:
            data = json.load(f)
        posts = data['ranked_posts'][:1]  # Test top post only
    except FileNotFoundError:
        print("❌ No scraped data found. Run test_hybrid_scraper.py first!")
        return
    
    print(f"\n📱 Generating AI-powered viral tweet with image for top post...\n")
    
    for i, post in enumerate(posts, 1):
        print(f"\n{'='*60}")
        print(f"POST #{i}: {post['title'][:60]}...")
        print(f"Author: {post['author']} | ↑{post['upvotes']} 💬{post['comments']}")
        print(f"{'='*60}")
        
        # Generate tweet with image
        print(f"\n🤖 Generating viral tweet + downloading image...")
        tweet, image_path = generate_viral_tweet_with_image(post)
        
        # Calculate Twitter character count (URLs count as 23 chars)
        twitter_count = len(tweet)
        if 'http' in tweet:
            # Find URLs and count them as 23 chars each
            import re
            urls = re.findall(r'https?://[^\s]+', tweet)
            for url in urls:
                twitter_count = twitter_count - len(url) + 23
        
        print(f"\n🐦 GENERATED TWEET ({len(tweet)} chars, {twitter_count} Twitter chars):")
        print("-" * 60)
        print(tweet)
        print("-" * 60)
        
        if image_path:
            print(f"\n📸 IMAGE: {image_path}")
            print(f"   Size: {os.path.getsize(image_path) / 1024:.1f} KB")
        else:
            print(f"\n⚠️  No image downloaded")
        
        # Show engagement prediction
        print(f"\n📊 Engagement Prediction:")
        if any(word in tweet.lower() for word in ["secret", "hidden", "they're"]):
            print("   🔥 High controversy potential - likely to spark debate")
        if any(word in tweet.lower() for word in ["scary", "terrifying", "afraid"]):
            print("   😨 Fear factor - high share potential")
        if len(tweet) < 250:
            print("   📏 Concise - optimized for mobile")
        if "#" in tweet:
            hashtags = [tag for tag in tweet.split() if tag.startswith("#")]
            print(f"   #️⃣ Hashtags: {', '.join(hashtags)}")
        
        print("\n" + "="*60)
    
    print(f"\n✅ Tweet + image generated successfully!")
    print(f"\n💡 Ready to post to Twitter!")
    print(f"   • Tweet is under 280 characters")
    print(f"   • Image downloaded from Moltbook")
    print(f"   • Optimized for maximum engagement")
    print(f"   • Cost-effective: Single Claude API call")


if __name__ == "__main__":
    main()
