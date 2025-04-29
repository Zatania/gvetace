from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

csrf = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate(db=db)
