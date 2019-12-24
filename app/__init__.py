#pylint: disable=no-member
#from flask import Flask


from flask import Flask
from flask_cors import CORS

application = Flask(__name__)
CORS(application)

from app import routes
# app = the name of the package
# application = the name of the flask instance variable
