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
        model = genai.GenerativeModel("gemini-2.5-flash") 

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

        Task:
        Please summarize why this stock may have moved in a way that a retail investor can easily understand.
        - Start with percentage of change in the stock(no intro sentences like 'Of course' or 'Here is a summary').  
        - Use simple, clear language for retail investors.  
        - Give 3-4 short bullet points explaining the key factors.
        - Keep it concise and actionable.  
        - Avoid unnecessary background or long explanations Make It Perfect.
        """

        # Gemini call
        response = model.generate_content(prompt)

        summary = response.text.strip() if response.text else "⚠️ No response from Gemini."

        # Add a separator line at the end
        # Add a full-width horizontal line instead of a fixed 50 chars
        return f"{summary}\n\n---\n\n"


    except Exception as e:
        return f"⚠️ Error generating reasoning: {str(e)}"