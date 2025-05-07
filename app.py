from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
import pymysql
from pm25 import (
    get_pm25_data_from_mysql,
    update_db,
    get_pm25_data_by_site,
    get_all_counties,
    get_site_by_counties,
)
import json

app = Flask(__name__)


@app.route("/")
def index():
    columns, datas = get_pm25_data_from_mysql()
    df = pd.DataFrame(datas, columns=columns)
    counties = sorted(df["county"].unique().tolist())
    print(counties)

    county = request.args.get("county", "ALL")
    columns, datas = get_pm25_data_from_mysql()
    df = pd.DataFrame(datas, columns=columns)

    if county == "ALL":
        df1 = df.groupby("county")["pm25"].mean().reset_index()
        x_data = df1["county"].to_list()
    else:
        df = df.groupby("county").get_group(county)
        x_data = df["site"].to_list()

    y_data = df["pm25"].to_list()
    columns = df.columns.tolist()
    datas = df.values.tolist()

    return render_template(
        "index.html",
        columns=columns,
        datas=datas,
        counties=counties,
        selected_county=county,
        x_data=x_data,
        y_data=y_data,
    )


# return render_template("index.html", **locals())
# @app.route("/filter", methods=["POST"]
#    county = request.form.get("county")
@app.route("/pm25-data-site")
def pm25_data_by_site():
    county = request.args.get("county")
    site = request.args.get("site")
    if not county or not site:
        result = json.dumps({"error": "城市跟站點名稱不能為空!"}, ensure_ascii=False)
    else:
        columns, datas = get_pm25_data_by_site(county, site)
        df = pd.DataFrame(datas, columns=columns)

        result = {
            "county": county,
            "site": site,
            "x_data": df["datacreationdate"].to_list(),
            "y_data": df["pm25"].to_list(),
            "higher": df["pm25"].max(),
            "lower": df["pm25"].min(),
        }
    return result


@app.route("/pm25-county-site")
def pm25_county_site():
    county = request.args.get("county")
    sites = get_site_by_counties(county)
    result = json.dumps(sites, ensure_ascii=False)
    return result


@app.route("/update-db")
def update_pm25_db():
    count, message = update_db()
    nowtime = datetime.now().strftime("%Y-%m-%d")
    result = json.dumps(
        {"時間": nowtime, "更新筆數": count, "結果": message}, ensure_ascii=False
    )
    return result


@app.route("/pm25-site")
def pm25_site():
    counties = get_all_counties()
    return render_template("pm25-site.html", counties=counties)


if __name__ == "__main__":
    app.run(debug=True)
