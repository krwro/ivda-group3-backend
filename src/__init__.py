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
        cursor = stocks.find()
        return [Stock(**doc).to_json() for doc in cursor]


class StockFeatures(Resource):
    def get(self):
        # Retrieve all field names from the Stock model
        fields = Stock.schema()['properties'].keys()
        feature_names = [field for field in fields if field not in ['symbol', 'date', '_id']]
        return {'features': feature_names}


class RankStocks(Resource):
    def post(self):
        data = request.get_json()
        selected_features = data.get('selectedFeatures', [])

        cursor = stocks.find()
        stocks_df = pd.DataFrame(list(cursor))

        ranker = StockRanker(stocks_df, selected_features)

        ranked_stocks_df = ranker.rank_stocks()

        ranked_stocks_json = ranked_stocks_df.to_json(orient='records', default_handler=str)
        return {"rankedStocks": ranked_stocks_json}


api.add_resource(StockList, '/stocks')
api.add_resource(StockFeatures, '/stock-features')
api.add_resource(RankStocks, '/rank-stocks')
