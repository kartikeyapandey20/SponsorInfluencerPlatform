from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from application.models import*
from application.admin_controllers import*
from application.home_controllers import*
from application.inf_controllers import*
from application.sponsor_controllers import*
from application.adreq_controllers import*
from application.charts_controllers import*

# Run the Flask application
if __name__=='__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

