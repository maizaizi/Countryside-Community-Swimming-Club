from flask import Blueprint, render_template, redirect, url_for,\
    session, request, flash
from flask_hashing import Hashing
from config import get_cursor, allowed_file, UPLOAD_FOLDER
from functools import wraps
import re
import os
from datetime import datetime,timedelta,date
from werkzeug.utils import secure_filename
import requests
# create the auth blueprint for authorization view, such as login, register and logout
auth_blueprint = Blueprint('auth', __name__)
# create an instance of hashing
hashing = Hashing()

# decorate function to check if user is logged in
def login_required(f):
    @wraps(f)
    def wrapper_login_required(*args,**kwargs):
       if 'username' not in session:
           return redirect(url_for('auth.login'))
       else:
           return f(*args,**kwargs)
    return wrapper_login_required

# decorate function to check if user has the required role
def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper_role_required(*args,**kwargs):
            if "username" in session:
                if session["role"] not in role:
                    return redirect(url_for('auth.unauthorized'))
                else:
                    return f(*args,**kwargs)
            else:
                return redirect(url_for("auth.login"))
        return wrapper_role_required
    return decorator

# this is the login page
@auth_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ''  # Message to display on the login page
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_password = request.form['password']
        # Retrieve the account details from the database
        cursor = get_cursor()  
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            account_id, username, stored_password, role = account['account_id'], account['username'], account['password'], account['role']
            if hashing.check_value(stored_password, user_password, salt='GROUPAP'):
                # get the status of this account
                cursor.execute('SELECT status FROM member WHERE account_id = %s\
                            UNION SELECT status FROM instructor WHERE account_id = %s\
                            UNION SELECT status FROM manager WHERE account_id = %s',\
                            (account_id,account_id,account_id))
                status = cursor.fetchone()
                # check if the account status is active
                if status['status'] =='active':
                    # Set session variables and redirect the user to the appropriate dashboard
                    session['loggedin'] = True
                    session['id'] = account_id
                    session['username'] = username
                    session['role'] = role
                    # Redirect to home page
                    return redirect(url_for('auth.user'))
                else:
                    # Output message if the account is inactive.
                    msg = 'Your account is inactive, please contact manager for more infromation.'
            else:
                # Password incorrect
                msg = 'Invalid password'
        else:
            # Account doesnt exist or username incorrect
            msg = 'Invalid username'
    # Render the login page with any message (if applicable)
    return render_template('login.html', msg=msg)

# this is the registration page
@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    cursor=get_cursor()
    cursor.execute("SELECT * FROM subscription")
    subscription=cursor.fetchall()
    if request.method=='POST':
        account_type='member'
        username=request.form['username']
        password=request.form['password']
        title=request.form['title']
        first_name=request.form['first_name']
        family_name=request.form['family_name']
        position=request.form['position']
        phone=request.form['phone']
        email= request.form['email']
        address=request.form['address']
        # get the member date of birth
        dob=request.form['dob'] 
        subscription_id=request.form['subscription']
        cursor=get_cursor()
        cursor.execute("SELECT * FROM subscription WHERE id=%s",(subscription_id,))
        selected_subscription=cursor.fetchone()
        # get the profile image, can be null
        image=request.files['image']
        # get the health information, can be null
        health_info=request.form['health_info']
        cursor = get_cursor()
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg='Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg='Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg='Username must contain only characters and numbers!'
        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
            msg='Password must be at least 8 characters long and mix with lowercase \
                letter, uppercase letter and number!'
        # raise a notice if the uploaed image does not meet the requirement
        elif  image.filename!='' and not allowed_file(image.filename):  
            msg='Please upload images in type of jpg, png and jpeg.'
        else:
             # Account doesnt exists and the form data is valid, now insert new account into accounts table
            hashed = hashing.hash_value(password, salt='GROUPAP')
            # insert into the account table
            cursor.execute('INSERT INTO account (username,password,role)\
                    VALUES (%s, %s, %s)', (username, hashed, account_type))
            # get the inserted account_id
            account_id=cursor.lastrowid
            if image.filename !='':
                # change the image name to a secure name
                seruce_image_name = secure_filename(image.filename)
                # create unique name of the image
                image_name=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+seruce_image_name
                # save image to the local folder
                image.save(os.path.join(UPLOAD_FOLDER, image_name))
            else:
                image_name=''
            # insert into the instructor table
            cursor.execute('INSERT INTO member (account_id, title,first_name, family_name,\
                    position, phone, email, address,dob,image,health_info) \
                    VALUES (%s,%s, %s, %s,%s, %s, %s,%s, %s,%s,%s)',\
                    (account_id, title,first_name, family_name,\
                    position, phone, email, address,dob,image_name,health_info))   
            member_id=cursor.lastrowid 
            print('this is new member id',member_id)
            session['loggedin'] = True
            session['id'] = account_id
            session['username'] = username
            session['role'] = account_type
            flash('You have successfully registered an account. Please make the membership subscription payment')
            return render_template('payment_subscription.html',subscription=selected_subscription,member_id=member_id) 
        
        return render_template('register.html',msg=msg,subscription=subscription) 
       
    return render_template('register.html',subscription=subscription)        


# this is the logout page
@auth_blueprint.route('/logout')
# require to login first
@login_required
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('role', None)
   # Redirect to login page
   return redirect(url_for('auth.login'))

# direct to unauthorized page when user is not allowed to access
@auth_blueprint.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html')

# direct to the home page for each user: member, instructor and manager
# login is required
@auth_blueprint.route('/user')
@login_required
def user():
    if session["role"]=="member":
        return redirect(url_for('member.member'))
    elif session["role"]=="instructor":
        return redirect(url_for('instructor.instructor'))
    elif session["role"]=="manager":
        return redirect(url_for('manager.manager'))



