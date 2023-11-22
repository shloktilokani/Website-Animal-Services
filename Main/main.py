from flask import *
import mysql.connector
from flask_mail import *
from random import *
import password

app = Flask(__name__)
mail = Mail(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = password.Email
app.config[
    "MAIL_PASSWORD"
] = password.passwd  # you have to give your password of gmail account
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)
otp = randint(000000, 999999)
# MySQL database configuration
# 123
db = mysql.connector.connect(
    host="localhost", user="root", password="", database="petservice"
)

cursor = db.cursor()
table = "appointmentdb"


@app.route("/", methods=["GET", "POST"])
def mainpage():
    return render_template("mainpage.html")


@app.route("/tip", methods=["GET", "POST"])
def tip():
    return render_template("tip.html")


user = None
Date = None
Fullname = None
phn = None
service = None
email = None
time = None


@app.route("/About", methods=["GET", "POST"])
def About():
    return render_template("About.html")


@app.route("/services", methods=["GET", "POST"])
def services():
    return render_template("Services.html")


@app.route("/verify", methods=["POST"])
def verify():
    if request.method == "POST":
        global Fullname
        Fullname = request.form["fullname"]
        global email
        email = request.form["email"]
        global phn
        phn = request.form["phone"]
        global options
        options = request.form.getlist("services")
        global service
        service = ", ".join(options)
        global Date
        Date = request.form["date"]
        global time
        time = request.form["slot"]
    msg = Message(subject="OTP", sender="furryaavjo@gmail.com", recipients=[email])
    msg.body = str(otp)
    mail.send(msg)
    return render_template("verify.html")


@app.route("/validate", methods=["GET", "POST"])
def validate():
    # TODO : Add an alert box that says "Email has been send please check"
    user_otp = request.form["otp"]
    if otp == int(user_otp):
        message = "OTP verified \n", "Your appointment has been booked..."
        insert_query = (
            "INSERT INTO petservice.appointmentdb (date, time, full_name, phone, services, email) VALUES (%s, %s, "
            "%s, %s, %s,%s)"
        )
        cursor.execute(insert_query, (Date, time, Fullname, phn, service, email))
        db.commit()
        msg = Message(
            subject="Appointmet Confirmation",
            sender="furryaavjo@gmail.com",
            recipients=[email],
        )
        msg.body = (
            f"Thanks {Fullname} for using our portal.\n"
            f"Your appointment has been booked for {Date} at {time} hours. \n"
            f"Services availed : {service}.\n"
            f"For any queries please contact us on 1234567890"
        )
        mail.send(msg)
        return redirect("/services")
    else:
        message = "Please try again"
    return render_template("verify.html", message=message)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    global user
    if user == None:
        if request.method == "POST":
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]

                # Validate user login
                select_query = "SELECT * FROM petservice.admindb WHERE user_id = %s AND password = %s"
                cursor.execute(select_query, (username, password))
                user = cursor.fetchone()
                if user:
                    return redirect("/index")
                else:
                    return "Invalid username or password. Please try again."
        return render_template("admin.html")
    else:
        return redirect("/index")


# TODO: Send Email on validation
@app.route("/index", methods=["GET", "POST"])
def index():
    if user:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table} ORDER BY time")
        data = cursor.fetchall()
        return render_template("index.html", data=data)
    else:
        return redirect("/admin")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        # Handle form submission, update the record in the database
        date = request.form.get("date")
        time = request.form.get("time")
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE appoint_id = %s", (id,))
        record = cursor.fetchone()
        appointId = record[0]
        email = record[6]
        fname = record[3]
        services = record[5]
        reason = request.form["reason"]
        try:
            cursor.execute(
                f"UPDATE {table} SET date=%s, time=%s WHERE appoint_id=%s",
                (date, time, id),
            )
            db.commit()
            msg = Message(
                subject="Appointment Rescheduled",
                sender="furryaavjo@gmail.com",
                recipients=[email],
            )
            msg.body = (
                f"Appointment ID : {appointId}\n"
                f"Services : {services}\n\n"
                f"Dear {fname},\n"
                f"This is to inform you that your appointment for the services has been rescheduled to : \n"
                f"Date : {date}\n"
                f"Time : {time}\n"
                f"Reason : {reason}\n\n"
                f"We are extremely sorry for the inconvenience.\n"
                f"For any queries please contact us on 1234567890"
            )
            mail.send(msg)
            return redirect("/index")
        except mysql.connector.Error as err:
            # Handle database errors, log or display an error message
            pass
    else:
        # Fetch the record to be edited
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE appoint_id = %s", (id,))
        record = cursor.fetchone()

        if record:
            return render_template("edit.html", record=record)
        else:
            # Handle record not found, e.g., redirect to an error page
            pass


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    if request.method == "POST":
        reason = request.form["reason"]
        try:
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE appoint_id = %s", (id,))
            record = cursor.fetchone()
            appointId = record[0]
            date = record[1]
            time = record[2]
            email = record[6]
            fname = record[3]
            services = record[5]

            cursor.execute(
                f"DELETE FROM {table} WHERE appoint_id = %s",
                (id,),
            )
            db.commit()
            msg = Message(
                subject="Appointment Cancelled",
                sender="furryaavjo@gmail.com",
                recipients=[email],
            )
            msg.body = (
                f"Appointment ID : {appointId}\n"
                f"Services : {services}\n\n"
                f"Dear {fname},\n"
                f"This is to inform you that your appointment dated {date} at {time} has been CANCELED.\n"
                f"Reason : {reason}\n\n"
                f"We are extremely sorry for the inconvenience.\n"
                f"For any queries please contact us on 1234567890"
            )
            mail.send(msg)
            return redirect("/index")
        except mysql.connector.Error as err:
            # Handle database errors, log or display an error message
            pass
    else:
        # Fetch the record to be edited
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE appoint_id = %s", (id,))
        record = cursor.fetchone()

        if record:
            return render_template("delete.html", record=record)
        else:
            # Handle record not found, e.g., redirect to an error page
            pass


@app.route("/logout", methods=["POST"])
def logout():
    global user  # Assuming "user" is the variable that tracks the logged-in user.
    user = None  # Clear the user session.
    return redirect("/admin")


# TODO User Payment Cancellation using unique key

if __name__ == "__main__":
    app.run(debug=True)
