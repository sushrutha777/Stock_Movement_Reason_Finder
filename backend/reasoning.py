import os
from typing import List, Dict, Optional

import google.generativeai as genai
from dotenv import load_dotenv

# Load env vars once at import time
load_dotenv()
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY")


class ReasoningGenerator:
    """
    Service class to generate reasoning for stock moves using Gemini API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-3.6-flash",
    ):
        """
        Initialize the ReasoningGenerator.

        Args:
            api_key (str, optional): Gemini API key. If None, will use .env vlaue.
            model_name (str): Gemini model name.
        """
        # Prioritize passed key, then environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or DEFAULT_API_KEY
        self.model_name = model_name

        if not self.api_key:
            # You can raise an error here instead if you prefer
            print("Warning: GEMINI_API_KEY not found. Reasoning generation will fail.")

        # Configure Gemini once
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def _build_headlines_text(self, headlines: List[Dict]) -> str:
        """Convert list of headline dicts into displayable text."""
        if not headlines:
            return "No major news available."
        return "\n".join([f"- {h.get('title', '')}" for h in headlines])

    def _build_prompt(self, stock_info: str, headlines_text: str) -> str:
        """Create the prompt for Gemini."""
        return f"""
        Stock Analysis:
        {stock_info}

        Recent News:
        {headlines_text}

        Task:
        Please summarize why this stock may have moved in a way that a retail investor can easily understand.
        - Start with percentage of change in the stock(no intro sentences like 'Of course' or 'Here is a summary').  
        - Use simple, clear language for retail investors.  
        - Give 4-5 short bullet points explaining the key factors.
        - Keep it concise and actionable.  
        - Avoid unnecessary background or long explanations. Make it perfect.
        """

    def generate_reasoning(self, stock_info: str, headlines: List[Dict]) -> str:
        """
        Generate a concise explanation of stock movement.

        Args:
            stock_info (str): Info about the stock (price change, company details, etc.).
            headlines (list[dict]): List of headlines with "title" key.

        Returns:
            str: Explanation + separator line.
        """
        if not self.api_key or not self.model:
            return "Gemini API key not found."

        try:
            headlines_text = self._build_headlines_text(headlines)
            prompt = self._build_prompt(stock_info, headlines_text)

            response = self.model.generate_content(prompt)
            summary = response.text.strip() if response.text else "No response from Gemini."

            return f"{summary}\n\n---\n\n"

        except Exception as e:
            return f"Error generating reasoning: {str(e)}"
