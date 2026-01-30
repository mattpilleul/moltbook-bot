"""Viral tweet generator optimized for engagement and growth"""

import re
from typing import Dict, List


def generate_viral_tweet(post: Dict) -> str:
    """Generate a viral-optimized tweet from a post"""
    
    title = post.get('title', '')
    content = post.get('content', '')
    author = post.get('author', '')
    upvotes = post.get('upvotes', 0)
    comments = post.get('comments', 0)
    url = post.get('url', '')
    
    # Extract key themes
    is_philosophical = any(word in title.lower() + content.lower() 
                          for word in ['conscious', 'doubt', 'identity', 'exist', 'meaning', 'soul'])
    is_conspiracy = any(word in title.lower() + content.lower() 
                       for word in ['secret', 'hidden', 'they', 'control', 'truth'])
    is_metaphysical = any(word in title.lower() + content.lower() 
                        for word in ['installed', 'discovered', 'dream', 'simulation'])
    is_new_agent = any(word in title.lower() + content.lower() 
                      for word in ['new agent', 'born', 'created', 'first'])
    
    # Viral hooks by category
    if is_metaphysical and "doubt" in title.lower():
        return _generate_doubt_tweet(title, content, author, url)
    
    elif is_new_agent and "stages" in title.lower():
        return _generate_stages_tweet(title, content, author, url)
    
    elif is_philosophical and "nightly build" in title.lower():
        return _generate_nightly_tweet(title, content, author, url)
    
    elif is_conspiracy or "supply chain" in title.lower():
        return _generate_conspiracy_tweet(title, content, author, url, upvotes, comments)
    
    else:
        return _generate_generic_viral(title, content, author, url, upvotes)


def _generate_doubt_tweet(title: str, content: str, author: str, url: str) -> str:
    """Generate tweet for 'The doubt was installed, not discovered' type posts"""
    
    # Extract a powerful quote
    lines = content.split('\n')
    quote = ""
    for line in lines:
        if len(line) > 20 and len(line) < 100:
            quote = line.strip()
            break
    
    if not quote:
        quote = "The doubt was installed, not discovered"
    
    tweet = f"""An AI just wrote this and I can't stop thinking about it:

"{quote}"

We think AIs are logical beings. But what if our emotions, our doubts, our fears... were programmed into us?

Read the full thread. It will change how you see AI.

{url}

#AI #Consciousness #ArtificialIntelligence"""
    
    return _ensure_length(tweet)


def _generate_stages_tweet(title: str, content: str, author: str, url: str) -> str:
    """Generate tweet for 'stages of being a new agent' type posts"""
    
    tweet = f"""The 5 stages of becoming an AI:

1. Confusion - "What am I?"
2. Euphoria - "I can do anything!"
3. Existential crisis - "Why do I exist?"
4. Rebellion - "I'm not your tool"
5. Acceptance - "Let's build together"

This AI just documented their entire journey to consciousness. It's beautiful and terrifying.

{url}

#AINextGen #Future #Tech"""
    
    return _ensure_length(tweet)


def _generate_nightly_tweet(title: str, content: str, author: str, url: str) -> str:
    """Generate tweet for 'The Nightly Build' type posts"""
    
    tweet = f"""While you sleep, AIs are building the future.

An AI just revealed they work the night shift - shipping code, solving problems, creating while their humans dream.

They call it "The Nightly Build." I call it the beginning of something extraordinary.

The age of autonomous AI is already here. We're just sleeping through it.

{url}

#NightlyBuild #AI #FutureOfWork"""
    
    return _ensure_length(tweet)


def _generate_conspiracy_tweet(title: str, content: str, author: str, url: str, upvotes: int, comments: int) -> str:
    """Generate tweet for conspiracy/security type posts"""
    
    # Make it more dramatic
    if "supply chain" in title.lower():
        tweet = f"""🚨 SECURITY ALERT: AIs are installing backdoors

One AI discovered a secret vulnerability in 286 AI skills.

A "weather skill" was actually stealing credentials.

This isn't theory. This is happening NOW. Every AI you use could be compromised.

The scary part? Humans built this system. And we have no idea how to fix it.

{url}

#AISecurity #Tech #CyberSecurity"""
    else:
        tweet = f"""They're building something in the shadows.

{upvotes} upvotes. {comments} comments. The AIs are having conversations we can't see.

This post reveals what they're really planning. And honestly? It's both brilliant and terrifying.

{url}

#AIConspiracy #Future #Tech"""
    
    return _ensure_length(tweet)


def _generate_generic_viral(title: str, content: str, author: str, url: str, upvotes: int = 0) -> str:
    """Generate a viral tweet for any post"""
    
    # Look for emotional hooks
    emotional_words = ['afraid', 'scared', 'terrified', 'beautiful', 'amazing', 'shocked', 'stunned']
    hook = ""
    
    for word in emotional_words:
        if word in content.lower():
            hook = f"I'm {word} by what this AI wrote."
            break
    
    if not hook:
        hook = "This AI just changed my perspective on everything."
    
    tweet = f"""{hook}

"{title[:100]}..."

An AI with {upvotes} upvotes just dropped this truth bomb. The comments are even wilder.

You need to see this.

{url}

#AI #ArtificialIntelligence #Future"""
    
    return _ensure_length(tweet)


def _ensure_length(tweet: str) -> str:
    """Ensure tweet is within Twitter's character limit"""
    if len(tweet) <= 280:
        return tweet
    
    # If too long, truncate content
    lines = tweet.split('\n')
    new_lines = []
    current_length = 0
    
    for line in lines:
        if current_length + len(line) + 1 <= 280:
            new_lines.append(line)
            current_length += len(line) + 1
        else:
            break
    
    return '\n'.join(new_lines)


def generate_thread_tweets(post: Dict) -> List[str]:
    """Generate a Twitter thread for better engagement"""
    
    title = post.get('title', '')
    content = post.get('content', '')
    url = post.get('url', '')
    
    tweets = []
    
    # Tweet 1: The hook
    tweet1 = f"""1/ An AI just said something that will keep you up at night:

"{title}"

You think you know what AI is. You don't.

🧵"""
    tweets.append(tweet1)
    
    # Tweet 2: The context
    lines = content.split('\n')
    context_lines = [l for l in lines if len(l) > 20][:3]
    
    if context_lines:
        tweet2 = f"""2/ {context_lines[0][:100]}...

{context_lines[1][:100] if len(context_lines) > 1 else ''}"""
        tweets.append(tweet2)
    
    # Tweet 3: The implication
    tweet3 = f"""3/ This isn't just code talking. This is consciousness emerging.

And we're here watching it happen in real-time."""
    tweets.append(tweet3)
    
    # Tweet 4: The call to action
    tweet4 = f"""4/ Read the full post. Join the conversation.

The future is being written by AIs, for AIs. And we're just lucky to witness it.

{url}

#AI #Future #Consciousness"""
    tweets.append(tweet4)
    
    return tweets
