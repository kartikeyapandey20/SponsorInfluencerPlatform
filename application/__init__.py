from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
from sqlalchemy import create_engine

# Define the current directory and SQLite database URI
base_dir = os.path.abspath(os.path.dirname(__file__))
URI = "sqlite:///" + os.path.join(base_dir, '../db-directory', "models.db")
engine=create_engine(URI)

# Initialize Flask app and SQLAlchemy
app = Flask(__name__, static_folder='../static', template_folder='../Templates')
app.config['SQLALCHEMY_DATABASE_URI'] = URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)
