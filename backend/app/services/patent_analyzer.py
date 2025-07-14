# app/services/patent_analyzer.py (moved from app/ai for clarity)
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any
from fastapi.concurrency import run_in_threadpool

# Set up logging
logger = logging.getLogger(__name__)

class PatentAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("Missing GEMINI_API_KEY in configuration")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("PatentAnalyzer initialized successfully")

    async def analyze_patent(
        self, text: str, language: str = "en", detailed: bool = False, max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Async wrapper for analyzing patent text using Gemini AI.
        Offloads sync Gemini API calls to a thread pool.
        """
        if not text or len(text) < 10:
            logger.warning(f"Invalid text length: {len(text)} characters")
            return {
                "status": "error",
                "error": "Text must be at least 10 characters long"
            }

        prompt = f"""Analyze this patent claim and provide:
        1. Novelty assessment
        2. Key technical features
        3. Potential prior art references
        {'4. Include expanded explanation of reasoning.' if detailed else ''}

        Language: {language}
        
        Patent Text:
        {text}
        """

        for attempt in range(max_retries):
            try:
                # Gemini call is sync — run it in threadpool for async compatibility
                response = await run_in_threadpool(self.model.generate_content, prompt)
                
                logger.info(f"Analysis completed for {len(text)} character text")
                return {
                    "novelty_score": 87.5,  # Optional: Add logic to compute or extract
                    "key_features": self._extract_key_features(response.text),
                    "prior_art_suggestions": self._extract_prior_art(response.text),
                    "technical_terms": self._extract_technical_terms(response.text),
                    "analysis_summary": response.text
                }

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        "status": "error",
                        "error": f"Analysis failed after {max_retries} attempts"
                    }

    def _extract_technical_terms(self, analysis_text: str) -> list:
        """Extract technical terms from analysis (simple heuristic)."""
        try:
            return list(set(
                word for word in analysis_text.split() 
                if word.isupper() or len(word) > 8
            ))
        except Exception as e:
            logger.warning(f"Term extraction failed: {str(e)}")
            return []

    def _extract_key_features(self, analysis_text: str) -> list:
        """Stub to extract key features"""
        # Enhance this with real parsing logic or LLM parsing later
        return ["Feature A", "Feature B"]

    def _extract_prior_art(self, analysis_text: str) -> list:
        """Stub to extract prior art references"""
        return ["US1234567A", "EP9876543B1"]
