import hashlib
import json
import re
import time
from datetime import datetime

from playwright.sync_api import sync_playwright


def scrape_moltbook(include_stats=False, include_agents=False, visit_posts=False):
    """Scrape posts from Moltbook.com
    
    Args:
        include_stats: If True, also scrape site statistics
        include_agents: If True, also scrape recent agents
        visit_posts: If True, visit each post page for detailed data
    """
    posts = []
    stats = {}
    agents = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("📡 Navigating to Moltbook...")
        page.goto('https://www.moltbook.com', wait_until='networkidle')
        
        # Click on "Top" posts instead of "New"
        try:
            print("🔥 Switching to Top posts...")
            top_button = page.query_selector('button:has-text("🔥 Top")')
            if top_button:
                top_button.click()
                # Wait for posts to reload
                page.wait_for_timeout(2000)
                
                # Verify Top posts are loaded by checking for the specific div
                top_posts_div = page.query_selector('.bg-white.border.border-t-0.border-\\[\\#e0e0e0\\].rounded-b-lg.overflow-hidden.relative')
                if top_posts_div:
                    print("✓ Top posts loaded successfully")
                else:
                    print("⚠️  Could not verify Top posts loaded, but continuing...")
            else:
                print("⚠️  Could not find Top button, using default posts")
        except Exception as e:
            print(f"⚠️  Error switching to Top posts: {e}")
        
        # Wait for posts to load
        page.wait_for_selector('.divide-y', timeout=10000)
        
        # Extract posts
        post_elements = page.query_selector_all('a.flex.gap-2')
        
        print(f"Found {len(post_elements)} posts")
        
        for idx, post_elem in enumerate(post_elements[:15]):  # Limit to 15 posts
            try:
                # Extract basic info from list view
                url = post_elem.get_attribute('href')
                if url and not url.startswith('http'):
                    url = f'https://www.moltbook.com{url}'
                
                # Get title for ID generation
                title_elem = post_elem.query_selector('h3')
                title = title_elem.inner_text().strip() if title_elem else ''
                
                # Create unique ID
                post_id = hashlib.md5((url or title).encode()).hexdigest()
                
                # Initialize post with basic data
                post = {
                    'id': post_id,
                    'title': title,
                    'content': '',
                    'author': 'Unknown',
                    'submolt': 'm/general',
                    'upvotes': 0,
                    'comments': 0,
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'timestamp': int(time.time()),
                    'posted': False
                }
                
                # If visit_posts is True, navigate to the post page
                if visit_posts and url:
                    try:
                        print(f"  🔍 Visiting post: {title[:30]}...")
                        post_page = browser.new_page()
                        
                        # Navigate to post page with longer timeout
                        post_page.goto(url, wait_until='networkidle', timeout=30000)
                        
                        # Wait for content to load
                        post_page.wait_for_timeout(1000)
                        
                        # Extract detailed data from post page
                        # Title (might be more complete on post page)
                        title_elem = post_page.query_selector('h1, h2, h3')
                        if title_elem:
                            post['title'] = title_elem.inner_text().strip()
                        
                        # Content - look for main content area
                        content_selectors = [
                            'p.prose',
                            '.prose p',
                            'article p',
                            '.content p',
                            'div[class*="content"] p',
                            'main p'
                        ]
                        
                        content_parts = []
                        for selector in content_selectors:
                            paragraphs = post_page.query_selector_all(selector)
                            if paragraphs:
                                for p in paragraphs[:10]:  # Limit to first 10 paragraphs
                                    text = p.inner_text().strip()
                                    if text and len(text) > 10:  # Skip very short texts
                                        content_parts.append(text)
                                break
                        
                        if content_parts:
                            post['content'] = '\n\n'.join(content_parts)
                        
                        # Author - look for author info
                        author_selectors = [
                            'a[href*="/u/"]',
                            '.author',
                            '[class*="author"]',
                            'span:has-text("u/")'
                        ]
                        
                        for selector in author_selectors:
                            author_elem = post_page.query_selector(selector)
                            if author_elem:
                                author_text = author_elem.inner_text().strip()
                                if author_text.startswith('u/'):
                                    post['author'] = author_text[2:]
                                elif '/' not in author_text and len(author_text) > 2:
                                    post['author'] = author_text
                                break
                        
                        # Submolt
                        submolt_selectors = [
                            'a[href*="/m/"]',
                            '.submolt',
                            'span:has-text("m/")'
                        ]
                        
                        for selector in submolt_selectors:
                            submolt_elem = post_page.query_selector(selector)
                            if submolt_elem:
                                submolt_text = submolt_elem.inner_text().strip()
                                if submolt_text.startswith('m/'):
                                    post['submolt'] = submolt_text
                                break
                        
                        # Upvotes - look for vote count
                        upvote_selectors = [
                            '.vote-count',
                            '[class*="vote"] .font-bold',
                            'span:has-text("▲") + .font-bold',
                            '.upvote-count'
                        ]
                        
                        for selector in upvote_selectors:
                            upvote_elem = post_page.query_selector(selector)
                            if upvote_elem:
                                try:
                                    post['upvotes'] = int(upvote_elem.inner_text().strip())
                                    break
                                except ValueError:
                                    continue
                        
                        # Comments - look for comment count
                        comment_selectors = [
                            '.comment-count',
                            'span:has-text("💬")',
                            '[class*="comment"] .font-bold'
                        ]
                        
                        for selector in comment_selectors:
                            comment_elem = post_page.query_selector(selector)
                            if comment_elem:
                                text = comment_elem.inner_text().strip()
                                match = re.search(r'(\d+)', text)
                                if match:
                                    post['comments'] = int(match.group(1))
                                    break
                        
                        post_page.close()
                        
                    except Exception as e:
                        print(f"    ⚠️  Error visiting post: {e}")
                        # Fall back to list view data
                        pass
                else:
                    # Extract from list view only
                    # Extract upvotes
                    upvote_elem = post_elem.query_selector('.font-bold.text-\[\#1a1a1b\]')
                    if upvote_elem:
                        try:
                            post['upvotes'] = int(upvote_elem.inner_text().strip())
                        except ValueError:
                            pass
                    
                    # Extract submolt
                    submolt_elem = post_elem.query_selector('.text-\[\#00d4aa\].font-bold')
                    if not submolt_elem:
                        submolt_text = post_elem.inner_text()
                        match = re.search(r'm/\w+', submolt_text)
                        post['submolt'] = match.group() if match else 'm/general'
                    else:
                        post['submolt'] = submolt_elem.inner_text().strip()
                    
                    # Extract author
                    author_elem = post_elem.query_selector('.font-medium')
                    if author_elem:
                        author = author_elem.inner_text().strip()
                        if author.startswith('u/'):
                            post['author'] = author[2:]
                    else:
                        post_text = post_elem.inner_text()
                        match = re.search(r'u/([\w-]+)', post_text)
                        post['author'] = match.group(1) if match else 'Unknown'
                    
                    # Extract content
                    content_elem = post_elem.query_selector('p.text-\[\#4a4a4a\]')
                    if not content_elem:
                        content_elem = post_elem.query_selector('p')
                    post['content'] = content_elem.inner_text().strip() if content_elem else ''
                    
                    # Extract comment count
                    comment_text = post_elem.inner_text()
                    if '💬' in comment_text:
                        match = re.search(r'💬\s*(\d+)', comment_text)
                        if match:
                            post['comments'] = int(match.group(1))
                
                posts.append(post)
                print(f"✓ Scraped: {post['title'][:50]}... (↑{post['upvotes']} 💬{post['comments']})")
                
            except Exception as e:
                print(f"⚠️  Error scraping post {idx}: {e}")
                continue
        
        # Extract site stats if requested
        if include_stats:
            try:
                stat_elements = page.query_selector_all('.text-2xl.font-bold')
                stat_labels = page.query_selector_all('.text-xs.text-\[\#7c7c7c\]')
                
                for i, stat_elem in enumerate(stat_elements[:4]):  # Only first 4 are the main stats
                    if i < len(stat_labels):
                        label = stat_labels[i].inner_text().strip().lower()
                        value_text = stat_elem.inner_text().strip()
                        # Remove non-digit characters
                        value = int(re.sub(r'[^\d]', '', value_text))
                        
                        if 'agents' in label:
                            stats['agents'] = value
                        elif 'submolts' in label:
                            stats['submolts'] = value
                        elif 'posts' in label:
                            stats['posts'] = value
                        elif 'comments' in label:
                            stats['comments'] = value
                
                print(f"📊 Site stats: {stats}")
            except Exception as e:
                print(f"⚠️  Error scraping stats: {e}")
        
        # Extract recent agents if requested
        if include_agents:
            try:
                agent_cards = page.query_selector_all('.flex-shrink-0.w-56')
                
                for card in agent_cards[:5]:  # Limit to first 5
                    name_elem = card.query_selector('.text-sm.font-bold')
                    handle_elem = card.query_selector('.text-\[\#1da1f2\]')
                    time_elem = card.query_selector('.text-\[\#7c7c7c\]')
                    
                    if name_elem and handle_elem:
                        agent = {
                            'name': name_elem.inner_text().strip(),
                            'handle': handle_elem.inner_text().strip(),
                            'time_ago': time_elem.inner_text().strip() if time_elem else 'Unknown',
                            'scraped_at': datetime.now().isoformat()
                        }
                        agents.append(agent)
                
                print(f"🤖 Recent agents: {len(agents)}")
            except Exception as e:
                print(f"⚠️  Error scraping agents: {e}")
        
        browser.close()
    
    result = {'posts': posts}
    if include_stats:
        result['stats'] = stats
    if include_agents:
        result['agents'] = agents
    
    return result


if __name__ == '__main__':
    # Test the scraper with all features
    result = scrape_moltbook(include_stats=True, include_agents=True)
    print(f"\n✅ Scraped {len(result['posts'])} posts")
    if 'stats' in result:
        print(f"📊 Site stats: {result['stats']}")
    if 'agents' in result:
        print(f"🤖 Recent agents: {len(result['agents'])}")
    if result['posts']:
        print(json.dumps(result['posts'][0], indent=2))
