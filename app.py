from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
import pymysql
from pm25 import get_pm25_data_from_mysql, update_db
import json

app = Flask(__name__)

books = {1: "Python book", 2: "Java book", 3: "Flask book"}


@app.route("/")
def index():
    columns, datas = get_pm25_data_from_mysql()
    df = pd.DataFrame(datas, columns=columns)
    counties = sorted(df["county"].unique().tolist())
    print(counties)

    county = request.args.get("county", "ALL")
    columns, datas = get_pm25_data_from_mysql()
    df = pd.DataFrame(datas, columns=columns)

    if county != "ALL":
        df = df.groupby("county").get_group(county)
        columns = df.columns.tolist()
        datas = df.values.tolist()
        print(df)

    x_data = df["site"].to_list()
    y_data = df["pm25"].to_list()

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


@app.route("/books")
def book_page():
    # return f"<h1>Hello World!</h1><br>{datetime.now()}"
    sw = 1
    if sw:
        books = [
            {
                "name": "Python book",
                "price": 299,
                "image_url": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/CN1/136/11/CN11361197.jpg&v=58096f9ck&w=348&h=348",
            },
            {
                "name": "Java book",
                "price": 399,
                "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/087/31/0010873110.jpg&v=5f7c475bk&w=348&h=348",
            },
            {
                "name": "C# book",
                "price": 499,
                "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/036/04/0010360466.jpg&v=62d695bak&w=348&h=348",
            },
        ]
    else:
        books = []

    for book in books:
        print(book["name"])
        print(book["price"])
        print(book["image_url"])

    username = "Victor"
    nowtime = datetime.now().strftime("%Y-%m-%d")

    return render_template("books.html", **locals())


### @app.route("/filter", methods=["POST"]
###    county = request.form.get("county")
@app.route("/filter")
def filter_data():
    county = request.args.get("county")
    columns, datas = get_pm25_data_from_mysql()
    df = pd.DataFrame(datas, columns=columns)
    df1 = df.groupby("county").get_group(county).groupby("site")["pm25"].mean().round(2)
    print(df1)
    return {"county": county}


@app.route("/update-db")
def update_pm25_db():
    count, message = update_db()
    nowtime = datetime.now().strftime("%Y-%m-%d")
    result = json.dumps(
        {"時間": nowtime, "更新筆數": count, "結果": message}, ensure_ascii=False
    )
    return result


@app.route("/pm25")
def get_pm25_data():
    api_url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=CSV"
    df = pd.read_csv(api_url)
    df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
    df1 = df.dropna()
    return df1.values.tolist()


@app.route("/bmi")
def get_bmi():
    height = request.args.get("height")
    weight = request.args.get("weight")

    bmi = round(eval(weight) / (eval(height) / 100) ** 2, 2)
    print(bmi)
    return render_template(
        "bmi.html", bmi={"height": height, "weight": weight, "bmi": bmi}
    )


if __name__ == "__main__":
    app.run(debug=True)
