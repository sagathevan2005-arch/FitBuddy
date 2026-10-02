import os
import time
from dotenv import load_dotenv

load_dotenv()

# Check API key
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
print("Gemini API key loaded:", bool(api_key))

try:
    from google import genai
    from google.genai.errors import ServerError
except ImportError:
    genai = None
    ServerError = Exception


def _client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key or genai is None:
        return None

    return genai.Client(api_key=api_key)


def generate_workout_gemini(
    age: int,
    weight: str,
    goal: str,
    intensity: str
) -> str:

    client = _client()

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a structured 7-day workout plan for:

Age: {age}
Weight: {weight}
Fitness goal: {goal}
Workout intensity: {intensity}

Requirements:
- Give Day 1 through Day 7.
- Include a warm-up of about 5-10 minutes.
- Include main exercises with sets/repetitions or duration.
- Include rest/recovery guidance.
- Match the requested intensity and goal.
- Include at least one recovery/rest-focused day where appropriate.
- Keep the plan practical and easy to follow.
- Do not claim to diagnose or treat medical conditions.
- If the user has an injury, medical condition, or concerning symptoms,
  advise professional guidance.

Use clear headings and plain text.
Do not use markdown tables.
"""

    # If Gemini is not available, use demo plan
    if client is None:
        print("Gemini client unavailable. Using demo workout.")
        return _demo_plan(goal, intensity)

    model = os.getenv(
        "GEMINI_WORKOUT_MODEL",
        "gemini-3.8-flash"
    )

    # Retry Gemini when temporary 503 errors occur
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:
            print(
                f"Gemini workout request: attempt "
                f"{attempt}/{max_attempts}"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )

            if response and response.text:
                print("Gemini workout generated successfully.")
                return response.text.strip()

            print("Gemini returned an empty response.")

        except ServerError as e:

            print(f"Gemini server error on attempt {attempt}: {e}")

            if attempt < max_attempts:
                wait_time = 2 ** attempt
                print(
                    f"Retrying Gemini in {wait_time} seconds..."
                )
                time.sleep(wait_time)
            else:
                print(
                    "Gemini is currently unavailable. "
                    "Using demo workout."
                )

        except Exception as e:

            print(f"Gemini error: {e}")

            # Don't crash the entire website
            print("Using demo workout instead.")
            break

    return _demo_plan(goal, intensity)


def _demo_plan(goal: str, intensity: str) -> str:

    return f"""
DEMO MODE — Gemini temporarily unavailable

Goal: {goal}
Intensity: {intensity}

Day 1 — Full Body
Warm-up: 5-10 minutes brisk walking and mobility.
Main workout:
- Squats 3 x 10
- Push-ups 3 x 8-12
- Rows 3 x 10
- Plank 3 x 30 seconds

Cooldown: 5 minutes easy stretching.

Day 2 — Cardio
Warm-up: 5 minutes easy movement.
Main workout: 20-30 minutes moderate cardio.
Cooldown: 5 minutes walking and stretching.

Day 3 — Lower Body
Warm-up: 5-10 minutes.
Main workout:
- Lunges 3 x 10 per side
- Glute bridges 3 x 12
- Calf raises 3 x 15

Cooldown: Lower-body stretching.

Day 4 — Recovery
Light walking, mobility work, and gentle stretching.

Day 5 — Upper Body
Warm-up: 5-10 minutes.
Main workout:
- Push-ups 3 x 8-12
- Rows 3 x 10
- Shoulder press 3 x 10
- Plank 3 x 30 seconds

Cooldown: 5 minutes stretching.

Day 6 — Cardio + Core
Warm-up: 5 minutes.
Main workout:
- 20 minutes cardio
- Dead bugs 3 x 10
- Side plank 3 x 20 seconds per side

Cooldown: Easy walking and stretching.

Day 7 — Rest / Active Recovery
Gentle walking and mobility as comfortable.

Note:
This is fallback demonstration content.
Gemini will be used automatically when the API is available.
"""