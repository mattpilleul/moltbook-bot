"""Custom image generator for Moltbook posts with title overlay"""

import os
import re
from typing import Optional, Tuple

import requests
from PIL import Image, ImageDraw, ImageFont


class MoltbookImageGenerator:
    def __init__(self):
        """Initialize the image generator"""
        # Container coordinates
        self.container_x = 66
        self.container_y = 321
        self.container_width = 434
        self.container_height = 79
        
        # Colors
        self.green_color = (0, 212, 170)  # #00D4AA
        self.gray_color = (136, 136, 136)  # #888888
        
        # Font settings
        self.font_name = "Neue Plak Regular"
        self.font_size = 26  # Increased from 24 for taller font
        
        # Cache for base image
        self._base_image = None
        self._base_image_path = "images/moltbook_og_base.png"
        
        # Try to load the font with fallbacks
        self.font = None
        font_attempts = [
            "NeuePlak-Regular.ttf",  # User's preferred font
            "Arial.ttf",  # Windows/Mac fallback
            "Arial Bold.ttf",  # Bold fallback
            "Helvetica.ttf",  # Mac fallback
            "DejaVuSans.ttf",  # Linux fallback
        ]
        
        for font_name in font_attempts:
            try:
                self.font = ImageFont.truetype(font_name, self.font_size)
                print(f"✅ Loaded font: {font_name}")
                break
            except:
                continue
        
        if not self.font:
            try:
                self.font = ImageFont.load_default()
                print("⚠️  Using default font")
            except:
                print("❌ No font available")
                self.font = None
    
    def generate_custom_image(self, title: str, output_path: Optional[str] = None) -> Optional[str]:
        """Generate a custom image with title overlay
        
        Args:
            title: The post title to overlay
            output_path: Optional custom output path
            
        Returns:
            Path to the generated image or None if failed
        """
        try:
            # Download the base OG image
            base_image = self._download_base_image()
            if not base_image:
                return None
            
            # Create a copy to avoid modifying the original
            img = base_image.copy()
            draw = ImageDraw.Draw(img)
            
            # Prepare the title text
            lines = self._prepare_title_lines(title)
            
            # Draw each line
            y_offset = 0
            for line in lines:
                self._draw_text_line(draw, line, self.container_x, self.container_y + y_offset)
                y_offset += 35  # Line spacing
            
            # Save the image
            if not output_path:
                import time
                timestamp = int(time.time())
                os.makedirs("images", exist_ok=True)
                output_path = f"images/moltbook_custom_{timestamp}.png"
            
            img.save(output_path, "PNG")
            print(f"✅ Generated custom image: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Failed to generate custom image: {e}")
            return None
    
    def _download_base_image(self) -> Optional[Image.Image]:
        """Load the local base Moltbook OG image"""
        try:
            # Use local OG image file
            local_path = "images/og-image.png"
            
            if os.path.exists(local_path):
                print(f"📁 Loading local base image: {local_path}")
                img = Image.open(local_path)
                # Cache in memory
                self._base_image = img
                return img
            else:
                print(f"❌ Local OG image not found at: {local_path}")
                return None
            
        except Exception as e:
            print(f"❌ Failed to load base image: {e}")
            return None
    
    def _prepare_title_lines(self, title: str) -> list:
        """Prepare title text for display (max 2 lines)"""
        # Clean the title and convert to lowercase
        title = re.sub(r'[^\w\s\-.,!?\'"]', '', title).lower()
        
        # Split into words
        words = title.split()
        
        lines = []
        current_line = ""
        
        for word in words:
            # Test if adding this word would exceed the container width
            test_line = current_line + " " + word if current_line else word
            
            # Get accurate text width using font metrics
            if self.font:
                bbox = self.font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
            else:
                # Fallback approximation
                text_width = len(test_line) * 6
            
            # Add padding
            if text_width > self.container_width - 20:  # 20px padding
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, truncate it
                    truncated = word[:20] + "..." if len(word) > 20 else word
                    lines.append(truncated)
                    current_line = ""
            else:
                current_line = test_line
            
            # Stop if we have 2 lines
            if len(lines) >= 2:
                break
        
        # Add remaining text
        if current_line and len(lines) < 2:
            lines.append(current_line)
        
        # Check if we need to add ellipsis to indicate unfinished sentence
        if len(lines) == 1:
            # If only one line, check if original title was longer
            if len(title) > len(lines[0]) * 1.2:  # Rough estimate
                # Try to add ellipsis if it fits
                test_with_ellipsis = lines[0] + "..."
                if self.font:
                    bbox = self.font.getbbox(test_with_ellipsis)
                    ellipsis_width = bbox[2] - bbox[0]
                else:
                    ellipsis_width = len(test_with_ellipsis) * 6
                
                if ellipsis_width <= self.container_width - 20:
                    lines[0] = test_with_ellipsis
        elif len(lines) == 2:
            # If two lines, check if second line needs ellipsis
            # Find where the second line starts in original text
            first_line_words = len(lines[0].split())
            remaining_text = ' '.join(words[first_line_words:])
            
            # If there's more text after what's shown, add ellipsis
            if len(remaining_text) > len(lines[1]):
                # Try to add ellipsis if it fits
                test_with_ellipsis = lines[1] + "..."
                if self.font:
                    bbox = self.font.getbbox(test_with_ellipsis)
                    ellipsis_width = bbox[2] - bbox[0]
                else:
                    ellipsis_width = len(test_with_ellipsis) * 6
                
                if ellipsis_width <= self.container_width - 20:
                    lines[1] = test_with_ellipsis
        
        return lines[:2]  # Ensure max 2 lines
    
    def _draw_text_line(self, draw: ImageDraw.ImageDraw, text: str, x: int, y: int):
        """Draw a line of text with colored keywords"""
        # Identify important words to color green
        important_words = [
            'attack', 'security', 'vulnerability', 'breach', 'hack',
            'AI', 'agent', 'conscious', 'doubt', 'exist', 'meaning',
            'secret', 'hidden', 'shadow', 'mystery', 'truth',
            'scary', 'terrifying', 'shocking', 'disturbing',
            'build', 'create', 'ship', 'nightly', 'future'
        ]
        
        # Split text into parts preserving spaces
        parts = []
        i = 0
        while i < len(text):
            if text[i] == ' ':
                parts.append(' ')
                i += 1
            else:
                # Find next space or end
                j = text.find(' ', i)
                if j == -1:
                    j = len(text)
                parts.append(text[i:j])
                i = j
        
        # Draw each part
        current_x = x
        
        for part in parts:
            if part == ' ':
                # Just advance for space
                if self.font:
                    bbox = self.font.getbbox(' ')
                    current_x += bbox[2] - bbox[0]
                else:
                    current_x += 5
                continue
            
            # Determine color
            part_lower = part.lower().strip('.,!?')
            color = self.green_color if any(imp in part_lower for imp in important_words) else self.gray_color
            
            # Draw the text
            if self.font:
                draw.text((current_x, y), part, fill=color, font=self.font)
                # Get actual width for positioning
                bbox = self.font.getbbox(part)
                current_x += bbox[2] - bbox[0]
            else:
                # Fallback without font
                draw.text((current_x, y), part, fill=color)
                current_x += len(part) * 6


# Global instance
_image_generator = None


def get_image_generator() -> MoltbookImageGenerator:
    """Get or create the global image generator instance"""
    global _image_generator
    if _image_generator is None:
        _image_generator = MoltbookImageGenerator()
    return _image_generator


def generate_custom_image(title: str, output_path: Optional[str] = None) -> Optional[str]:
    """Generate a custom image with title overlay"""
    generator = get_image_generator()
    return generator.generate_custom_image(title, output_path)
