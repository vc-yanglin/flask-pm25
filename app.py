from flask import Flask, render_template
from datetime import datetime
import pandas as pd
import pymysql

app = Flask(__name__)


@app.route("/")
def index():
    # return f"<h1>Hello World!</h1><br>{datetime.now()}"
    username = "Victor"
    nowtime = datetime.now().strftime("%Y-%m-%d")

    return render_template("index.html", name=username, now=nowtime)


@app.route("/pm25")
def get_pm25_data():
    api_url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=CSV"
    df = pd.read_csv(api_url)
    df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
    df1 = df.dropna()
    return df1.values.tolist()


app.run(debug=True)
