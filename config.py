import os
 # Convert bytes to string before inserting

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql://quiz_user:password@13.232.97.59/quizdb'  # Ensure this is set before SQLAlchemy initialization
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optionally disable modification tracking
