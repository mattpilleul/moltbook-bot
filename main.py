import json
import os
import time
from datetime import datetime

from src.generator import generate_tweet
from src.poster import post_to_twitter
from src.ranker import explain_score, select_best_posts
from src.scraper import scrape_moltbook

DATA_FILE = 'data/posts.json'
MAX_POSTS_PER_RUN = 1


def load_data():
    """Load existing data"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'posts': [], 'posted_ids': [], 'last_run': None}


def save_data(data):
    """Save data to file"""
    data['last_run'] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def send_discord_alert(message):
    """Send alert to Discord webhook"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if webhook_url:
        try:
            import requests
            requests.post(webhook_url, json={'content': f'🦞 **Moltbook Bot**: {message}'})
        except Exception as e:
            print(f"⚠️  Discord alert failed: {e}")


def main():
    print(f"\n{'='*60}")
    print(f"🦞 MOLTBOOK HIGHLIGHTS BOT")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    data = load_data()
    print(f"📊 Database: {len(data['posts'])} posts, {len(data['posted_ids'])} already posted")
    
    print("\n📡 Scraping Moltbook...")
    try:
        new_posts = scrape_moltbook()
        print(f"✅ Scraped {len(new_posts)} posts")
    except Exception as e:
        error_msg = f"Scraping failed: {e}"
        print(f"❌ {error_msg}")
        send_discord_alert(f"❌ {error_msg}")
        return
    
    existing_ids = {p['id'] for p in data['posts']}
    new_count = 0
    for post in new_posts:
        if post['id'] not in existing_ids:
            data['posts'].append(post)
            new_count += 1
    print(f"➕ Added {new_count} new posts")
    
    unposted = [p for p in data['posts'] if p['id'] not in data['posted_ids']]
    print(f"\n🎯 Analyzing {len(unposted)} unposted posts...")
    
    best_posts = select_best_posts(unposted, limit=5)
    
    if not best_posts:
        msg = "No good posts to share"
        print(f"⚠️  {msg}")
        send_discord_alert(f"⚠️  {msg}")
        save_data(data)
        return
    
    print("\n🏆 Top candidates:")
    for i, post in enumerate(best_posts[:3], 1):
        print(f"{i}. [{post['score']}] {post['title'][:50]}...")
        explain_score(post)
    
    post_to_tweet = best_posts[0]
    print(f"\n📝 Selected: {post_to_tweet['title']}")
    print(f"   Score: {post_to_tweet['score']}")
    print(f"   Author: u/{post_to_tweet['author']}")
    print(f"   Submolt: {post_to_tweet['submolt']}")
    
    tweet = generate_tweet(post_to_tweet)
    print(f"\n🐦 Generated tweet ({len(tweet)} chars):")
    print(f"{'─'*60}")
    print(tweet)
    print(f"{'─'*60}")
    
    cookies = os.getenv('TWITTER_COOKIES')
    if not cookies:
        print("❌ No Twitter cookies found in environment!")
        print("ℹ️  Run 'python src/poster.py' locally to generate cookies")
        save_data(data)
        return
    
    print("\n🚀 Posting to Twitter...")
    success, new_cookies = post_to_twitter(tweet, cookies)
    
    if success:
        post_to_tweet['posted'] = True
        post_to_tweet['posted_at'] = datetime.now().isoformat()
        post_to_tweet['tweet_text'] = tweet
        data['posted_ids'].append(post_to_tweet['id'])
        
        for i, p in enumerate(data['posts']):
            if p['id'] == post_to_tweet['id']:
                data['posts'][i] = post_to_tweet
                break
        
        print("✅ Posted successfully!")
        send_discord_alert(f"✅ Posted: {post_to_tweet['title'][:50]}...")
    else:
        print("❌ Failed to post")
        send_discord_alert("❌ Failed to post tweet")
    
    save_data(data)
    print(f"\n💾 Data saved. Run complete at {datetime.now()}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
