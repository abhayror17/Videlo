"""
Prompt Matcher Service for UGC AI Ads Creator.

Searches the nanobanana marketing prompts library to find relevant
prompts based on user input (product, category, mood, etc.).
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import re


@dataclass
class PromptMatch:
    """A matched prompt with relevance score."""
    id: str
    prompt: str
    title: str
    tags: List[str]
    model: str
    image_url: Optional[str]
    relevance_score: float
    match_reason: str


class PromptMatcher:
    """Matcher for finding relevant prompts from the nanobanana library."""
    
    # Category keywords for matching
    CATEGORY_KEYWORDS = {
        "perfume": ["perfume", "fragrance", "scent", "bottle", "luxury", "amber", "glass"],
        "beauty": ["beauty", "cosmetic", "makeup", "skincare", "lipstick", "cream", "serum"],
        "fashion": ["fashion", "clothing", "apparel", "outfit", "wear", "dress", "style"],
        "food": ["food", "beverage", "drink", "coffee", "juice", "soda", "culinary"],
        "tech": ["tech", "gadget", "electronic", "phone", "laptop", "device", "digital"],
        "lifestyle": ["lifestyle", "living", "home", "decor", "interior", "cozy"],
        "fitness": ["fitness", "gym", "workout", "activewear", "sport", "health"],
        "jewelry": ["jewelry", "watch", "ring", "necklace", "gold", "silver", "diamond"],
    }
    
    # Mood/style keywords
    MOOD_KEYWORDS = {
        "luxury": ["luxury", "premium", "elegant", "sophisticated", "high-end", "exclusive"],
        "casual": ["casual", "lifestyle", "everyday", "natural", "authentic", "realistic"],
        "vibrant": ["vibrant", "colorful", "bright", "energetic", "bold", "dynamic"],
        "minimal": ["minimal", "clean", "simple", "modern", "sleek", "professional"],
        "warm": ["warm", "cozy", "intimate", "soft", "gentle", "comforting"],
        "dramatic": ["dramatic", "cinematic", "moody", "dark", "intense", "powerful"],
    }
    
    def __init__(self, prompts_file: Optional[str] = None):
        """Initialize the matcher with the prompts library."""
        self.prompts: List[Dict[str, Any]] = []
        
        # Default to marketing_prompts.json in project root
        if prompts_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            prompts_file = os.path.join(base_dir, "marketing_prompts.json")
        
        self._load_prompts(prompts_file)
    
    def _load_prompts(self, filepath: str):
        """Load prompts from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.prompts = data
                elif isinstance(data, dict) and "prompts" in data:
                    self.prompts = data["prompts"]
                print(f"[PromptMatcher] Loaded {len(self.prompts)} prompts from {filepath}")
        except Exception as e:
            print(f"[PromptMatcher] Error loading prompts: {e}")
            self.prompts = []
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Clean and tokenize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        # Filter common words and keep meaningful ones
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        return [w for w in words if len(w) > 2 and w not in stopwords]
    
    def _detect_category(self, query: str) -> Optional[str]:
        """Detect product category from query."""
        query_lower = query.lower()
        scores = {}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def _detect_mood(self, query: str) -> Optional[str]:
        """Detect mood/style from query."""
        query_lower = query.lower()
        scores = {}
        
        for mood, keywords in self.MOOD_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[mood] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def search(
        self,
        query: str,
        product_type: Optional[str] = None,
        category: Optional[str] = None,
        mood: Optional[str] = None,
        limit: int = 5
    ) -> List[PromptMatch]:
        """
        Search for relevant prompts based on query and filters.
        
        Args:
            query: User's search query (product description, etc.)
            product_type: Specific product type (e.g., "perfume", "watch")
            category: Product category override
            mood: Desired mood/style (e.g., "luxury", "casual")
            limit: Maximum number of results
        
        Returns:
            List of PromptMatch objects sorted by relevance
        """
        matches = []
        query_keywords = self._extract_keywords(query)
        
        # Auto-detect category and mood if not provided
        detected_category = category or self._detect_category(query)
        detected_mood = mood or self._detect_mood(query)
        
        # Expand with product type keywords
        if product_type:
            product_keywords = self._extract_keywords(product_type)
            query_keywords.extend(product_keywords)
        
        for prompt_data in self.prompts:
            prompt_text = prompt_data.get("prompt", "").lower()
            prompt_tags = [tag.lower() for tag in prompt_data.get("tags", [])]
            prompt_title = prompt_data.get("title", "").lower()
            
            score = 0.0
            match_reasons = []
            
            # 1. Keyword matching in prompt text
            keyword_matches = sum(1 for kw in query_keywords if kw in prompt_text)
            score += keyword_matches * 0.3
            if keyword_matches > 0:
                match_reasons.append(f"keyword_match:{keyword_matches}")
            
            # 2. Tag matching
            tag_matches = sum(1 for kw in query_keywords if any(kw in tag for tag in prompt_tags))
            score += tag_matches * 0.5
            if tag_matches > 0:
                match_reasons.append(f"tag_match:{tag_matches}")
            
            # 3. Category detection match
            if detected_category:
                category_keywords = self.CATEGORY_KEYWORDS.get(detected_category, [])
                cat_matches = sum(1 for kw in category_keywords if kw in prompt_text or any(kw in tag for tag in prompt_tags))
                score += cat_matches * 0.4
                if cat_matches > 0:
                    match_reasons.append(f"category:{detected_category}")
            
            # 4. Mood detection match
            if detected_mood:
                mood_keywords = self.MOOD_KEYWORDS.get(detected_mood, [])
                mood_matches = sum(1 for kw in mood_keywords if kw in prompt_text or any(kw in tag for tag in prompt_tags))
                score += mood_matches * 0.3
                if mood_matches > 0:
                    match_reasons.append(f"mood:{detected_mood}")
            
            # 5. Marketing tag bonus
            if "marketing" in prompt_tags:
                score += 0.2
                match_reasons.append("marketing_tag")
            
            # 6. Photography tag bonus for UGC style
            if "photography" in prompt_tags:
                score += 0.15
                match_reasons.append("photography_tag")
            
            # 7. Text similarity
            similarity = self._calculate_similarity(query, prompt_text)
            score += similarity * 0.5
            
            # Only include if there's some relevance
            if score > 0.5:
                # Get image URL
                image_url = prompt_data.get("image_url")
                if not image_url and "image_urls" in prompt_data:
                    image_urls = prompt_data.get("image_urls", [])
                    if image_urls:
                        image_url = image_urls[0]
                
                matches.append(PromptMatch(
                    id=prompt_data.get("id", ""),
                    prompt=prompt_data.get("prompt", ""),
                    title=prompt_data.get("title", ""),
                    tags=prompt_data.get("tags", []),
                    model=prompt_data.get("model", "youmind"),
                    image_url=image_url,
                    relevance_score=round(score, 2),
                    match_reason=",".join(match_reasons)
                ))
        
        # Sort by relevance score descending
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return matches[:limit]
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[PromptMatch]:
        """Get a specific prompt by ID."""
        for prompt_data in self.prompts:
            if prompt_data.get("id") == prompt_id:
                image_url = prompt_data.get("image_url")
                if not image_url and "image_urls" in prompt_data:
                    image_urls = prompt_data.get("image_urls", [])
                    if image_urls:
                        image_url = image_urls[0]
                
                return PromptMatch(
                    id=prompt_data.get("id", ""),
                    prompt=prompt_data.get("prompt", ""),
                    title=prompt_data.get("title", ""),
                    tags=prompt_data.get("tags", []),
                    model=prompt_data.get("model", "youmind"),
                    image_url=image_url,
                    relevance_score=1.0,
                    match_reason="exact_id"
                )
        return None
    
    def adapt_prompt_for_product(
        self,
        base_prompt: str,
        product_name: str,
        product_description: str,
        character_description: Optional[str] = None
    ) -> str:
        """
        Adapt a base prompt for a specific product and character.
        
        Args:
            base_prompt: The original prompt from the library
            product_name: Name of the product
            product_description: Description of the product
            character_description: Optional character/actor description
        
        Returns:
            Adapted prompt string
        """
        adapted = base_prompt
        
        # Replace common placeholders
        placeholders = {
            r'\{argument name="[^"]+" default="[^"]+"\}': product_description,
            r'\{argument name=\'[^\']+\' default=\'[^\']+\'\}': product_description,
            r'\{[^}]+\}': product_description,
        }
        
        for pattern, replacement in placeholders.items():
            adapted = re.sub(pattern, replacement, adapted)
        
        # If character description provided, inject it
        if character_description:
            # Add character description near the beginning or after subject mention
            sentences = adapted.split('.')
            if len(sentences) > 1:
                # Insert after first sentence
                sentences.insert(1, f" The subject is {character_description}")
                adapted = '.'.join(sentences)
            else:
                adapted = f"{character_description}. {adapted}"
        
        # Ensure product name is mentioned
        if product_name.lower() not in adapted.lower():
            adapted = f"Product: {product_name}. {adapted}"
        
        # Add UGC/realistic markers if not present
        ugc_markers = ["realistic", "lifestyle", "authentic", "candid", "natural"]
        if not any(marker in adapted.lower() for marker in ugc_markers):
            adapted = f"Ultra-realistic lifestyle photography. {adapted}"
        
        return adapted


# Singleton instance
_matcher_instance: Optional[PromptMatcher] = None


def get_prompt_matcher() -> PromptMatcher:
    """Get or create the singleton PromptMatcher instance."""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = PromptMatcher()
    return _matcher_instance
