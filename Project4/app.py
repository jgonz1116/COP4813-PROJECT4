import requests
import main_functions
from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField

app = Flask(__name__)
credentials = main_functions.read_from_file("JSON_Documents/credentials.json")
username = credentials["username"]
password = credentials["password"]
app.config["SECRET_KEY"] = "010296db"
app.config["MONGO_URI"] = "mongodb+srv://{0}:{1}@cluster0.rhhi3.mongodb.net/db?retryWrites=true&w=majority".format(
    username, password)
mongo = PyMongo(app)


class Expenses(FlaskForm):
    description = StringField('description')
    category = SelectField('category', choices=[('rent', 'Rent'),
                                                ('electricity', 'Electricity'),
                                                ('water', 'Water'),
                                                ('insurance', 'Insurance'),
                                                ('internet', 'Internet'),
                                                ('restaurants', 'Restaurants'),
                                                ('groceries', 'Groceries'),
                                                ('gas', 'Gas'),
                                                ('college', 'College'),
                                                ('party', 'Party'),
                                                ('mortgage', 'Mortgage')])
    cost = DecimalField('cost', places=2)
    currency = SelectField('currency', choices=[('USD', 'US Dollar'),
                                                ('BRL', 'Brazilian Real'),
                                                ('BTC', 'Bitcoin'),
                                                ('CAD', 'Canadian Dollar'),
                                                ('COP', 'Colombian Peso'),
                                                ('EUR', 'Euro'),
                                                ('GBP', 'British Pound Sterling')])
    date = DateField('date')


def get_total_expenses(category):
    total_expenses = 0
    all_category = mongo.db.expenses.find({"category": category})
    for i in all_category:
        total_expenses += float(i["cost"])
    return total_expenses


@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])
    expensesByCategory = [
        ("rent", get_total_expenses("rent")),
        ("electricity", get_total_expenses("electricity")),
        ("water", get_total_expenses("water")),
        ("insurance", get_total_expenses("insurance")),
        ("internet", get_total_expenses("internet")),
        ("restaurants", get_total_expenses("restaurants")),
        ("groceries", get_total_expenses("groceries")),
        ("gas", get_total_expenses("gas")),
        ("college", get_total_expenses("college")),
        ("party", get_total_expenses("party")),
        ("mortgage", get_total_expenses("mortgage"))
    ]
    # expensesByCategory is a list of tuples
    # each tuple has two elements:
    ## a string containing the category label, for example, insurance
    ## the total cost of this category
    dict(expensesByCategory)
    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses', methods=["GET", "POST"])
def addExpenses():
    expensesForm = Expenses(request.form)
    if request.method == "POST":
        description = request.form['description']
        category = request.form['category']
        cost = request.form['cost']
        currency = request.form['currency']
        date = request.form['date']
        converted_cost = currency_converter(cost, currency)
        # INSERT ONE DOCUMENT TO THE DATABASE
        # CONTAINING THE DATA LOGGED BY THE USER
        # REMEMBER THAT IT SHOULD BE A PYTHON DICTIONARY
        newExpense = {"description": description,
                      "category": category,
                      "cost": converted_cost,
                      "date": date}
        mongo.db.expenses.insert_one(newExpense)
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)

def currency_converter(cost,currency):
    float_cost = float(cost)
    url = "http://api.currencylayer.com/live?access_key=37a47b066cccdff362e4e654150c43fd"
    response = requests.get(url).json()
    main_functions.save_to_file(response, "JSON_Documents/response.json")
    currencies = main_functions.read_from_file("JSON_Documents/response.json")
    if currency != 'USD':
        float_cost = float(cost) / float(currencies["quotes"]["USD" + currency])
    converted_cost = "{:.2f}".format(float_cost)
    return converted_cost

app.run()