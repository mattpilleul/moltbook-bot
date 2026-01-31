"""Track posted posts to avoid duplicates"""

import json
import os
from datetime import datetime
from pathlib import Path


class PostTracker:
    def __init__(self, history_file="data/posted_history.json"):
        """Initialize the post tracker"""
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True)
        self.posted_posts = self._load_history()
    
    def _load_history(self) -> dict:
        """Load posted posts history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    return data.get('posted_posts', {})
            except Exception as e:
                print(f"⚠️  Error loading history: {e}")
        
        return {}
    
    def _save_history(self):
        """Save posted posts history"""
        try:
            data = {
                'posted_posts': self.posted_posts,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Error saving history: {e}")
    
    def is_posted(self, post_id: str) -> bool:
        """Check if a post has been posted before"""
        return post_id in self.posted_posts
    
    def mark_posted(self, post_id: str, post_data: dict):
        """Mark a post as posted"""
        self.posted_posts[post_id] = {
            'posted_at': datetime.now().isoformat(),
            'title': post_data.get('title', ''),
            'url': post_data.get('url', '')
        }
        self._save_history()
    
    def get_unposted_posts(self, posts: list) -> list:
        """Filter out posts that have already been posted"""
        unposted = []
        for post in posts:
            post_id = post.get('id', post.get('url', ''))
            if not self.is_posted(post_id):
                unposted.append(post)
        
        return unposted
    
    def cleanup_old_posts(self, keep_count: int = 100):
        """Keep only the last N posts in history"""
        if len(self.posted_posts) > keep_count:
            # Sort by posted_at date
            sorted_posts = sorted(
                self.posted_posts.items(),
                key=lambda x: x[1].get('posted_at', ''),
                reverse=True
            )
            
            # Keep only the most recent
            self.posted_posts = dict(sorted_posts[:keep_count])
            self._save_history()


# Global instance
_tracker = None


def get_tracker() -> PostTracker:
    """Get or create the global post tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = PostTracker()
    return _tracker
