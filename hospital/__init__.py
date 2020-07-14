#importing Flask
from flask import Flask
#importing SQLALchemy(database) extension for flask
from flask_sqlalchemy import SQLAlchemy
#importing crypting algorithm extension for flask( for safe passwords )
from flask_bcrypt import Bcrypt
#importing login extension for flask
from flask_login import LoginManager

#giving variable for Flask application 
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

#configurating SQLALchemy database uri
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

#giving variable for SQLALchemy
db = SQLAlchemy(app)

#giving variable for bcrypt function
bcrypt = Bcrypt(app)

#giving variable for login manager
login_manager = LoginManager(app)

#path in the case of causing login
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from hospital import routes
