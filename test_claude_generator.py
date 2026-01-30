#!/usr/bin/env python3
"""Test Claude API-powered viral tweet generator"""

import json
import os
from datetime import datetime

from src.claude_generator import (generate_all_variations,
                                  generate_viral_tweet_with_claude,
                                  get_claude_generator)


def main():
    print(f"\n{'='*60}")
    print(f"🤖 MOLTBOOK BOT - CLAUDE AI TWEET GENERATOR")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  No ANTHROPIC_API_KEY found in environment variables")
        print("   Set it with: export ANTHROPIC_API_KEY=your_key_here")
        print("   Or create a .env file with the key")
        print("   Note: The key you shared earlier should be rotated for security!\n")
    else:
        print("✅ Found ANTHROPIC_API_KEY in environment")
    
    # Load scraped data
    try:
        with open('data/hybrid_test_scrape.json', 'r') as f:
            data = json.load(f)
        posts = data['ranked_posts'][:3]  # Test top 3 posts
    except FileNotFoundError:
        print("❌ No scraped data found. Run test_hybrid_scraper.py first!")
        return
    
    print(f"\n📱 Generating AI-powered viral tweets for top {len(posts)} posts...\n")
    
    for i, post in enumerate(posts, 1):
        print(f"\n{'='*60}")
        print(f"POST #{i}: {post['title'][:60]}...")
        print(f"Author: {post['author']} | ↑{post['upvotes']} 💬{post['comments']}")
        print(f"{'='*60}")
        
        # Generate multiple variations
        print(f"\n🤖 Generating {3} AI variations...")
        variations = generate_all_variations(post, num_variations=3)
        
        if not variations:
            print("❌ Failed to generate variations")
            continue
        
        # Show all variations with scores
        for j, variation in enumerate(variations, 1):
            print(f"\n📊 Variation {j} (Score: {variation.get('score', 0)}/100)")
            print(f"   Angle: {variation.get('angle', 'unknown')}")
            print(f"   Tweet ({len(variation.get('tweet', ''))} chars):")
            print(f"   {variation.get('tweet', '')}")
            
            if 'analysis' in variation:
                analysis = variation['analysis']
                if analysis.get('emotional_core'):
                    print(f"   💭 Emotional core: {analysis['emotional_core']}")
                if analysis.get('viral_angle'):
                    print(f"   🎯 Viral angle: {analysis['viral_angle']}")
        
        # Show best variation
        best = variations[0]
        print(f"\n🏆 BEST TWEET (Score: {best.get('score', 0)}/100):")
        print("-" * 60)
        print(best.get('tweet', ''))
        print("-" * 60)
        
        print("\n" + "="*60)
    
    print(f"\n✅ AI-powered tweets generated!")
    
    # Show generator stats
    generator = get_claude_generator()
    if generator.client:
        print(f"\n📈 Generator Status: Using Claude API")
        print(f"   Model: claude-3-haiku-20240307 (fast, cost-effective)")
        print(f"   Fallback: Template-based generator ready")
    else:
        print(f"\n⚠️  Generator Status: Using template fallback only")
        print(f"   Fix: Set ANTHROPIC_API_KEY environment variable")
    
    print(f"\n💡 Pro Tips:")
    print(f"   • Claude analyzes emotional hooks & viral angles")
    print(f"   • Multiple variations increase chances of virality")
    print(f"   • Scores help predict engagement potential")
    print(f"   • Fallback ensures reliability even if API fails")


if __name__ == "__main__":
    main()
