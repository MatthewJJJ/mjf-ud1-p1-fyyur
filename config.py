import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the databaseE
   
#pswd = open('pswd.txt', 'r')
pswd = '' # enter password here...

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:{0}@localhost:5432/fyyur'.format(pswd)
print(SQLALCHEMY_DATABASE_URI)
