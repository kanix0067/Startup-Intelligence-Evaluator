from pydantic import BaseModel
from typing import Optional

class StartupInput(BaseModel):
    startup_idea: str
    problem: str
    target_customer: str
    industry: str
    location: str
    budget: Optional[float] = None
    target_market: Optional[str] = None
    additional_information: Optional[str] = None