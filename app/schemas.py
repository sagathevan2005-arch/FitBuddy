from pydantic import BaseModel, Field


class UserInput(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: str = Field(min_length=1, max_length=30)
    goal: str = Field(min_length=1, max_length=100)
    intensity: str = Field(pattern="^(low|medium|high)$")


class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str = Field(min_length=1, max_length=2000)
