from flask import Flask, render_template, request, redirect, url_for, session, flash
import smtplib, random, time
from config import SENDER_EMAIL, EMAIL_PASSWORD, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Store OTP and timestamp
otp_store = {}

# Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        # Dummy credentials
        if username == "admin" and password == "admin123":
            otp = str(random.randint(100000, 999999))
            otp_store[email] = {"otp": otp, "time": time.time()}
            session["email"] = email

            subject = "Your OTP for Login"
            body = f"Your OTP is: {otp}\n(Valid for 2 minutes)"
            message = f"Subject: {subject}\n\n{body}"

            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(SENDER_EMAIL, EMAIL_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, message)
                server.quit()
                flash("OTP has been sent to your email.", "info")
                return redirect(url_for("otp_verify"))
            except Exception as e:
                return render_template("error.html", msg=str(e))
        else:
            flash("Invalid Username or Password", "danger")
    return render_template("login.html")

# OTP Page
@app.route("/otp", methods=["GET", "POST"])
def otp_verify():
    if request.method == "POST":
        entered_otp = request.form["otp"]
        email = session.get("email")

        if email in otp_store:
            saved_otp = otp_store[email]["otp"]
            otp_time = otp_store[email]["time"]

            # Check OTP expiry (2 minutes)
            if time.time() - otp_time > 120:
                flash("OTP expired. Please login again.", "warning")
                return redirect(url_for("login"))

            if entered_otp == saved_otp:
                session["logged_in"] = True
                return redirect(url_for("success"))
            else:
                flash("Invalid OTP. Try again.", "danger")
    return render_template("otp.html")

# Success Page
@app.route("/success")
def success():
    if session.get("logged_in"):
        return render_template("success.html", email=session.get("email"))
    else:
        return redirect(url_for("login"))

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# Error Page
@app.route("/error")
def error():
    return render_template("error.html", msg="Something went wrong.")

if __name__ == "__main__":
    app.run(debug=True)
