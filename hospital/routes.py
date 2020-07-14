from datetime import date
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from hospital import app, db, bcrypt
from hospital.forms import RegistrationForm, LoginForm, UpdateAccountForm, DiagnosisForm, UpdateAccountAdminForm, UploadPictureForm, DateForm
from hospital.models import Patient, Doctor, Diagnosis, Admin
from flask_login import login_user, current_user, logout_user, login_required

#function for quick sort
def qsort_index(lst, index):
    if len(lst) == 0:
        return []
    else:
        pivot = lst[0]
        lesser = qsort_index([x for x in lst[1:] if x[index] < pivot[index]], index)
        greater = qsort_index([x for x in lst[1:] if x[index] >= pivot[index]], index)
        return lesser + [pivot] + greater


def binarySearch (arr, l, r, x): 
    # Check base case 
    if r >= l: 
        mid = l + (r - l)//2
        # If element is present at the middle itself 
        if arr[mid] == x: 
            return mid 
        # If element is smaller than mid, then it can only 
        # be present in left subarray 
        elif arr[mid] > x: 
            return binarySearch(arr, l, mid-1, x) 
        # Else the element can only be present in right subarray 
        else: 
            return binarySearch(arr, mid+1, r, x) 
    else: 
        # Element is not present in the array 
        return -1

#function for binary search
def recursiveBinarySearch(aList, target):
    aList = sorted(aList)

    if len(aList) == 0:
        return False
    else:
        midpoint = len(aList) // 2
        if aList[midpoint] == target:
            return aList.index(target)
        else:
            if target < aList[midpoint]:
                return recursiveBinarySearch(aList[:midpoint],target)
            else:
                return recursiveBinarySearch(aList[midpoint+1:],target)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Main" )



@app.route("/about")
def about():
    return render_template('about.html', title='About')

#decorator for registrating patients
@app.route("/register_patient", methods=['GET', 'POST'])
def register_patient():
    form = RegistrationForm()
    if form.validate_on_submit():
        #hashing passwords using bcrypt for security
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #executing sql query to insert new user
        result = db.engine.execute("insert into patient(name, surname, id, password, image_file, role) values(:n, :s, :i,:p,:f, :r)",{'n':form.name.data, 's':form.surname.data, 'i':form.email.data, 'p': hashed_password, 'f':'default.jpg', 'r':'patient'})
        db.session.commit()
        flash('New patient`s account has been created! New patient is now able to log in', 'success')
        return redirect(url_for('patient_admin'))
    return render_template('register.html', title='New Patient', form=form)

#decorator for registrating doctors
@app.route("/register_doctor", methods=['GET', 'POST'])
def register_doctor():
    form = RegistrationForm()
    if form.validate_on_submit():
        #hashing passwords using bcrypt for security
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #executing sql query to insert new user
        result = db.engine.execute("insert into doctor(name, surname, id, password, image_file, role) values(:n, :s, :i,:p,:f, :r)",{'n':form.name.data, 's':form.surname.data, 'i':form.email.data, 'p': hashed_password, 'f':'default.jpg', 'r':'doctor'})
        db.session.commit()
        flash('New doctor`s account has been created! New doctor is now able to log in', 'success')
        return redirect(url_for('doctor_admin'))
    return render_template('register.html', title='New Doctor', form=form)


#authenctication decorator
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #declaring form for login
    form = LoginForm()
    if form.validate_on_submit():
        #checking the type of account and authentication
        patient = Patient.query.filter_by(id=form.email.data).first()
        doctor = Doctor.query.filter_by(id=form.email.data).first()
        admin = Admin.query.filter_by(id=form.email.data).first()
        if patient and bcrypt.check_password_hash(patient.password, form.password.data):
            login_user(patient, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        elif doctor and bcrypt.check_password_hash(doctor.password, form.password.data):
            login_user(doctor, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        elif admin and admin.password == form.password.data:
            login_user(admin, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#decorator for logging out
@app.route("/logout")
def logout():
    #function for logging out user
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


#decorator for account page
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    #if form called, all the variables will be added and edited for current user`s account
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if current_user.role == 'admin':    
            result = db.engine.execute("update admin set name = :n, surname = :s, id = :e where id_number = :i", { 'n':form.name.data, 's':form.surname.data, 'e':form.email.data, 'i':current_user.id_number })    
        elif current_user.role == 'doctor':
            result = db.engine.execute("update doctor set name = :n, surname = :s, id = :e where id_number = :i", { 'n':form.name.data, 's':form.surname.data, 'e':form.email.data, 'i':current_user.id_number })
        elif current_user.role == 'patient':
            result = db.engine.execute("update patient set name = :n, surname = :s, id = :e where id_number = :i", { 'n':form.name.data, 's':form.surname.data, 'e':form.email.data, 'i':current_user.id_number })
        #current_user.name = form.name.data
        #current_user.surname = form.surname.data
        #current_user.id = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    #condition will give form current user details     
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.id
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

def save_picture_diagnosis(form_picturee):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picturee.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/diagnosis_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picturee)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

#decorator for adding new diagnosis
@app.route("/diagnosis/new", methods=['GET', 'POST'])
@login_required
def new_diagnosis():
    form1 = DiagnosisForm()
    current_image = None
    picture_file = "default.png" 
    if form1.validate_on_submit():
        # if user uploads new image, it saves it, else default image will be saved
        if form1.picture.data:
            picture_file = save_picture_diagnosis(form1.picture.data)
            current_image = url_for('static', filename='diagnosis_pics/' + picture_file)
        patient = Patient.query.filter_by(id=form1.patientemail.data).first()
        if patient:
            #inserting query into diagnosis
            result = db.engine.execute("insert into diagnosis(status, image_file, patient_id, content, doctor_id, date_posted) values(:s, :f, :p,:c,:d, :o)",{'s':form1.status.data, 'f': 'default.png', 'p':patient.id_number, 'c': form1.content.data , 'd':current_user.id_number, 'o': date.today()}) 
            #diagnosis = Diagnosis(status=form1.status.data , image_file=picture_file, patient = patient, content=form1.content.data, doctor = current_user)
            #db.session.add(diagnosis)
            db.session.commit()
            flash('Your diagnosis has been created!', 'success')
            return redirect(url_for('my_diagnosis'))
        else:
            #if email of patient is valid
            flash('Unsuccessful. There is no patient with such email', 'danger')
    return render_template('new_diagnosis.html', title='New Diagnosis',
                           form=form1, legend='New Diagnosis', current_image = current_image)

@app.route("/diagnosis/<int:diagnosis_id>", methods=['GET', 'POST'])
def diagnosis(diagnosis_id): 
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    return render_template('diagnosis.html', title = 'Diagnosis', diagnosis=diagnosis)

#decorator for updating diaganosis
@app.route("/diagnosis/<int:diagnosis_id>/update", methods=['GET', 'POST'])
@login_required
def update_diagnosis(diagnosis_id):
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    form = DiagnosisForm()
    if form.validate_on_submit():
        #sql query updates data in diagnosis database
        result = db.engine.execute("update diagnosis set status = :s, content = :c where id = :i", { 's':form.status.data, 'c':form.content.data, 'i': diagnosis_id })
        #diagnosis.status = form.status.data
        #diagnosis.content = form.content.data 
        db.session.commit()
        flash('Your diagnosis has been updated!', 'success')
        return redirect(url_for('diagnosis', diagnosis_id=diagnosis.id))
    # initially, forms gets current data about diagnosis    
    elif request.method == 'GET':
        form.patientemail.data = diagnosis.patient.id
        form.status.data = diagnosis.status
        form.content.data = diagnosis.content
    return render_template('new_diagnosis.html', title='Update Diagnosis',
                           form=form, legend='Update Diagnosis')


#decorator for deleting existing diagnisis
@app.route("/diagnosis/<int:diagnosis_id>/delete", methods=['POST'])
@login_required
def delete_diagnosis(diagnosis_id):
    #sql query for deleting current diagnosis
    diagnosis = db.engine.execute("delete from diagnosis where id = :n",{'n':diagnosis_id})
    #diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    #db.session.delete(diagnosis)
    db.session.commit()
    flash('Your diagnosis has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/doctor_admin")
def doctor_admin():
    doctors = Doctor.query.all()
    return render_template('doctor_admin.html', doctors = doctors)

@app.route("/patient_admin")
def patient_admin():
    patients = Patient.query.all()
    return render_template('patient_admin.html', patients = patients)

#decorator for showing list od diagnosis
@app.route("/my_diagnosis", methods=['GET', 'POST'])
def my_diagnosis():
    user_role = current_user.role
    #taking data about current user diagnosis depending on role
    if user_role == 'doctor':
       diagnosises = db.engine.execute("select patient.name, patient.surname, diagnosis.image_file, diagnosis.status, diagnosis.content, diagnosis.date_posted, diagnosis.id from diagnosis inner join patient on diagnosis.patient_id=patient.id_number where patient_id = :n",{'n':current_user.id_number}).fetchall()
    elif user_role == 'patient':
       diagnosises = db.engine.execute("select doctor.name, doctor.surname, diagnosis.image_file, diagnosis.status, diagnosis.content, diagnosis.date_posted, diagnosis.id from diagnosis inner join doctor on diagnosis.doctor_id=doctor.id_number where doctor_id = :n",{'n':current_user.id_number}).fetchall()
    
    form = DateForm()
    #creating final list of diagnosies
    final_diagnosises = diagnosises
    if form.validate_on_submit():
        date = form.date.data
        #sorting diagnosises
        #sorted_diagnosies = qsort_index(diagnosises,2)
        #search diagnosis if date inputed
        final_diagnosises = recursiveBinarySearch(diagnosises[2], date)   
        flash('Your diagnosis has been updated!', 'success')
        #return redirect(url_for('my_diagnosis')
    
    return render_template('my_diagnosis2.html', title='My Diagnosis', diagnosises = final_diagnosises, form = form)



@app.route("/user/<string:user_role>/<int:user_id>", methods=['GET', 'POST'])
def user(user_role, user_id):
    form = UpdateAccountForm()
    if user_role == 'doctor':
       user = Doctor.query.get_or_404(user_id)
    elif user_role == 'patient':
       user = Patient.query.get_or_404(user_id)
    elif user_role == 'admin':
       user = Admin.query.get_or_404(user_id)
    return render_template('user.html', title=user.surname, user=user)


#decorator for updating users
@app.route("/user/<string:user_role>/<int:user_id>/update", methods=['GET', 'POST'])
def update_user(user_role, user_id):
    #getting current data about current user by checking the role
    if user_role == 'doctor':
       user = Doctor.query.get_or_404(user_id)
    elif user_role == 'patient':
       user = Patient.query.get_or_404(user_id)
    elif user_role == 'admin':
       user = Admin.query.get_or_404(user_id)
    form = UpdateAccountAdminForm()
    if form.validate_on_submit():
        #checks if user entered new picture
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        #updates data according to the edited data in form
        if user_role == 'doctor':
            result = db.engine.execute("update doctor set name = :n, surname = :s, id = :e where id_number = :i", { 'n':form.name.data, 's':form.surname.data,'e':form.email.data, 'i': user_id })
        elif user_role == 'patient':
            result = db.engine.execute("update patient set name = :n, surname = :s, id = :e where id_number = :i", { 'n':form.name.data, 's':form.surname.data,'e':form.email.data, 'i': user_id })
        elif user_role == 'admin':    
            result = db.engine.execute("update admin set name = :n, surname = :s, id = :e where id_number = :i", { 'n':form.name.data, 's':form.surname.data,'e':form.email.data, 'i': user_id })    
        #user.name = form.name.data
        #user.surname = form.surname.data
        #user.id = form.email.data
        db.session.commit()
        flash('Account has been updated!', 'success')
        return redirect(url_for('user', user_id=user.id_number, user_role=user.role))
    # takes current user data for the form    
    elif request.method == 'GET':
        form.name.data = user.name
        form.surname.data = user.surname
        form.email.data = user.id
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('account.html', title=user.surname +' '+ user.name,
                           image_file=image_file, form=form)

#decorator for deleting users
@app.route("/user/<string:user_role>/<int:user_id>/delete", methods=['POST'])
def delete_user(user_id, user_role):
    #identifies user account type and gets data from database
    if user_role == 'doctor':
       user = Doctor.query.get_or_404(user_id)
    elif user_role == 'patient':
       user = Patient.query.get_or_404(user_id)
    elif user_role == 'admin':
       user = Admin.query.get_or_404(user_id)
    #deleting from database depending on user type
    if user_role == 'doctor':
       result = db.engine.execute("delete from doctor where id = :i",{'i':user_id})
    elif user_role == 'patient':
       result = db.engine.execute("delete from patient where id = :i",{'i':user_id})
    elif user_role == 'admin':
       result = db.engine.execute("delete from admin where id = :i",{'i':user_id})
       
    #db.session.delete(user)
    db.session.commit()
    flash('User has been deleted!', 'success')
    return redirect(url_for('home'))
