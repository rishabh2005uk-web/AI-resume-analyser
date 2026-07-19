from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
import models
import PyPDF2
import docx
import json

# IMPORTANT: Make sure this matches the name of the file where analyze_resume is saved!
from ai import analyze_resume 

app = Flask(__name__)
app.secret_key = "secret123"

Base.metadata.create_all(bind=engine)

# HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

# ---- Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            return "user already exist"
        
        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()

        return redirect("/login")
    
    return render_template("signup.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.User).filter_by(email=email, password=password).first()

        if user:
            session["user"] = user.email
            return redirect("/dashboard")
        else:
            return "Invalid credentials"
        
    return render_template("login.html")

# Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")

        # File handling
        if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}
            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Docx error: {str(e)}"}

        if resume_text and user_goal:
            try:
                result = analyze_resume(resume_text, user_goal)

                # Save to db
                db = SessionLocal()
                user = db.query(models.User).filter_by(email=session["user"]).first()

                report = models.Report(
                    user_id=user.id,
                    resume_text=resume_text,
                    results=json.dumps(result)
                )

                db.add(report)
                db.commit()

            except Exception as e:
                result = {"error": f"AI error: {str(e)}"}
                
    # This return is now correctly indented outside the POST block
    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )

# History
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()

    reports = db.query(models.Report).filter_by(user_id=user.id).all()
    
    # Convert JSON string > dict
    parsed_reports = []
    for r in reports:
        try:
            parsed_result = json.loads(r.results)
        except:
            parsed_result = []

        parsed_reports.append({
            "resume": r.resume_text,
            "result": parsed_result
        })

    return render_template("history.html", reports=parsed_reports) 

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)