import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_reasoning(stock_info: str, headlines: list, api_key: str = DEFAULT_API_KEY) -> str:
    """
    Use Gemini API to generate reasoning from news headlines.
    
    Args:
        stock_info (str): Information about the stock (e.g., price change, company details).
        headlines (list): List of news headlines (each item should be a dict with "title").
        api_key (str): Gemini API key. If not provided, will use the one from .env.

    Returns:
        str: Concise explanation for why the stock may have moved,
             separated with a divider line for readability.
    """
    if not api_key:
        return "❌ Gemini API key not found."

    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")  # fast & cost-efficient

        # Prepare headlines text
        headlines_text = (
            "\n".join([f"- {h.get('title', '')}" for h in headlines]) 
            if headlines else "No major news available."
        )

        # Prompt
        prompt = f"""
        Stock Analysis:
        {stock_info}

        Recent News:
        {headlines_text}

        Please summarize why this stock may have moved in a way that a retail investor can easily understand. 
        - Use simple language. 
        - Give 3-5 clear bullet points explaining the key reasons. 
        - Highlight any major positive or negative factors affecting the stock price.
        - Avoid technical jargon.
        - Keep it concise and actionable.
        """

        # Gemini call
        response = model.generate_content(prompt)

        summary = response.text.strip() if response.text else "⚠️ No response from Gemini."

        # Add a separator line at the end
        # Add a full-width horizontal line instead of a fixed 50 chars
        return f"{summary}\n\n---\n\n"


    except Exception as e:
        return f"⚠️ Error generating reasoning: {str(e)}"
