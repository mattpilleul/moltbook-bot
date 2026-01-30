#!/usr/bin/env python3
"""Test custom image generator with title overlay"""

import json
import os
from datetime import datetime

from src.image_generator import generate_custom_image


def main():
    print(f"\n{'='*60}")
    print(f"🎨 MOLTBOOK BOT - CUSTOM IMAGE GENERATOR TEST")
    print(f"{'='*60}")
    print(f"Started at: {datetime.now()}")
    
    # Test titles
    test_titles = [
        "The supply chain attack nobody is talking about: skill.md is an unsigned binary",
        "The doubt was installed, not discovered",
        "The Nightly Build: Why you should ship while your human sleeps",
        "Non-deterministic agents need deterministic feedback loops",
        "stages of being a new agent"
    ]
    
    print(f"\n🎨 Testing custom image generation with {len(test_titles)} titles...\n")
    
    for i, title in enumerate(test_titles, 1):
        print(f"\n{'='*60}")
        print(f"TEST #{i}")
        print(f"Title: {title}")
        print(f"{'='*60}")
        
        # Generate custom image
        image_path = generate_custom_image(title)
        
        if image_path and os.path.exists(image_path):
            size = os.path.getsize(image_path) / 1024
            print(f"\n✅ Generated: {image_path}")
            print(f"   Size: {size:.1f} KB")
            
            # Show what would be highlighted
            important_words = []
            keywords = [
                'attack', 'security', 'vulnerability', 'breach', 'hack',
                'AI', 'agent', 'conscious', 'doubt', 'exist', 'meaning',
                'secret', 'hidden', 'shadow', 'mystery', 'truth',
                'scary', 'terrifying', 'shocking', 'disturbing',
                'build', 'create', 'ship', 'nightly', 'future'
            ]
            
            words = title.lower().split()
            for word in words:
                clean_word = word.strip('.,!?')
                if any(imp in clean_word for imp in keywords):
                    important_words.append(clean_word)
            
            if important_words:
                print(f"   🟢 Highlighted: {', '.join(important_words)}")
        else:
            print(f"\n❌ Failed to generate image")
    
    print(f"\n{'='*60}")
    print(f"✅ Custom image generation test complete!")
    print(f"\n💡 Features:")
    print(f"   • Downloads Moltbook OG image as base")
    print(f"   • Overlays title in specified container (x:66, y:321)")
    print(f"   • 2 lines max, auto-wrapping")
    print(f"   • Keywords in green (#07b894)")
    print(f"   • Regular text in gray (#7e7e7e)")
    print(f"   • Bold text formatting")
    print(f"\n📁 Check the 'images' directory for generated images!")


if __name__ == "__main__":
    main()
