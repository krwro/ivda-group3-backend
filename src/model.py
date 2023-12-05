from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Stock(BaseModel):
    _id: str
    date: datetime
    symbol: str

    price: Optional[float] = None
    F1_price: Optional[float] = None
    F2_price: Optional[float] = None

    grossProfitMargin: Optional[float] = None
    eps: Optional[float] = None
    dividendYield: Optional[float] = None
    grahamNumber: Optional[float] = None
    cashFlowToDebtRatio: Optional[float] = None
    operatingCashFlowPerShare: Optional[float] = None
    returnOnAssets: Optional[float] = None
    roe: Optional[float] = None
    debtEquityRatio: Optional[float] = None

    revenue: Optional[float] = None
    F1_revenue: Optional[float] = None
    F2_revenue: Optional[float] = None

    netIncome: Optional[float] = None
    F1_netIncome: Optional[float] = None
    F2_netIncome: Optional[float] = None

    grossProfit: Optional[float] = None
    F1_grossProfit: Optional[float] = None
    F2_grossProfit: Optional[float] = None

    interestCoverage: Optional[float] = None
    F1_interestCoverage: Optional[float] = None
    F2_interestCoverage: Optional[float] = None

    operatingIncome: Optional[float] = None
    F1_operatingIncome: Optional[float] = None
    F2_operatingIncome: Optional[float] = None

    bookValuePerShare: Optional[float] = None
    F1_bookValuePerShare: Optional[float] = None
    F2_bookValuePerShare: Optional[float] = None

    tangibleAssetValue: Optional[float] = None
    F1_tangibleAssetValue: Optional[float] = None
    F2_tangibleAssetValue: Optional[float] = None

    workingCapital: Optional[float] = None
    F1_workingCapital: Optional[float] = None
    F2_workingCapital: Optional[float] = None

    priceToSalesRatio: Optional[float] = None
    F1_priceToSalesRatio: Optional[float] = None
    F2_priceToSalesRatio: Optional[float] = None


    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)
