import json
import time

from playwright.sync_api import sync_playwright

COOKIES_FILE = 'twitter_cookies.json'


def post_to_twitter(tweet_text, cookies_json=None):
    """Post a tweet using browser automation"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        if cookies_json:
            try:
                cookies = json.loads(cookies_json)
                context.add_cookies(cookies)
                print("✓ Loaded saved session")
            except Exception as e:
                print(f"⚠️  Could not load cookies: {e}")
        
        page = context.new_page()
        
        try:
            print("📱 Opening Twitter...")
            page.goto('https://twitter.com/home', timeout=30000)
            time.sleep(3)
            
            if 'login' in page.url.lower():
                raise Exception("Not logged in! Please update cookies.")
            
            print("✍️  Writing tweet...")
            page.click('[data-testid="tweetTextarea_0"]', timeout=10000)
            time.sleep(1)
            
            page.keyboard.type(tweet_text, delay=50)
            time.sleep(2)
            
            print("🚀 Posting...")
            page.click('[data-testid="tweetButtonInline"]', timeout=10000)
            time.sleep(5)
            
            new_cookies = context.cookies()
            print("✅ Tweet posted successfully!")
            
            browser.close()
            return True, json.dumps(new_cookies)
            
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            browser.close()
            return False, None


def login_and_save_cookies():
    """Run this locally ONCE to save login session"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto('https://twitter.com/login')
        
        input("\n⚠️  Login manually in the browser, then press Enter here...")
        
        cookies = context.cookies()
        with open(COOKIES_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Saved session to {COOKIES_FILE}")
        print("⚠️  Add this to GitHub Secrets as TWITTER_COOKIES")
        
        browser.close()


if __name__ == '__main__':
    login_and_save_cookies()
