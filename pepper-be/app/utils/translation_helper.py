#!/usr/bin/env python3
"""
Translation Helper
Handles language detection and translation between Indonesian and English
"""

import re
from typing import Dict, Tuple, Optional

class TranslationHelper:
    
    # Simple dictionary untuk common phrases
    INDO_TO_ENGLISH = {
        "halo": "hello",
        "selamat pagi": "good morning",
        "selamat siang": "good afternoon", 
        "selamat sore": "good evening",
        "selamat malam": "good night",
        "terima kasih": "thank you",
        "sampai jumpa": "see you later",
        "maaf": "sorry",
        "permisi": "excuse me",
        "tolong": "please",
        "ya": "yes",
        "tidak": "no",
        "baik": "good",
        "buruk": "bad",
        "besar": "big",
        "kecil": "small",
        "cepat": "fast",
        "lambat": "slow",
        "cantik": "beautiful",
        "jelek": "ugly",
        "pintar": "smart",
        "bodoh": "stupid",
        "senang": "happy",
        "sedih": "sad",
        "marah": "angry",
        "takut": "afraid",
        "lapar": "hungry",
        "haus": "thirsty",
        "capek": "tired",
        "sakit": "sick",
        "sehat": "healthy"
    }
    
    # Reverse dictionary
    ENGLISH_TO_INDO = {v: k for k, v in INDO_TO_ENGLISH.items()}
    
    # Indonesian language indicators
    INDONESIAN_INDICATORS = [
        "selamat", "terima", "kasih", "sampai", "jumpa", "maaf", "permisi", 
        "tolong", "tidak", "dengan", "untuk", "dari", "yang", "adalah",
        "akan", "sudah", "belum", "saya", "anda", "kita", "mereka",
        "dimana", "kapan", "siapa", "apa", "kenapa", "bagaimana"
    ]
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect if text is Indonesian or English
        
        Args:
            text: Input text to analyze
            
        Returns:
            'indo' for Indonesian, 'en' for English
        """
        if not text or not text.strip():
            return 'indo'  # Default to Indonesian
        
        text_lower = text.lower().strip()
        
        # Check exact matches in dictionaries
        if text_lower in TranslationHelper.INDO_TO_ENGLISH:
            return 'indo'
        if text_lower in TranslationHelper.ENGLISH_TO_INDO:
            return 'en'
        
        # Check for Indonesian indicators
        words = text_lower.split()
        indonesian_word_count = 0
        
        for word in words:
            # Remove punctuation for checking
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in TranslationHelper.INDONESIAN_INDICATORS:
                indonesian_word_count += 1
            elif clean_word in TranslationHelper.INDO_TO_ENGLISH:
                indonesian_word_count += 1
        
        # If more than 30% of words are Indonesian indicators, classify as Indonesian
        if len(words) > 0 and (indonesian_word_count / len(words)) > 0.3:
            return 'indo'
        
        # Additional heuristics
        # Check for Indonesian-specific patterns
        if any(pattern in text_lower for pattern in ['ng', 'ny', 'kh', 'sy']):
            # These are common in Indonesian but less common in English
            return 'indo'
        
        # Default to English if no strong Indonesian indicators
        return 'en'
    
    @staticmethod
    def translate_text(text: str, target_language: str) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: 'indo' or 'en'
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        text_lower = text.lower().strip()
        
        # Check direct dictionary matches first
        if target_language == 'en' and text_lower in TranslationHelper.INDO_TO_ENGLISH:
            return TranslationHelper.INDO_TO_ENGLISH[text_lower]
        elif target_language == 'indo' and text_lower in TranslationHelper.ENGLISH_TO_INDO:
            return TranslationHelper.ENGLISH_TO_INDO[text_lower]
        
        # For multi-word phrases, try Google Translate
        try:
            return TranslationHelper._google_translate(text, target_language)
        except Exception as e:
            print(f"Google Translate failed: {e}")
            return TranslationHelper._fallback_translate(text, target_language)
    
    @staticmethod
    def _google_translate(text: str, target_language: str) -> str:
        """
        Use Google Translate API as primary translation method
        """
        try:
            from googletrans import Translator
            translator = Translator()
            
            # Map our language codes to Google's
            target_lang = 'en' if target_language == 'en' else 'id'
            
            result = translator.translate(text, dest=target_lang)
            return result.text
            
        except ImportError:
            print("googletrans not installed, using fallback translation")
            return TranslationHelper._fallback_translate(text, target_language)
        except Exception as e:
            print(f"Google Translate error: {e}")
            return TranslationHelper._fallback_translate(text, target_language)
    
    @staticmethod
    def _fallback_translate(text: str, target_language: str) -> str:
        """
        Fallback translation using word-by-word dictionary lookup
        """
        words = text.lower().split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = re.sub(r'[^\w]', '', word)
            
            if target_language == 'en' and clean_word in TranslationHelper.INDO_TO_ENGLISH:
                translated_words.append(TranslationHelper.INDO_TO_ENGLISH[clean_word])
            elif target_language == 'indo' and clean_word in TranslationHelper.ENGLISH_TO_INDO:
                translated_words.append(TranslationHelper.ENGLISH_TO_INDO[clean_word])
            else:
                # Keep original word if no translation found
                translated_words.append(word)
        
        return ' '.join(translated_words)
    
    @staticmethod
    def process_text_for_kamus(input_text: str) -> Dict[str, str]:
        """
        Process input text for Kamus_Bahasa entry creation
        
        Args:
            input_text: User input text
            
        Returns:
            Dict with 'text_indo' and 'text_english' keys
        """
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty")
        
        text = input_text.strip()
        detected_language = TranslationHelper.detect_language(text)
        
        if detected_language == 'indo':
            # Input is Indonesian, translate to English
            text_indo = text
            text_english = TranslationHelper.translate_text(text, 'en')
        else:
            # Input is English, translate to Indonesian
            text_english = text
            text_indo = TranslationHelper.translate_text(text, 'indo')
        
        return {
            'text_indo': text_indo,
            'text_english': text_english,
            'detected_language': detected_language
        } 