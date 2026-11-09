import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

pending_codes = {}

SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "alisharred001@gmail.com"
SMTP_PASS = "xsmtpsib-8bd3b520f419d94b21b4ee03bd4ba38ff79e5a8a0f4df0d32c0811cd4cc87a8f-T9DoXiV1jsVnpwwV"
SENDER_EMAIL = "synapse.edu.portal@gmail.com"


@app.route("/api/send-code", methods=["POST"])
def send_code():
  data = request.json
  email = data.get("email")
  if not email:
    return jsonify({"success": False, "error": "Email is required"}), 400

  code = str(random.randint(100000, 999999))
  pending_codes[email] = code

  try:
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = email
    msg["Subject"] = f"{code} is your Synapse verification code"

    body = (
        f"Your 6-digit verification code for Synapse is: {code}\nIt expires in"
        " 10 minutes."
    )
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(SENDER_EMAIL, email, msg.as_string())
    server.quit()

    return jsonify({"success": True})
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/verify-code", methods=["POST"])
def verify_code():
  data = request.json
  email = data.get("email")
  code = data.get("code")

  if not email or not code:
    return (
        jsonify(
            {"success": False, "valid": False, "error": "Email and code required"}
        ),
        400,
    )

  stored_code = pending_codes.get(email)

  is_valid = bool(stored_code and stored_code == code)

  if is_valid:
    del pending_codes[email]  # Clear code once successfully used

  return jsonify({"success": True, "valid": is_valid})


if __name__ == "__main__":
  app.run(port=5000, debug=True)