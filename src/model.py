from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Company(BaseModel):
        id: int
        name: str
        category: str
        founding_year: int
        employees: int
        profit: List
        average_employees_in_category: float
        median_employees_in_category: float

        def to_json(self):
                return jsonable_encoder(self, exclude_none=True)
