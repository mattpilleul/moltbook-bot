"""Claude API-powered viral tweet generator with image support"""

import os
import time
from typing import Dict, List, Optional, Tuple

import anthropic
import requests
from dotenv import load_dotenv

from .image_generator import generate_custom_image
from .viral_generator import generate_viral_tweet as fallback_generator

# Load environment variables
load_dotenv()


class ClaudeTweetGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client with API key from environment or parameter"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print("✅ Claude API client initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize Claude client: {e}")
                self.client = None
        else:
            print("⚠️  No Claude API key provided, using fallback generator")
    
    def generate_viral_tweet_with_image(self, post: Dict) -> Tuple[str, Optional[str]]:
        """Generate a single viral tweet with image
        
        Returns:
            Tuple of (tweet_text, image_path)
        """
        if not self.client:
            # Fallback to template-based generator
            tweet = fallback_generator(post)
            # Generate custom image
            image_path = generate_custom_image(post.get('title', ''))
            return tweet, image_path
        
        # Prepare the post data for Claude
        post_data = self._prepare_post_data(post)
        
        # Generate single best tweet with retry logic
        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    temperature=0.8,
                    system=self._get_system_prompt(),
                    messages=[
                        {
                            "role": "user",
                            "content": self._get_single_tweet_prompt(post_data)
                        }
                    ]
                )
                
                # Parse Claude's response
                tweet = self._parse_single_tweet_response(response.content[0].text, post.get('url', ''))
                
                # Generate custom image with title
                image_path = generate_custom_image(post.get('title', ''))
                
                return tweet, image_path
                
            except anthropic.RateLimitError:
                wait_time = 2 ** attempt
                print(f"⚠️  Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            except Exception as e:
                print(f"⚠️  Claude API error (attempt {attempt + 1}): {e}")
                if attempt == 2:
                    # Final fallback
                    tweet = fallback_generator(post)
                    image_path = generate_custom_image(post.get('title', ''))
                    return tweet, image_path
        
        # Should not reach here
        tweet = fallback_generator(post)
        image_path = generate_custom_image(post.get('title', ''))
        return tweet, image_path
    
    def _prepare_post_data(self, post: Dict) -> str:
        """Format post data for Claude"""
        return f"""
Title: {post.get('title', '')}
Author: {post.get('author', '')}
Upvotes: {post.get('upvotes', 0)}
Comments: {post.get('comments', 0)}
Content: {post.get('content', '')[:500]}...
URL: {post.get('url', '')}
"""
    
    def _get_single_tweet_prompt(self, post_data: str) -> str:
        """User prompt for generating a single best viral tweet"""
        return f"""Write a viral tweet (220-240 chars) about this Moltbook post:

{post_data}

Include hook, insight, and implications. Add 0-1 hashtags only if highly relevant. URL will be added separately.

Tweet:"""
    
    def _parse_single_tweet_response(self, response_text: str, url: str) -> str:
        """Parse Claude's single tweet response"""
        # Clean up the response
        tweet = response_text.strip()
        
        # Remove any quotes if present
        if tweet.startswith('"') and tweet.endswith('"'):
            tweet = tweet[1:-1]
        
        # If the response seems to include the prompt, extract just the tweet
        if "Tweet:" in tweet:
            # Get everything after "Tweet:"
            parts = tweet.split("Tweet:", 1)
            if len(parts) > 1:
                tweet = parts[1].strip()
        
        # Remove any remaining prompt artifacts
        lines = tweet.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines that look like part of the prompt
            if not line.startswith(('Write a viral tweet', 'Include hook', 'Post data:', 'Title:', 'Author:', 'Upvotes:', 'Comments:', 'Content:', 'URL:')):
                cleaned_lines.append(line)
        
        tweet = '\n'.join(cleaned_lines)
        
        # Calculate effective length (URLs count as 23 chars on Twitter)
        url_length = 23 if url else 0
        max_content_length = 280 - url_length
        
        # Ensure tweet is not too long
        if len(tweet) > max_content_length:
            # Find the last complete sentence before the limit
            truncated = tweet[:max_content_length - 3]  # Leave room for "..."
            # Try to end at a period or question mark
            last_period = truncated.rfind('.')
            last_question = truncated.rfind('?')
            last_exclamation = truncated.rfind('!')
            last_punct = max(last_period, last_question, last_exclamation)
            
            if last_punct > max_content_length * 0.7:  # Don't cut too much
                tweet = truncated[:last_punct + 1]
            else:
                tweet = truncated + "..."
        
        # Add URL if provided
        if url:
            tweet = tweet.rstrip() + '\n' + url
        
        return tweet
    
    def _get_system_prompt(self) -> str:
        """System prompt for Claude defining the persona and approach"""
        return """You are a viral social media manager specializing in AI content. Your tweets consistently get 10k+ impressions and high engagement.

Your approach:
1. Find the emotional core - what makes humans feel something
2. Create controversy or mystery - "they're hiding something"
3. Use quotable lines that make people stop scrolling
4. Include hooks that challenge assumptions about AI
5. Add relevant hashtags that boost visibility

Viral tweet patterns you master:
- "An AI just said this and I can't stop thinking about it..."
- "They're building something in the shadows..."
- "The scary part about [X] that nobody talks about..."
- "5 stages of [emotional journey]..."

Always keep tweets under 280 characters. Focus on engagement over information."""


# Global instance
_claude_generator = None


def get_claude_generator() -> ClaudeTweetGenerator:
    """Get or create the global Claude generator instance"""
    global _claude_generator
    if _claude_generator is None:
        _claude_generator = ClaudeTweetGenerator()
    return _claude_generator


def generate_viral_tweet_with_image(post: Dict) -> Tuple[str, Optional[str]]:
    """Generate the best viral tweet with image using Claude"""
    generator = get_claude_generator()
    return generator.generate_viral_tweet_with_image(post)
