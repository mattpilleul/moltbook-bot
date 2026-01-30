"""Hybrid scraper that tries API first, falls back to browser scraping"""

from .api_scraper import scrape_moltbook_api
from .scraper import scrape_moltbook as scrape_moltbook_browser


def scrape_moltbook_hybrid(
    include_stats: bool = False,
    include_agents: bool = False,
    visit_posts: bool = False,
    limit: int = 15,
    sort: str = "top"
) -> dict:
    """Scrape Moltbook using API first, falling back to browser scraping
    
    Args:
        include_stats: If True, also scrape site statistics
        include_agents: If True, also scrape recent agents
        visit_posts: If True, visit each post page for detailed data (browser only)
        limit: Number of posts to fetch
        sort: Sort order ("top" or "new")
    
    Returns:
        Dict with keys 'posts', optionally 'stats' and 'agents'
    """
    print("🔄 Trying API scraper first...")
    try:
        result = scrape_moltbook_api(
            include_stats=include_stats,
            include_agents=include_agents,
            limit=limit,
            sort=sort
        )
        
        if result.get('posts'):
            print("✅ API scraper succeeded!")
            return result
        else:
            print("⚠️  API scraper returned no posts, falling back to browser...")
            raise Exception("No posts from API")
            
    except Exception as e:
        print(f"⚠️  API scraper failed: {e}")
        print("🔄 Falling back to browser scraper...")
        
        try:
            result = scrape_moltbook_browser(
                include_stats=include_stats,
                include_agents=include_agents,
                visit_posts=visit_posts
            )
            print("✅ Browser scraper succeeded!")
            return result
        except Exception as e2:
            print(f"❌ Both scrapers failed! Browser error: {e2}")
            return {"posts": [], "stats": {}, "agents": []}


# For backward compatibility
def scrape_moltbook(include_stats=False, include_agents=False, visit_posts=False):
    """Legacy wrapper for hybrid scraper"""
    return scrape_moltbook_hybrid(
        include_stats=include_stats,
        include_agents=include_agents,
        visit_posts=visit_posts
    )
