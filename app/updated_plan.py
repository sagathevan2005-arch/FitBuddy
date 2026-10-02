import os
import time
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
except ImportError:
    genai = None


def update_workout_plan(original_plan: str, feedback: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key or genai is None:
        return f"""DEMO UPDATED PLAN

Original plan was received.

User feedback:
{feedback}

In a production configuration, Gemini will use this feedback to regenerate
the full 7-day plan. For now, review the feedback and configure GEMINI_API_KEY
in the .env file to enable AI plan updating.

Original plan:
{original_plan}
"""

    client = genai.Client(api_key=api_key)

    # Your .env setting is used here.
    model = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.7-flash")

    prompt = f"""
You are updating a FitBuddy 7-day workout plan.

Original plan:
{original_plan}

User feedback:
{feedback}

Create a complete revised 7-day plan.
- Preserve useful parts of the original plan.
- Apply the user's feedback where reasonable.
- Keep the plan structured by Day 1 through Day 7.
- Include warm-up, main workout, and recovery/cooldown guidance.
- Do not provide medical diagnosis or treatment.
- If feedback indicates an injury or medical issue, recommend professional guidance.

Return only the revised plan.
"""

    # Retry temporary Gemini 503 errors.
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )

            return response.text.strip()

        except Exception as e:
            error_text = str(e)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                if attempt < 2:
                    time.sleep(5)
                    continue

                return """Gemini is temporarily busy and could not update your
workout plan right now.

Please wait a little while and try "Update Your Plan" again."""

            raise