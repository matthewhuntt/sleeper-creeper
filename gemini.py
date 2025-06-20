# gemini_api.py
import requests
import json
from google import genai

def generate_recap(api_key, summary_data, league_member_info=None):
    """Sends data to Gemini and gets a fantasy recap using the Google AI SDK."""
    try:
        client = genai.Client(api_key=api_key)

        model = "gemini-2.5-flash"

        # This is the prompt that instructs Gemini on its persona and task
        prompt = f"""
        You are a sarcastic and witty fantasy football commentator.
        Your task is to write a weekly recap for a fantasy football league.
        Use the provided data to call out specific teams and scores, but don't simply restate the outcomes. 
        You do not need to recap every single game, but rather focus on the most interesting and impactful matchups.
        Think hard and come up with insightful commentary that goes beyond the results.
        Be as succinct as possible.
        
        {league_member_info if league_member_info else ""}

        Here is the data for the week:
        ---
        {summary_data}
        ---

        Now, write the recap. After the summary, answer the following questions in 1-2 sentences each:

        1. What was the most surprising outcome of the week?
        2. Which player had the biggest impact on their team's performance?
        3. What was the funniest moment of the week?
        4. Any other notable events or performances? 
        """

        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"An error occurred while generating the recap: {e}")
        return "Failed to generate recap due to an API error."
