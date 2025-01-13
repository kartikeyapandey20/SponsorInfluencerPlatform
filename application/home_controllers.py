from flask import Flask, render_template,redirect,url_for,flash,request,session,abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from application.models import*
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
import os

#Error Handling
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('Home_Error.html',message="You are not authorized to access this page"), 403

@app.errorhandler(404)
def page_not_found(e):
    return ('Page Not Found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return ('Oops! Something went wrong'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return ('Oops! Something went wrong'), 500


def login_user(user, user_type):
    if user_type == 'admin':
        user_id = user.AdminID
    elif user_type == 'sponsor':
        user_id = user.SponsorID
    elif user_type == 'influencer':
        user_id = user.InfluencerID
    else:
        user_id = None
    session['user_id'] = user_id
    session['user_type'] = user_type

def get_user_by_type(user_type, username):
    if user_type == 'admin':
        return Admin.query.filter_by(Name=username).first()
    elif user_type == 'sponsor':
        return Sponsor.query.filter_by(Name=username).first()
    elif user_type == 'influencer':
        return Influencer.query.filter_by(Name=username).first()
    return None


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('You need to log in to access this page.')
                return redirect(url_for('login'))
            
            user_id = None
            if role == 'influencer':
                user_id = kwargs.get('influencer_ID')
            elif role == 'sponsor':
                user_id = kwargs.get('sponsor_ID')
            elif role == 'admin':
                user_id = kwargs.get('admin_ID')
                
            if role and (session.get('user_type') != role or session.get('user_id') != user_id):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/home',methods=["GET"])
def home():
    return render_template('Home_LoginChoice.html')

@app.route('/home/influencer/signup',methods=["GET","POST"])
def influencer_signup():
    if request.method=='POST':
        name = request.form.get('Username')
        email = request.form.get('Email')
        password = request.form.get('Password')
        bio = request.form.get('bio')
        followers = request.form.get('followers')
        phone=request.form.get('Phone')
        profile_image = request.files.get('profile_image')

        profile_pic_link = None
        if profile_image:
            upload_folder = 'static/images/Influencer'
            filename = secure_filename(f"{name}.png")
            filepath = os.path.join(upload_folder, filename)
            profile_image.save(filepath)
            profile_pic_link = filename

        new_influencer = Influencer(
            Name=name,
            Email=email,
            Password=password,
            Bio=bio,
            Followers=int(followers),
            PhoneNo=phone,
            JoiningDate=datetime.today(),
            ProfilePicLink=profile_pic_link
        )
        db.session.add(new_influencer)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('Influencer_registration.html')

@app.route('/home/sponsor/signup',methods=['GET','POST'])
def sponsor_signup():
    if request.method == 'POST':
        username = request.form.get('Username')
        email = request.form.get('Email')
        password = request.form.get('Password')
        phone = request.form.get('Phone')
        address = request.form.get('Address')
        brand = request.form.get('brand')
        industry = request.form.get('industry')
        about = request.form.get('About')
        link = request.form.get('link')
        profile_image = request.files.get('profile_image')

        profile_pic_link = None
        if profile_image:
            upload_folder = 'static/images/Sponsor'
            filename = secure_filename(f"{username}.png")
            filepath = os.path.join(upload_folder, filename)
            profile_image.save(filepath)
            profile_pic_link = filename

        new_sponsor = Sponsor(
            Name=username,
            Email=email,
            Password=password,
            PhoneNo=phone,
            Address=address,
            Brand=brand,
            Industry=industry,
            BrandDescription=about,
            Website=link,
            ProfilePicLink=profile_pic_link,
            JoiningDate=datetime.today()
        )

        db.session.add(new_sponsor)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('Sponsor_registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session and 'user_type' in session:
        user_type = session['user_type']
        user_id = session['user_id']
        if user_type == 'admin':
            return redirect(f'/admin/home/{user_id}')
        elif user_type == 'sponsor':
            return redirect(f'/sponsor/home/{user_id}')
        elif user_type == 'influencer':
            return redirect(f'/influencer/home/{user_id}')
    error=None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['role']

        user = get_user_by_type(user_type, username)

        if user and (user.Password==password):
            if (user_type == 'sponsor' or user_type == 'influencer') and user.Flagged==1:
                error = 'Your account is flagged. Please contact support.'
            else:
                login_user(user, user_type)
                if user_type == 'admin':
                    return redirect(f'/admin/home/{user.AdminID}')
                elif user_type == 'sponsor':
                    return redirect(f'/sponsor/home/{user.SponsorID}')
                elif user_type == 'influencer':
                    return redirect(f'/influencer/home/{user.InfluencerID}')
        else:
            error='Invalid Username or Password'

    return render_template('Home_Login.html',error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))