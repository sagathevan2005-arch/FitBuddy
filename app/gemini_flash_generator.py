import os
import time
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    from google.genai.errors import ServerError
except ImportError:
    genai = None
    ServerError = Exception


def generate_nutrition_tip_with_flash(goal: str) -> str:

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    # Gemini unavailable → fallback
    if not api_key or genai is None:
        return _fallback_tip(goal)

    client = genai.Client(api_key=api_key)

    model = os.getenv(
        "GEMINI_NUTRITION_MODEL",
        "gemini-3.8-flash"
    )

    prompt = f"""
Give one concise, practical nutrition or recovery tip for someone whose
fitness goal is: {goal}.

Keep it to 2-4 sentences.
Avoid diagnosing medical conditions.
"""

    # Try Gemini up to 3 times
    for attempt in range(1, 4):

        try:
            print(
                f"Gemini nutrition request: "
                f"attempt {attempt}/3"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )

            if response and response.text:
                print("Nutrition tip generated successfully.")
                return response.text.strip()

        except ServerError as e:

            print(
                f"Gemini nutrition server error "
                f"on attempt {attempt}: {e}"
            )

            if attempt < 3:
                wait_time = 2 ** attempt
                print(
                    f"Retrying nutrition request "
                    f"in {wait_time} seconds..."
                )
                time.sleep(wait_time)

        except Exception as e:

            print(f"Nutrition Gemini error: {e}")
            break

    # Gemini still unavailable
    print("Using fallback nutrition tip.")
    return _fallback_tip(goal)


def _fallback_tip(goal: str) -> str:

    return (
        f"Nutrition/Recovery Tip for {goal}: "
        "Prioritize balanced meals, adequate protein, "
        "hydration, fruits and vegetables, and sufficient recovery."
    )