from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_restx import Resource, Api
from pymongo.collection import Collection

from .model import Stock

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


api.add_resource(StockList, '/stocks')
api.add_resource(StockFeatures, '/stock-features')
