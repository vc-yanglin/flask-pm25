import pandas as pd
import pymysql


def get_site_by_counties(county):
    conn = None
    sites = []
    try:
        conn = open_db()
        cur = conn.cursor()
        sqlstr = "select distinct site from pm25 where county=%s;"
        cur.execute(sqlstr, (county,))
        datas = cur.fetchall()

        sites = [data[0] for data in datas]

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
    return sites


def get_all_counties():
    conn = None
    counties = []
    try:
        conn = open_db()
        cur = conn.cursor()
        sqlstr = "select distinct county from pm25;"
        cur.execute(sqlstr)
        datas = cur.fetchall()

        counties = [data[0] for data in datas]

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
    return counties


def open_db():
    conn = None
    try:
        conn = pymysql.connect(
            host="127.0.0.1", port=3306, user="root", password="12345678", db="demo"
        )
    except Exception as e:
        print("資料庫開啟失敗", e)
    return conn


def get_pm25_data_by_site(county, site):
    conn = None
    columns, datas = None, None
    try:
        conn = open_db()
        cur = conn.cursor()
        sqlstr = "select * from pm25 where county=%s and site=%s;"
        cur.execute(sqlstr, (county, site))
        print(cur.description)
        columns = [col[0] for col in cur.description]
        datas = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
    return columns, datas


def get_pm25_data_from_mysql():
    conn = None
    columns, datas = None, None
    try:
        conn = open_db()
        cur = conn.cursor()
        sqlstr = "select * from pm25 where datacreationdate=(select MAX(datacreationdate) from pm25);"

        cur.execute(sqlstr)
        print(cur.description)
        columns = [col[0] for col in cur.description]
        datas = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
    return columns, datas


def update_db():
    api_url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=CSV"
    sqlstr = """
    insert ignore into pm25(site,county,pm25,datacreationdate,itemunit) 
    values(%s,%s,%s,%s,%s)
    """

    row_count = 0
    message = []
    try:
        df = pd.read_csv(api_url)
        df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
        df1 = df.dropna()
        values = df1.values.tolist()
        conn = open_db()
        cur = conn.cursor()
        cur.executemany(sqlstr, values)
        row_count = cur.rowcount
        conn.commit()
        print(f"更新{row_count}筆資料成功")
        message = "更新資料庫成功"

    except Exception as e:
        print(e)
        message = "更新資料庫失敗"

    finally:
        if conn is not None:
            conn.close()
    return row_count, message


if __name__ == "__main__":
    # update_db()
    # print(get_pm25_data_by_site("新北市", "富貴角"))
    print(get_all_counties())
