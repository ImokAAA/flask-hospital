from datetime import date
from hospital import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id): 
    patient = Patient.query.filter_by(id=user_id).first()
    doctor = Doctor.query.filter_by(id=user_id).first()
    admin = Admin.query.filter_by(id=user_id).first()
    if admin:
        return Admin.query.get(int(admin.id_number))
    elif doctor:
        return Doctor.query.get(int(doctor.id_number))
    elif patient:
        return Patient.query.get(int(patient.id_number))

#database model for admin table
class Admin(db.Model, UserMixin): 
    id_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    id = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='admin')
    #function for setting values, that class will return when calling the database
    def __repr__(self):
        return f"Admin('{self.name}','{self.surname}' ,'{self.id}', '{self.image_file}','{self.role}','{self.password}')"
#database model for paatient table
class Patient(db.Model, UserMixin):
    id_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    id = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    diagnosis = db.relationship('Diagnosis', backref='patient', lazy=True)
    role = db.Column(db.String(10), nullable=False, default='patient')
    #function for setting values, that class will return when calling the database
    def __repr__(self):
        return f"Patient('{self.name}','{self.surname}' ,'{self.id}', '{self.image_file}','{self.role}')"
#database model for doctor table
class Doctor(db.Model, UserMixin):
    id_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    id = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    diagnosis = db.relationship('Diagnosis', backref='doctor', lazy=True)
    role = db.Column(db.String(10), nullable=False, default='doctor')
    #function for setting values, that class will return when calling the database
    def __repr__(self):
        return f"Doctor('{self.name}','{self.surname}' ,'{self.id}', '{self.image_file}','{self.role}')"

#database model for diagnosis table
class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.Date, nullable=False, default=date.today())
    image_file = db.Column(db.String(20), nullable=False, default = 'default.png')
    content = db.Column(db.Text, nullable=False)
    #foregin keys from patient and doctor tables
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id_number'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id_number'), nullable=False)
    #function for setting values, that class will return when calling the database
    def __repr__(self):
        return f"Diagnosis('{self.status}', '{self.date_posted}', '{self.image_file}')"

