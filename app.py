from flask import Flask, render_template, request, redirect, flash, session, make_response, url_for, jsonify
import dbhelper, os
from dbhelper import get_student_by_username, update_student_profile
from werkzeug.utils import secure_filename
from PIL import Image  


app = Flask(__name__)
app.secret_key = "deluna"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def disable_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/")
def home():
    if "user" in session:
        return redirect("/student_dashboard")
    return redirect("/student_login")

# =============== STUDENT AREA ===================== STUDENT AREA ======================= STUDENT AREA ============= STUDENT AREA ===============



# LOGIN STUDENT
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = dbhelper.get_username(username)  

        if user and user[0]["password"] == password:
            session["user"] = username
            session['logged_in'] = True
            flash("Login successful!", "success")  
            return redirect("/student_dashboard")
        flash("Invalid username or password.", "danger") 
        return redirect("/student_login")

    return render_template("student_login.html")

# REGISTRATION
@app.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        idno = request.form["idno"]
        lastname = request.form["lastname"]
        firstname = request.form["firstname"]
        middlename = request.form["middlename"]
        course = request.form["course"]
        year_level = request.form["year_level"]
        email_address = request.form["email_address"]
        username = request.form["username"]
        password = request.form["password"]  
        success = dbhelper.register_user(lastname, firstname, middlename, course, year_level, email_address, username, password)  

        if success:
            flash("Registration successful! Please login.", "success")
            return redirect("/student_login")
        else:
            flash("Username already exists. Please try again with a different username.", "danger")

    return render_template("student_register.html")

# STUDENT DASBOARD
@app.route("/student_dashboard")
def student_dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect("/student_login")
    
    student_info = dbhelper.get_student_by_username(session["user"])

    if not student_info:
        flash("User not found!", "danger")
        return redirect("/student_login")

    return render_template("student_dashboard.html", student=student_info)



# EDIT_PROFILE
# @app.route('/edit_profile', methods=['GET', 'POST'])
# def edit_profile():
    
#     username = session.get('user')  
#     if not username:
#         flash("Please log in first.", "warning")
#         return redirect(url_for('student_login'))  

    
#     student = session.get('student_info')
#     if not student or student.get("username") != username:
#         student = get_student_by_username(username)
#         session['student_info'] = student  

#     if request.method == 'POST':
#         firstname = request.form['firstname']
#         lastname = request.form['lastname']
#         middlename = request.form['middlename']
#         course = request.form['course']
#         year_level = request.form['year_level']
#         email_address = request.form['email_address']
#         address = request.form['address']

#         profile_picture = student.get("profile_picture", "profile_picture.png")  

#         if 'profile_image' in request.files:
#             file = request.files['profile_image']
#             if file and file.filename:  
#                 filename = secure_filename(f"{username}_{file.filename}")  
#                 file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 file.save(file_path)
#                 profile_picture = filename  

#         success = update_student_profile(username, firstname, middlename, lastname, course,
#                                          year_level, email_address, address, profile_picture)

#         if success:
#             student.update({
#                 "firstname": firstname,
#                 "middlename": middlename,
#                 "lastname": lastname,
#                 "course": course,
#                 "year_level": year_level,
#                 "email_address": email_address,
#                 "address": address,
#                 "profile_picture": profile_picture
#             })
#             session['student_info'] = student  
            
#             flash('Profile updated successfully!', 'success')
#             return redirect(url_for('student_dashboard'))  
#         else:
#             flash('Failed to update profile.', 'danger')

#     return render_template('edit_profile.html', student=student)

# UPLOAD PROFILE PICTURE
@app.route("/upload_profile_picture", methods=["POST"])
def upload_profile_picture():
    if "user" not in session:
        return jsonify({"success": False, "message": "Please log in first."}), 403

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file selected."})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No selected file."})

    if file and allowed_file(file.filename):
        if file.content_length > 2 * 1024 * 1024:  
            return jsonify({"success": False, "message": "File size exceeds 2MB limit."})

        filename = secure_filename(f"{session['user']}_{file.filename}")
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Save and resize image
        image = Image.open(file)
        image.thumbnail((300, 300)) 
        image.save(file_path)

        # Update database
        dbhelper.update_profile_picture(session["user"], filename)

        # Update session
        session['student_info']['profile_picture'] = filename

        return jsonify({"success": True, "message": "Profile picture updated!", "image_filename": filename})

    return jsonify({"success": False, "message": "Invalid file type. Allowed: png, jpg, jpeg, gif"})

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    username = session.get('user')  
    if not username:
        flash("Please log in first.", "warning")
        return redirect(url_for('student_login'))  

    student = get_student_by_username(username)
    if not student:
        flash("User not found!", "danger")
        return redirect(url_for('student_login'))

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        middlename = request.form['middlename']
        course = request.form['course']
        year_level = request.form['year_level']
        email_address = request.form['email_address']
        address = request.form['address']

        # Default profile picture
        profile_picture = student.get("profile_picture", "def.png")  

        # Handle profile picture upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename:
                if file.content_length > 2 * 1024 * 1024:  # Limit 2MB
                    flash("File size exceeds 2MB limit.", "danger")
                    return redirect(url_for('edit_profile'))

                if allowed_file(file.filename):
                    filename = secure_filename(f"{username}_{file.filename}")
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Save and resize image
                    image = Image.open(file)
                    image.thumbnail((300, 300))
                    image.save(file_path)

                    profile_picture = filename  

        # Update student profile
        success = update_student_profile(username, firstname, middlename, lastname, course, 
                                         year_level, email_address, address, profile_picture)

        if success:
            session['student_info'] = {
                "firstname": firstname,
                "middlename": middlename,
                "lastname": lastname,
                "course": course,
                "year_level": year_level,
                "email_address": email_address,
                "address": address,
                "profile_picture": profile_picture
            }
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('edit_profile'))

        else:
            flash('Failed to update profile.', 'danger')

    return render_template('edit_profile.html', student=student)





# SAVE EDIT_PROFILE
@app.route('/save_profile', methods=['POST'])
def save_profile():
    username = session.get('user')
    if not username:
        return {"success": False, "message": "Please log in first."}, 403 

    student = session.get('student_info')
    if not student or student.get("username") != username:
        student = get_student_by_username(username)
        session['student_info'] = student  

    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    middlename = request.form.get('middlename')
    course = request.form.get('course')
    year_level = request.form.get('year_level')
    email_address = request.form.get('email_address')
    address = request.form.get('address')

    profile_picture = student.get("profile_picture", "profile_picture.png")
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename:
            filename = secure_filename(f"{username}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            profile_picture = filename  

    success = update_student_profile(username, firstname, middlename, lastname, course, 
                                     year_level, email_address, address, profile_picture)

    if success:
        student.update({
            "firstname": firstname,
            "middlename": middlename,
            "lastname": lastname,
            "course": course,
            "year_level": year_level,
            "email_address": email_address,
            "address": address,
            "profile_picture": profile_picture
        })
        session['student_info'] = student  

        return {"success": True, "message": "Profile saved successfully!"}

    return {"success": False, "message": "Failed to save profile."}, 500

# LOGOUT FOR STUDENTS
@app.route("/logout")
def logout():
    flash("Logout Successfully", "success")
    session.pop("user", None)
    return redirect("/student_login")

# =============== STAFF AREA ===================== STAFF AREA ======================= STAFF AREA ============= STAFF AREA ===============
# STAFF DASHBOARD
@app.route("/staff_dashboard")
def staff_dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect("/student_login")
    staff_list = dbhelper.get_all_staff()
    return render_template("staff_dashboard.html", username=session["user"], staff_list=staff_list)

if __name__ == "__main__":
    app.run(debug=True)
