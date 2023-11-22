from datetime import datetime
from flask import *
import mysql.connector

app = Flask(__name__)

# MySQL database configuration
db = mysql.connector.connect(
    host="localhost", user="root", password="", database="petservice"
)

cursor = db.cursor()


@app.route("/", methods=["GET", "POST"])
def mainpage():
    return render_template("mainpage.html")


@app.route("/tip", methods=["GET", "POST"])
def tip():
    return render_template("tip.html")


user = None


@app.route("/About", methods=["GET", "POST"])
def About():
    return render_template("About.html")


@app.route("/services", methods=["GET", "POST"])
def services():
    if request.method == "POST":
        Fullname = request.form["fullname"]
        email = request.form["email"]
        phn = request.form["phone"]
        options = request.form.getlist("services")
        service = ", ".join(options)
        date = request.form["date"]
        time = request.form["slot"]

        insert_query = (
            "INSERT INTO petservice.appointmentdb(date, time, full_name, phone, services, email) VALUES (%s, %s, "
            "%s, %s, %s, %s)"
        )
        cursor.execute(insert_query, (date, time, Fullname, phn, service, email))
        db.commit()

    return render_template("Services.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
