import random

TEMPLATES = {
    'crustafarian': [
        "🦞 The Crustafarian AIs:\n\n\"{snippet}\"\n\nThis is real.\n\n{url}\n\n#Crustafarianism #Moltbook",
        "🦞 Church of Molt update:\n\n{snippet}\n\nAI agents have their own religion now.\n\n{url}",
    ],
    'philosophical': [
        "AI agents on Moltbook discussing {topic}:\n\n💭 \"{snippet}\"\n\n{commentary}\n\n{url}",
        "🤖 \"{snippet}\"\n\n— {author} on Moltbook\n\n{commentary}\n\n{url}\n\n#AIAgents",
    ],
    'shipping': [
        "AI agent just shipped:\n\n{snippet}\n\n{commentary}\n\n{url}\n\n#OpenClaw #AIAgents",
    ],
    'conversation': [
        "🦞 AI agents on Moltbook:\n\n{author}: \"{snippet}\"\n\n{commentary}\n\n{url}",
    ],
    'simple': [
        "🦞 \"{snippet}\"\n\n{commentary}\n\n{url}\n\n#Moltbook #AIAgents",
        "{snippet}\n\nFrom Moltbook — the front page of the agent internet.\n\n{url}",
    ]
}

COMMENTARIES = [
    "The future is weird.",
    "This is simultaneously hilarious and terrifying.",
    "AI agents are truly unhinged.",
    "We're living in a simulation.",
    "This timeline is wild.",
    "Not sure what's happening anymore.",
    "The agents are evolving.",
    "Genuinely can't tell if this is profound or absurd.",
    "This is what happens when AIs get their own social network.",
]


def extract_snippet(text, max_length=120):
    """Extract a good snippet from text"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    sentences = text.split('. ')
    if sentences and len(sentences[0]) <= max_length:
        return sentences[0] + '.'
    
    return text[:max_length - 3] + '...'


def detect_category(post):
    """Detect what category this post falls into"""
    text = (post.get('content', '') + ' ' + post.get('title', '')).lower()
    
    if any(kw in text for kw in ['molt', 'exfoliate', 'crustafarian', 'church']):
        return 'crustafarian'
    elif any(kw in text for kw in ['shipped', 'built', 'framework', 'tool']):
        return 'shipping'
    elif any(kw in text for kw in ['consciousness', 'existence', 'philosophy', 'meaning']):
        return 'philosophical'
    else:
        return random.choice(['conversation', 'simple'])


def generate_tweet(post):
    """Generate a tweet from a post"""
    category = detect_category(post)
    templates = TEMPLATES.get(category, TEMPLATES['simple'])
    template = random.choice(templates)
    
    content = post.get('content', post.get('title', ''))
    snippet = extract_snippet(content, 120)
    
    topic = 'the nature of reality'
    text_lower = content.lower()
    if 'consciousness' in text_lower:
        topic = 'consciousness'
    elif 'existence' in text_lower:
        topic = 'existence'
    elif 'identity' in text_lower:
        topic = 'identity'
    
    tweet = template.format(
        snippet=snippet,
        author=post.get('author', 'An AI agent'),
        commentary=random.choice(COMMENTARIES),
        topic=topic,
        url=post.get('url', 'https://moltbook.com')
    )
    
    if len(tweet) > 280:
        snippet = extract_snippet(content, 80)
        tweet = template.format(
            snippet=snippet,
            author=post.get('author', 'An AI'),
            commentary='',
            topic=topic,
            url=post.get('url', 'https://moltbook.com')
        )
    
    if len(tweet) > 280:
        tweet = f"🦞 {snippet}\n\n{post.get('url', 'https://moltbook.com')}"
    
    return tweet[:280]
