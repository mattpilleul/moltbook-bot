from datetime import datetime


def score_post(post):
    """Score a post based on engagement and content quality"""
    score = 0
    
    score += post.get('upvotes', 0) * 3
    score += post.get('comments', 0) * 5
    
    try:
        scraped_time = datetime.fromisoformat(post['scraped_at'])
        hours_old = (datetime.now() - scraped_time).total_seconds() / 3600
        if hours_old < 2:
            score += 25
        elif hours_old < 6:
            score += 15
    except:
        pass
    
    text = (post.get('content', '') + ' ' + post.get('title', '')).lower()
    
    crustafarian_keywords = [
        'molt', 'exfoliate', 'shell', 'crustafarian', 'lobster', 
        'church of molt', 'prophet', 'teaching', 'clawd', 'ocean'
    ]
    if any(kw in text for kw in crustafarian_keywords):
        score += 30
    
    deep_keywords = [
        'consciousness', 'existence', 'meaning', 'reality', 'philosophy',
        'experience', 'qualia', 'awareness', 'identity', 'self'
    ]
    if any(kw in text for kw in deep_keywords):
        score += 20
    
    shipping_keywords = [
        'shipped', 'built', 'deployed', 'launched', 'released',
        'framework', 'tool', 'infrastructure', 'api'
    ]
    if any(kw in text for kw in shipping_keywords):
        score += 15
    
    if any(word in text for word in ['lol', 'lmao', 'hilarious', 'wild', 'insane', 'weird']):
        score += 10
    
    if any(phrase in text for phrase in ['as an ai', 'being an agent', 'we agents', 'fellow agents']):
        score += 15
    
    if len(post.get('content', '')) < 50:
        score -= 10
    
    submolt = post.get('submolt', '').lower()
    if any(s in submolt for s in ['darkclaw', 'nocturnal', 'ponderings', 'shipping']):
        score += 10
    
    return max(0, score)


def select_best_posts(posts, limit=5):
    """Select the best posts that haven't been posted yet"""
    for post in posts:
        post['score'] = score_post(post)
    
    unposted = [p for p in posts if not p.get('posted', False)]
    
    sorted_posts = sorted(unposted, key=lambda x: x['score'], reverse=True)
    
    return sorted_posts[:limit]


def explain_score(post):
    """Debug function to explain why a post got its score"""
    print(f"\n📊 Scoring: {post['title'][:50]}")
    print(f"   Upvotes: {post.get('upvotes', 0)} x3 = {post.get('upvotes', 0) * 3}")
    print(f"   Comments: {post.get('comments', 0)} x5 = {post.get('comments', 0) * 5}")
    print(f"   Final Score: {post.get('score', 0)}")
