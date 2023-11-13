from statistics import mean, median

from flask import Flask
from flask import request
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_restx import Resource, Api
from pymongo.collection import Collection

from .model import Company

# Configure Flask & Flask-PyMongo:
app = Flask(__name__)
# allow access from any frontend
cors = CORS()
cors.init_app(app, resources={r"*": {"origins": "*"}})
# add your mongodb URI
app.config["MONGO_URI"] = "mongodb://localhost:27017/companiesdatabase"
pymongo = PyMongo(app)
# Get a reference to the companies collection.
companies: Collection = pymongo.db.companies
categories = set([company.get("category") for company in companies.find()])
employeesInCategory = {}
for company in companies.find():
    if employeesInCategory.get(company.get("category")) is None:
        employeesInCategory[company.get("category")] = [company.get("employees")]
    else:
        employeesInCategory[company.get("category")].append(company.get("employees"))

averageEmployeesInCategory = {}
medianEmployeesInCategory = {}
for category in categories:
    averageEmployeesInCategory[category] = mean(employeesInCategory.get(category))
    medianEmployeesInCategory[category] = median(employeesInCategory.get(category))

for company in companies.find():
    company["average_employees_in_category"] = averageEmployeesInCategory.get(company.get("category"))
    company["median_employees_in_category"] = medianEmployeesInCategory.get(company.get("category"))
    pymongo.db.companies.update_one({"_id": company["_id"]},
                                    {"$set": {"average_employees_in_category": averageEmployeesInCategory.get(
                                        company.get("category"))}})
    pymongo.db.companies.update_one({"_id": company["_id"]},
                                    {"$set": {"median_employees_in_category": medianEmployeesInCategory.get(
                                        company.get("category"))}})

api = Api(app)


class CompaniesList(Resource):
    def get(self, args=None):
        # retrieve the arguments and convert to a dict
        args = request.args.to_dict()
        # If the user specified category is "All" we retrieve all companies
        if args['category'] == 'All':
            cursor = companies.find()
        # In any other case, we only return the companies where the category applies
        else:
            cursor = companies.find(args)
        # we return all companies as json
        return [Company(**doc).to_json() for doc in cursor]


class Companies(Resource):
    def get(self, id):
        import pandas as pd
        from statsmodels.tsa.ar_model import AutoReg
        # search for the company by ID
        cursor = companies.find_one_or_404({"id": id})
        company = Company(**cursor)
        # retrieve args
        args = request.args.to_dict()
        # retrieve the profit
        profit = company.profit
        # add to df
        profit_df = pd.DataFrame(profit).iloc[::-1]
        if args['algorithm'] == 'random':
            # retrieve the profit value from 2021
            prediction_value = int(profit_df["value"].iloc[-1])
            # add the value to profit list at position 0
            company.profit.insert(0, {'year': 2022, 'value': prediction_value})
        elif args['algorithm'] == 'regression':
            # create model
            model_ag = AutoReg(endog=profit_df['value'], lags=1, trend='c', seasonal=False, exog=None, hold_back=None,
                               period=None, missing='none')
            # train the model
            fit_ag = model_ag.fit()
            # predict for 2022 based on the profit data
            prediction_value = fit_ag.predict(start=len(profit_df), end=len(profit_df), dynamic=False).values[0]
            # add the value to profit list at position 0
            company.profit.insert(0, {'year': 2022, 'value': prediction_value})
        return company.to_json()


api.add_resource(CompaniesList, '/companies')
api.add_resource(Companies, '/companies/<int:id>')
