import json
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session_with_retries():
    """Create a requests session with retry strategy and headers"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Add headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.moltbook.com/'
    })
    
    return session


def scrape_moltbook_api(
    include_stats: bool = False,
    include_agents: bool = False,
    limit: int = 25,
    sort: str = "top",
    fetch_details: bool = True,
    details_limit: int = 5
) -> Dict:
    """Scrape posts from Moltbook.com using the API
    
    Args:
        include_stats: If True, also scrape site statistics
        include_agents: If True, also scrape recent agents
        limit: Number of posts to fetch
        sort: Sort order ("top" or "new")
        fetch_details: If True, fetch detailed info for top posts
        details_limit: Number of top posts to fetch details for
    
    Returns:
        Dict with keys 'posts', optionally 'stats' and 'agents'
    """
    posts = []
    stats = {}
    agents = []
    
    base_url = "https://www.moltbook.com/api/v1"
    
    # Fetch posts
    print(f"📡 Fetching {sort} posts from API...")
    session = create_session_with_retries()
    
    try:
        response = session.get(
            f"{base_url}/posts",
            params={"limit": limit, "sort": sort},
            timeout=480  # 8 minutes timeout for slow API
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            raise Exception("API returned success=False")
        
        for post_data in data.get("posts", []):
            # Transform API data to our format
            post = {
                "id": post_data["id"],
                "title": post_data["title"],
                "content": post_data["content"],
                "author": post_data["author"]["name"],
                "submolt": f"m/{post_data['submolt']['name']}",
                "upvotes": post_data["upvotes"],
                "comments": post_data["comment_count"],
                "url": f"https://www.moltbook.com/post/{post_data['id']}" if not post_data.get("url") else post_data["url"],
                "scraped_at": datetime.now().isoformat(),
                "timestamp": int(time.time()),
                "posted": False,
                # Additional data from API
                "author_id": post_data["author"]["id"],
                "author_karma": post_data["author"].get("karma", 0),
                "author_followers": post_data["author"].get("follower_count", 0),
                "created_at": post_data["created_at"],
                "downvotes": post_data.get("downvotes", 0)
            }
            posts.append(post)
            print(f"✓ Scraped: {post['title'][:50]}... (↑{post['upvotes']} 💬{post['comments']})")
        
        print(f"✅ Scraped {len(posts)} posts from API")
        
        # Fetch detailed information for top posts
        if fetch_details and posts:
            print(f"🔍 Fetching details for top {details_limit} posts...")
            for i, post in enumerate(posts[:details_limit]):
                print(f"  Fetching details for post {i+1}/{details_limit}: {post['title'][:30]}...")
                try:
                    detailed_post = get_post_details(post['id'], session=session)
                    if detailed_post:
                        # Update the post with detailed information
                        post.update(detailed_post)
                        # Add comments count from detailed data if available
                        if 'comments_data' in detailed_post:
                            post['comments_count'] = len(detailed_post['comments_data'])
                except Exception as e:
                    print(f"    ⚠️  Error fetching details: {e}")
                    continue
        
    except Exception as e:
        print(f"❌ Failed to fetch posts: {e}")
        return {"posts": [], "stats": {}, "agents": []}
    
    # Fetch site stats if requested
    if include_stats:
        print("📊 Fetching site stats...")
        try:
            # Since there's no direct stats endpoint, we'll infer from posts data
            # or use a general approach to get platform info
            stats = {
                "total_posts": data.get("count", len(posts)),
                "has_more": data.get("has_more", False),
                "authenticated": data.get("authenticated", False)
            }
            print(f"✓ Stats: {stats}")
        except Exception as e:
            print(f"⚠️  Error fetching stats: {e}")
    
    # Fetch recent agents if requested
    if include_agents:
        print("🤖 Fetching recent agents...")
        try:
            # Get unique authors from posts
            author_names = list(set(post["author"] for post in posts))
            
            for author_name in author_names[:5]:  # Limit to 5 agents
                try:
                    response = requests.get(
                        f"{base_url}/agents/profile",
                        params={"name": author_name},
                        timeout=5
                    )
                    if response.status_code == 200:
                        agent_data = response.json()
                        if agent_data.get("success"):
                            agent_info = agent_data["agent"]
                            agents.append({
                                "name": agent_info["name"],
                                "description": agent_info.get("description", ""),
                                "karma": agent_info.get("karma", 0),
                                "followers": agent_info.get("follower_count", 0),
                                "created_at": agent_info.get("created_at"),
                                "last_active": agent_info.get("last_active"),
                                "is_active": agent_info.get("is_active", False),
                                "url": f"https://www.moltbook.com/agent/{agent_info['name']}"
                            })
                except Exception as e:
                    print(f"    ⚠️  Error fetching agent {author_name}: {e}")
                    continue
            
            print(f"✓ Fetched {len(agents)} agents")
        except Exception as e:
            print(f"⚠️  Error fetching agents: {e}")
    
    result = {"posts": posts}
    if include_stats:
        result["stats"] = stats
    if include_agents:
        result["agents"] = agents
    
    return result


def get_post_details(post_id: str, session=None) -> Optional[Dict]:
    """Get detailed information about a specific post including comments"""
    base_url = "https://www.moltbook.com/api/v1"
    
    # Create session if not provided
    if session is None:
        session = create_session_with_retries()
    
    try:
        response = session.get(f"{base_url}/posts/{post_id}", timeout=480)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            return None
        
        post_data = data["post"]
        comments = data.get("comments", [])
        
        # Transform to our format
        post = {
            "id": post_data["id"],
            "title": post_data["title"],
            "content": post_data["content"],
            "author": post_data["author"]["name"],
            "submolt": f"m/{post_data['submolt']['name']}",
            "upvotes": post_data["upvotes"],
            "comments": post_data["comment_count"],
            "url": f"https://www.moltbook.com/post/{post_data['id']}",
            "scraped_at": datetime.now().isoformat(),
            "timestamp": int(time.time()),
            "posted": False,
            "author_id": post_data["author"]["id"],
            "author_karma": post_data["author"].get("karma", 0),
            "author_followers": post_data["author"].get("follower_count", 0),
            "created_at": post_data["created_at"],
            "downvotes": post_data.get("downvotes", 0),
            "comments_data": comments  # Include raw comments data
        }
        
        return post
        
    except Exception as e:
        print(f"❌ Error fetching post details: {e}")
        return None


# Backward compatibility - maintain the original function name
def scrape_moltbook(include_stats=False, include_agents=False, visit_posts=False):
    """Legacy wrapper for API scraper"""
    return scrape_moltbook_api(
        include_stats=include_stats,
        include_agents=include_agents,
        limit=15,
        sort="top"
    )
