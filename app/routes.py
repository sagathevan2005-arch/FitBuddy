from pathlib import Path

from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import User, Plan
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan


# Create database tables
Base.metadata.create_all(bind=engine)

router = APIRouter()

# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Templates folder
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# ---------------------------------------------------------
# GENERATE WORKOUT
# ---------------------------------------------------------
@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: str = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):

    # Find existing user
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    # Update existing user
    if user:
        user.name = name
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity

    # Create new user
    else:
        user = User(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        db.add(user)

    db.commit()
    db.refresh(user)

    # Generate AI workout plan
    workout_plan = generate_workout_gemini(
        age,
        weight,
        goal,
        intensity
    )

    # Generate nutrition tip
    nutrition_tip = generate_nutrition_tip_with_flash(
        goal
    )

    # Save plan
    plan = Plan(
        user_id=user.id,
        original_plan=workout_plan,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    # Show result page
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "user": user,
            "plan": plan,
            "message": None,
        }
    )


# ---------------------------------------------------------
# SUBMIT FEEDBACK
# ---------------------------------------------------------
@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):

    # Find user
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    # User not found
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": None,
                "plan": None,
                "message": "User ID not found.",
            }
        )

    # Find latest plan
    plan = (
        db.query(Plan)
        .filter(Plan.user_id == user.id)
        .order_by(Plan.id.desc())
        .first()
    )

    # No plan found
    if not plan:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": None,
                "message": "No workout plan found for this user.",
            }
        )

    # Use updated plan if available
    current_plan = (
        plan.updated_plan
        if plan.updated_plan
        else plan.original_plan
    )

    # Generate updated workout plan
    updated = update_workout_plan(
        current_plan,
        feedback
    )

    # Save feedback and updated plan
    plan.feedback = feedback
    plan.updated_plan = updated

    # Generate new nutrition tip
    plan.nutrition_tip = generate_nutrition_tip_with_flash(
        user.goal
    )

    db.commit()
    db.refresh(plan)

    # Display updated result
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "user": user,
            "plan": plan,
            "message": "Your workout plan has been updated successfully.",
        }
    )


# ---------------------------------------------------------
# VIEW ALL USERS
# ---------------------------------------------------------
@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .order_by(User.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "request": request,
            "users": users,
        }
    )


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------
@router.post("/delete-user/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user:
        db.delete(user)
        db.commit()

    return RedirectResponse(
        url="/view-all-users",
        status_code=303
    )