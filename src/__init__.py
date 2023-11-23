from datetime import datetime

import pandas as pd
from flask import Flask, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_restx import Resource, Api
from pymongo.collection import Collection

from .model import Stock
from .stock_ranker import StockRanker

# Configure Flask & Flask-PyMongo:
app = Flask(__name__)
# allow access from any frontend
cors = CORS()
cors.init_app(app, resources={r"*": {"origins": "*"}})
# add your mongodb URI
app.config["MONGO_URI"] = "mongodb://localhost:27017/stocks"
pymongo = PyMongo(app)
# Get a reference to the stocks collection.
stocks: Collection = pymongo.db.stocks
api = Api(app)


class StockList(Resource):
    def get(self):
        start_date = request.args.get('start_date', '1900-01-01')
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        cursor = stocks.find({"date": {"$gte": start_date, "$lte": end_date}})
        return [Stock(**doc).to_json() for doc in cursor]


class StockFeatures(Resource):
    def get(self):
        # Retrieve all field names from the Stock model
        fields = Stock.schema()['properties'].keys()
        feature_names = [field for field in fields if field not in ['symbol', 'date', '_id']]
        return {'features': feature_names}


class DateRange(Resource):
    def get(self):
        min_date = stocks.find_one(sort=[("date", 1)])["date"]
        max_date = stocks.find_one(sort=[("date", -1)])["date"]

        return {"min_date": min_date.isoformat(), "max_date": max_date.isoformat()}


class RankStocks(Resource):
    def post(self):
        data = request.get_json()
        selected_features = data.get('selectedFeatures', [])
        start_date = data.get('startDate', '1900-01-01')
        end_date = data.get('endDate', datetime.now().isoformat())
        decay_rate = data.get('decayRate', 0)
        decay_function = data.get('decayFunction', '')

        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        cursor = stocks.find({"date": {"$gte": start_date, "$lte": end_date}})
        stocks_df = pd.DataFrame(list(cursor))

        ranker = StockRanker(stocks_df, selected_features, decay_rate, decay_function)
        ranked_stocks_df = ranker.rank_stocks()

        ranked_stocks_json = ranked_stocks_df.to_json(orient='records', default_handler=str)
        return {"rankedStocks": ranked_stocks_json}


api.add_resource(DateRange, '/date-range')
api.add_resource(StockList, '/stocks')
api.add_resource(StockFeatures, '/stock-features')
api.add_resource(RankStocks, '/rank-stocks')
