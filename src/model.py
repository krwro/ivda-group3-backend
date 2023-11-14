from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Stock(BaseModel):
    _id: str
    date: datetime
    price: float
    symbol: str
    revenue: Optional[float] = None
    netIncome: Optional[float] = None
    eps: Optional[float] = None
    roe: Optional[float] = None
    roic: Optional[float] = None
    debtEquityRatio: Optional[float] = None
    F1_price: Optional[float] = None
    F2_price: Optional[float] = None
    F1_netIncome: Optional[float] = None
    F2_netIncome: Optional[float] = None

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)
