from fastapi import FastAPI
import mysql.connector

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}

@app.get("/db-check")
def db_check():
    try:
        conn = mysql.connector.connect(
            host="172.21.160.1",
            user="odiman",
            password="Ethan@2021",
            database="myproject_db"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        conn.close()
        return {"db_time": result[0].isoformat()}
    except Exception as e:
        return {"error": str(e)}
