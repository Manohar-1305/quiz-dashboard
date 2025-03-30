import os
 # Convert bytes to string before inserting

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql://quiz_user:password@15.206.72.196/quizdb'  # Ensure this is set before SQLAlchemy initialization
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optionally disable modification tracking
