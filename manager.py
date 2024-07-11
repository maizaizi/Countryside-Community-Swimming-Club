from flask import Blueprint, render_template, redirect, url_for,\
    session, request, flash, jsonify
from flask_hashing import Hashing
from config import get_cursor, get_user_id, allowed_file,UPLOAD_FOLDER,TIMESLOTS
from auth import role_required
import re
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from collections import Counter

#from flask_sqlalchemy import SQLAlchemy

# create manager blueprint view
manager_blueprint = Blueprint('manager', __name__)
#create an instance of hashing
hashing = Hashing()


# this is the home page for manager
@manager_blueprint.route('/')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def manager():
    account_id=session['id']
    manager_id=get_user_id(account_id)
    cursor=get_cursor()
    cursor.execute("SELECT COUNT(*) AS number FROM member")
    member_number=cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM instructor")
    instructor_number=cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM class WHERE status='active'")
    class_number=cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM memberships ")
    membership_number=cursor.fetchone()
    
    return render_template('manager_dashboard.html',active='dashboard',\
          member_number=member_number, instructor_number=instructor_number,\
        class_number=class_number,membership_number=membership_number) 

# this is the page to list all the members
@manager_blueprint.route('/listmembers')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def list_members():
    cursor=get_cursor()
    # get the information of members
    cursor.execute("SELECT member_id,title,first_name,family_name,\
            position,phone,email,address,dob,image, \
            IFNULL(health_info,'') AS health_info,status\
            FROM member ORDER BY family_name, first_name")
    member_list=cursor.fetchall()
    # using active to make the current members menu active
    return render_template('memberlist.html', member_list=member_list,active='members') 

# this is the page to search a member according to the first name or family name
@manager_blueprint.route('/searchmember', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def search_member():
    if request.method=='POST':
        member_name=request.form['member_search']
        search_name = '%'+ member_name +'%'
        cursor=get_cursor()
        # get the search result information of members
        cursor.execute("SELECT member_id,title,first_name,family_name,\
                position,phone,email,address,dob,image,\
                IFNULL(health_info,'') AS health_info,status\
                FROM member WHERE first_name LIKE %s or \
                family_name LIKE %s ORDER BY family_name, first_name",(search_name,search_name))
        member_list=cursor.fetchall()
        # using active to make the current members menu active
        return render_template('memberlist.html', member_list=member_list,active='members') 

# this is the page to inactive a member's account
@manager_blueprint.route('/editmemberstatus/<int:member_id>')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def edit_member_status(member_id):
    cursor=get_cursor()
    # get the information of member
    cursor.execute("SELECT first_name,family_name,status\
            FROM member WHERE member_id= %s", (member_id,))
    member=cursor.fetchone()
    if member['status']=='active':
        status='inactive'
    else:
        status='active'
    cursor.execute("UPDATE member SET status=%s\
                WHERE member_id=%s", (status,member_id))
    # show message after the update of the status
    message = "Update {} {}'s account to {}".format(\
        member['first_name'],member['family_name'],status)
    flash(message)
    return redirect(url_for('manager.list_members'))

# get member detail for editing
@manager_blueprint.route('/memberdetail/<int:member_id>')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def get_member_detail(member_id):
    cursor=get_cursor()
    # get the information of member
    cursor.execute("SELECT * FROM member WHERE member_id= %s", (member_id,))
    member=cursor.fetchone()
    # get the account information for this member
    cursor.execute("SELECT * FROM account AS a\
            JOIN member AS m ON a.account_id = m.account_id\
            WHERE member_id= %s", (member_id,))
    account=cursor.fetchone()
    return render_template('memberdetail.html',member= member,account=account,active='members')

# update the member's profile
@manager_blueprint.route('/updatememberprofile', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def update_member_profile():
    if request.method=='POST':
        member_id=request.form['member_id']
        title=request.form['title']
        first_name=request.form['first_name']
        family_name=request.form['family_name']
        position=request.form['position']
        phone=request.form['phone']
        email= request.form['email']
        address=request.form['address']
        dob=request.form['dob']
        health_info=request.form['health_info']
        # get the old image name
        old_image_name=request.form['old_image']
        image_name=old_image_name
        # get the new image 
        new_image=request.files['new_image']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            # flash message 
            flash('Invalid email address!')
        else:    
            if allowed_file(new_image.filename):
                # change the image name to a secure name
                seruce_image_name = secure_filename(new_image.filename)
                # create unique name of the image
                image_name=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+seruce_image_name
                # save image to the local folder
                new_image.save(os.path.join(UPLOAD_FOLDER, image_name))
                # if the old image is not null remove the old image
                if old_image_name:
                    os.remove(os.path.join(UPLOAD_FOLDER, old_image_name))
            # raise a notice if the image type is not allowed
            elif new_image.filename and not allowed_file(new_image.filename):
                flash('Please upload images in type of jpg, png and jpeg.')
                return redirect(url_for('manager.get_member_detail',member_id=member_id))
            cursor=get_cursor()
            # update the member profile
            sql_query="UPDATE member SET title=%s,first_name=%s,family_name=%s,position=%s,\
                phone=%s,email=%s,address=%s,dob=%s,image=%s,health_info=%s WHERE member_id=%s"
            cursor.execute(sql_query, (title,first_name,family_name,position,phone,email,\
                address,dob,image_name,health_info,member_id))
            message='You have successfully updated profile for {} {}'.format(first_name,family_name)
            flash(message)
        return redirect(url_for('manager.get_member_detail',member_id=member_id))
    return redirect(url_for('manager.list_members'))

# change the member's password
@manager_blueprint.route('/updatememberpassword', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def update_member_password():
    if request.method=='POST':
        account_id=request.form['id']
        password=request.form['new_password']
        cursor=get_cursor()
        cursor.execute("SELECT member_id,first_name,family_name FROM member AS m\
            JOIN account AS a ON m.account_id=a.account_id WHERE m.account_id=%s",(account_id,))
        member = cursor.fetchone()
        # check if password meets the requirement
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
            message='Password must be at least 8 characters long\
            and mix with lowercase letter, uppercase letter and number!'
            flash(message)
        else: 
            # hash the password and insert into the account table   
            hashed_password = hashing.hash_value(password, salt='GROUPAP')
            cursor.execute("UPDATE account SET password=%s \
                            WHERE account_id=%s",(hashed_password, account_id))
            message='You have successfully updated password for {} {}'.format\
                (member['first_name'],member['family_name'])
            flash(message)
        return redirect(url_for('manager.get_member_detail',member_id=member['member_id']))
    return redirect(url_for('manager.list_members'))

# this is the new member add form
@manager_blueprint.route('/newmemberform')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def get_member_form():
    return render_template('memberform.html',active='members')

# add new member
@manager_blueprint.route('/addmember', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def add_member():
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
        image=request.files['image']
        health_info=request.form['health_info']
        cursor = get_cursor()
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!') 
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
            flash('Password must be at least 8 characters long and mix with lowercase \
                letter, uppercase letter and number!')
        # raise a notice if the uploaded image does not meet the requirement
        elif  image.filename!='' and not allowed_file(image.filename):  
            flash('Please upload images in type of jpg, png and jpeg.')
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
            message='You have successfully added an account for {} {}'.format(first_name,family_name)
            flash(message)
    return redirect(url_for('manager.get_member_form'))


# this is the page to list all the instructors
@manager_blueprint.route('/listinstructors')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def list_instructors():
    cursor=get_cursor()
    # get the information of instructors
    cursor.execute("SELECT instructor_id,title,first_name,family_name,\
            position,phone,email,profile,expert_area, image,status\
            FROM instructor ORDER BY family_name, first_name")
    instructor_list=cursor.fetchall()
    # using active to make the current instructors menu active
    return render_template('instructorlist.html', instructor_list=instructor_list,\
            active='instructors')

# this is the page to list all available time for instructors
@manager_blueprint.route('/listavailabletime')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def list_available_time():
    cursor=get_cursor()
    # get the available time of instructors
    cursor.execute("SELECT CONCAT(i.first_name,' ',i.family_name) AS name,\
            day,start_time,end_time FROM available_time AS a\
            JOIN instructor AS i ON a.instructor_id=i.instructor_id\
            ORDER BY a.instructor_id, FIELD(day, 'Monday', 'Tuesday',\
            'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), start_time")
    available_time=cursor.fetchall()
     # organize available_time data by instructor name
    instructor_data = {}
    for time in available_time:
        instructor_name = time['name']
        if instructor_name not in instructor_data:
            instructor_data[instructor_name] = []
        instructor_data[instructor_name].append(time)
    # using active to make the current instructors menu active
    return render_template('availabletimelist.html', instructor_data=instructor_data,\
            active='instructors')

# this is the page to search a instructor according to the first name or family name
@manager_blueprint.route('/searchinstructor', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def search_instructor():
    if request.method=='POST':
        instructor_name=request.form['instructor_search']
        search_name = '%'+ instructor_name +'%'
        cursor=get_cursor()
        # get the search result information of instructors
        cursor.execute("SELECT instructor_id,title,first_name,family_name,\
            position,phone,email,profile,image,status\
            FROM instructor WHERE first_name LIKE %s or \
            family_name LIKE %s ORDER BY family_name, first_name",(search_name,search_name))
        instructor_list=cursor.fetchall()
        # using active to make the current instructors menu active
        return render_template('instructorlist.html', instructor_list=instructor_list,active='members') 
     

# this is the page to inactive an instructor's account
@manager_blueprint.route('/editinstructorstatus/<int:instructor_id>')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def edit_instructor_status(instructor_id):
    cursor=get_cursor()
    # get the information of instructor
    cursor.execute("SELECT first_name,family_name,status\
            FROM instructor WHERE instructor_id= %s", (instructor_id,))
    instructor=cursor.fetchone()
    if instructor['status']=='active':
        status='inactive'
    else:
        status='active'
    cursor.execute("UPDATE instructor SET status=%s\
                WHERE instructor_id=%s", (status,instructor_id))
    # show message after the update of the status
    message = "Update {} {}'s account to {}".format(\
        instructor['first_name'],instructor['family_name'],status)
    flash(message)
    return redirect(url_for('manager.list_instructors'))

# get the instructor's detail for editing
@manager_blueprint.route('/instructordetail/<int:instructor_id>')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def get_instructor_detail(instructor_id):
    cursor=get_cursor()
    # get the information of instructor
    cursor.execute("SELECT * FROM instructor WHERE instructor_id= %s", (instructor_id,))
    instructor=cursor.fetchone()
    cursor.execute("SELECT name FROM class WHERE status='active'")
    all_classes=cursor.fetchall()
    # get the account information for this instructor
    cursor.execute("SELECT * FROM account AS a\
            JOIN instructor AS i ON a.account_id = i.account_id\
            WHERE instructor_id= %s", (instructor_id,))
    account=cursor.fetchone()
    return render_template('instructordetail.html',instructor= instructor,\
            all_classes=all_classes,account=account,active='instructors')

# update the instructor's profile
@manager_blueprint.route('/updateinstructorprofile', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def update_instructor_profile():
    if request.method=='POST':
        instructor_id=request.form['instructor_id']
        title=request.form['title']
        first_name=request.form['first_name']
        family_name=request.form['family_name']
        position=request.form['position']
        phone=request.form['phone']
        email= request.form['email']
        profile=request.form['profile']
        # get the expert options, this is a list
        select=request.form.getlist('expert_area')
        # change option list to a string for MySQL inserting
        expert_area = ', '.join(select)     
        old_image_name=request.form['old_image']
        # set the image name = old image name first just in case no image is uploaded
        image_name=old_image_name
        # get the new image
        new_image=request.files['new_image']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            # flash message 
            flash('Invalid email address!')
        else:    
            if new_image.filename:
                if allowed_file(new_image.filename):
                    # change the image name to a secure name
                    seruce_image_name = secure_filename(new_image.filename)
                    # create unique name of the image
                    image_name=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+seruce_image_name
                    # save image to the local folder
                    new_image.save(os.path.join(UPLOAD_FOLDER, image_name))
                    # remove the old image
                    os.remove(os.path.join(UPLOAD_FOLDER, old_image_name))
                # raise a notice if the image type is not allowed
                elif new_image.filename and not allowed_file(new_image.filename):
                    message='Please upload images in type of jpg, png and jpeg.'
                    flash(message)
                    return redirect(url_for('manager.get_instructor_detail',instructor_id=instructor_id))
            cursor=get_cursor()
            # update the instructor profile
            sql_query="UPDATE instructor SET title=%s,first_name=%s,family_name=%s,position=%s,\
                phone=%s,email=%s,profile=%s,expert_area=%s,image=%s WHERE instructor_id=%s"
            cursor.execute(sql_query, (title,first_name,family_name,position,phone,email,\
                profile,expert_area,image_name,instructor_id))
            message='You have successfully updated profile for {} {}'.format(first_name,family_name)
            flash(message)
        return redirect(url_for('manager.get_instructor_detail',instructor_id=instructor_id))
    return redirect(url_for('manager.list_instructors'))

# change the password for the instructor
@manager_blueprint.route('/updateinstructorpassword', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def update_instructor_password():
    if request.method=='POST':
        account_id=request.form['id']
        password=request.form['new_password']
        cursor=get_cursor()
        cursor.execute("SELECT instructor_id,first_name,family_name FROM instructor AS i\
            JOIN account AS a ON i.account_id=a.account_id WHERE i.account_id=%s",(account_id,))
        instructor = cursor.fetchone()
        # check if password meets the requirement
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
            message='Password must be at least 8 characters long\
            and mix with lowercase letter, uppercase letter and number!'
            flash(message)
        else: 
            # hash the password and insert into the account table   
            hashed_password = hashing.hash_value(password, salt='GROUPAP')
            cursor.execute("UPDATE account SET password=%s \
                            WHERE account_id=%s",(hashed_password, account_id))
            message='You have successfully updated password for {} {}'.format\
                (instructor['first_name'],instructor['family_name'])
            flash(message)
        return redirect(url_for('manager.get_instructor_detail',instructor_id=instructor['instructor_id']))
    return redirect(url_for('manager.list_instructors'))

# this is the instructor adding form
@manager_blueprint.route('/newinstructorform')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def get_instructor_form():
    cursor=get_cursor()
    cursor.execute("SELECT name FROM class WHERE status='active'")
    all_classes=cursor.fetchall()
    return render_template('instructorform.html',all_classes=all_classes,active='instructors')

# add new instructor
@manager_blueprint.route('/addinstructor', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def add_instructor():
    if request.method=='POST':
        account_type='instructor'
        username=request.form['username']
        password=request.form['password']
        title=request.form['title']
        first_name=request.form['first_name']
        family_name=request.form['family_name']
        position=request.form['position']
        phone=request.form['phone']
        email= request.form['email']
        profile=request.form['profile']
        # get the expert options, this is a list
        select=request.form.getlist('expert_area')
        # change option list to a string for MySQL inserting
        expert_area = ', '.join(select)     
        image=request.files['image']
        cursor = get_cursor()
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!') 
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
            flash('Password must be at least 8 characters long and mix with lowercase \
                letter, uppercase letter and number!')
        elif not allowed_file(image.filename):  
            flash('Please upload images in type of jpg, png and jpeg.')
        else:
            # change the image name to a secure name
            seruce_image_name = secure_filename(image.filename)
            # create unique name of the image
            image_name=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+seruce_image_name
            # save image to the local folder
            image.save(os.path.join(UPLOAD_FOLDER, image_name))
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            hashed = hashing.hash_value(password, salt='GROUPAP')
            # insert into the account table
            cursor.execute('INSERT INTO account (username,password,role)\
                    VALUES (%s, %s, %s)', (username, hashed, account_type))
            # get the inserted account_id
            account_id=cursor.lastrowid
            # insert into the instructor table
            cursor.execute('INSERT INTO instructor (account_id, title,first_name, family_name,\
                    position, phone, email, profile, expert_area, image) \
                    VALUES (%s,%s, %s, %s,%s, %s, %s,%s, %s,%s)',\
                    (account_id,title, first_name, family_name, position, phone,\
                    email, profile, expert_area, image_name))    

            message='You have successfully added an account for {} {}'.format(first_name,family_name)
            flash(message)
    return redirect(url_for('manager.get_instructor_form'))


# this is the profile page for manager
@manager_blueprint.route('/profile')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def profile():
    account_id=session['id']
    cursor=get_cursor()
    # get the information of manager
    cursor.execute("SELECT * FROM manager AS m\
            JOIN account AS a on m.account_id=a.account_id\
            WHERE a.account_id= %s", (account_id,))
    manager=cursor.fetchone()
    return render_template('managerprofile.html',manager= manager,active='account') 

# update the manager's own profile 
@manager_blueprint.route('/updateprofile', methods=['GET','POST'])
@role_required(['manager'])
def update_profile():
    if request.method=='POST':
        manager_id=request.form['manager_id']
        title=request.form['title']
        first_name=request.form['first_name']
        family_name=request.form['family_name']
        position=request.form['position']
        phone=request.form['phone']
        email= request.form['email']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            # flash message 
            flash('Invalid email address!')
        else:    
            cursor=get_cursor()
            # update the manager profile
            sql_query="UPDATE manager SET title=%s,first_name=%s,family_name=%s,\
                position=%s,phone=%s,email=%s WHERE manager_id=%s"
            cursor.execute(sql_query, (title,first_name,family_name,position,phone,\
                email,manager_id))
            flash('You have successfully updated your profile')
    return redirect(url_for('manager.profile'))

# update the manager's own password 
@manager_blueprint.route('/updatepassword', methods=['GET','POST'])
@role_required(['manager'])
def update_password():
    if request.method=='POST':
        account_id=request.form['id']
        old_password=request.form['old_password']
        new_password=request.form['new_password']
        cursor=get_cursor()
        cursor.execute("SELECT * FROM account WHERE account_id=%s",(account_id,))
        account = cursor.fetchone()
        # get the old hashed password
        old_hashed_password=account['password']
        # check if the old password is right
        if not hashing.check_value(old_hashed_password,old_password,salt='GROUPAP'):
            message='The old password is not right!'
            flash(message)
        # check if password meets the requirement
        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', new_password):
            message='Password must be at least 8 characters long\
            and mix with lowercase letter, uppercase letter and number!'
            flash(message)
        else: 
            # hash the password and insert into the account table   
            hashed_password = hashing.hash_value(new_password, salt='GROUPAP')
            cursor.execute("UPDATE account SET password=%s \
                            WHERE account_id=%s",(hashed_password, account_id))
            flash('You have successfully updated your password.')
    return redirect(url_for('manager.profile'))



# schedule class 
@manager_blueprint.route('/scheduleclassform', methods=['GET','POST'])
@role_required(['manager'])
def schedule_class_form():
    cursor=get_cursor()
    cursor.execute("SELECT * FROM class WHERE status='active'")
    all_classes=cursor.fetchall()
    cursor.execute("SELECT * FROM lane ")
    all_lanes=cursor.fetchall()
    cursor.execute("SELECT * FROM pool ")
    all_pools=cursor.fetchall()
    return render_template('scheduleclass.html',active='schedule',\
                all_classes=all_classes,all_lanes=all_lanes,all_pools=all_pools,timeslots=TIMESLOTS)


# edit class schedule 
@manager_blueprint.route('/editscheduleform/<int:schedule_id>', methods=['GET','POST'])
@role_required(['manager'])
def edit_schedule_form(schedule_id):
    cursor=get_cursor()
    cursor.execute("SELECT * FROM class WHERE status='active'")
    all_classes=cursor.fetchall()
    cursor.execute("SELECT * FROM lane ")
    all_lanes=cursor.fetchall()
    cursor.execute("SELECT * FROM pool ")
    all_pools=cursor.fetchall()
    cursor.execute("SELECT * FROM schedules WHERE schedule_id =%s",(schedule_id,))
    selected_schedule=cursor.fetchone()
    return render_template('scheduleeditform.html',active='schedule',\
                all_lanes=all_lanes,all_pools=all_pools,selected_schedule=selected_schedule,all_classes=all_classes,timeslots=TIMESLOTS)



@manager_blueprint.route('/response_data', methods=['GET','POST'])
@role_required(['manager'])
def response_data():
    if request.method=="POST":
        # set response to empty dictionary
        response ={'end_time':None}
        # get the data from ajax
        dayofweek = request.form['dayofweek']
        class_id = request.form['class_id']
        start_time = request.form['start_time']
        pool_id = request.form['pool']
        if class_id:
            cursor=get_cursor()
            # search the class by class id from class table
            cursor.execute("SELECT * FROM class WHERE class_id=%s",(class_id,))
            selected_class=cursor.fetchone()
        if pool_id:
            cursor=get_cursor()
            cursor.execute("SELECT name FROM pool WHERE pool_id=%s",(pool_id,))
            pool=cursor.fetchone()
            pool_name=pool['name']
            cursor.execute("SELECT lane_id FROM lane WHERE pool_id=%s",(pool_id,))
            all_lanes=cursor.fetchall()
            if all_lanes:
                response['has_lane']=True
            else:
                response['has_lane']=False
        # Process the data based on selected options
        # if both the start time and class name have value, get the end time
        if start_time and class_id:
            initial_time_format = "%H:%M"
            start_time = datetime.strptime(start_time, initial_time_format)
            # Create a timedelta
            duration = timedelta(minutes= selected_class['duration'])
            # Add duration to the start time
            end_time = start_time + duration
            # Format the new time back to a string
            end_time = end_time.strftime(initial_time_format)
            response['end_time']=end_time
            if dayofweek :
                    # get the lane for the class
                if pool_id:
                    if all_lanes:
                        cursor.execute("SELECT lane_id FROM schedules WHERE status='active' AND day=%s AND ((start_time>=%s AND start_time<=%s) OR (end_time>=%s AND end_time<=%s))",\
                                    (dayofweek,start_time,end_time,start_time,end_time))
                        used_lanes=cursor.fetchall()
                        if used_lanes:  
                            lane_ids_to_remove = {d['lane_id'] for d in used_lanes}
                            available_lanes = [item for item in all_lanes if item.get('lane_id') not in lane_ids_to_remove]
                            if available_lanes:
                                response['lanes']=available_lanes
                            else:
                                response['lanes']=None
                        else:
                            response['lanes']=all_lanes
                    else:
                        cursor.execute("SELECT name, pool_id,start_time,end_time,day FROM schedules AS s\
                                JOIN class ON class.class_id = s.class_id\
                                WHERE s.status='active' AND pool_id=%s AND day=%s AND ((start_time>=%s AND start_time<=%s) \
                                OR (end_time>=%s AND end_time<=%s))",\
                                (pool_id,dayofweek,start_time,end_time,start_time,end_time))
                        schedule = cursor.fetchone()
                        if schedule:
                            msg='There will have {} in {} on {} from {} to {}.<br>\
                            Please select another time!'.format(schedule['name'],pool_name,schedule['day'],schedule['start_time'],schedule['end_time'])
                            response['alert']= msg
                class_search='%'+selected_class['name']+'%'
                # select the instructor according to the availability of instructor and the expert area
                # add instructor filter that already have class at this time
                cursor.execute("SELECT i.instructor_id, first_name,family_name from instructor AS i \
                    JOIN available_time AS a ON i.instructor_id = a.instructor_id\
                    WHERE day=%s AND start_time<=%s AND end_time>=%s AND expert_area LIKE %s",(dayofweek,start_time,end_time,class_search))
                instructor=cursor.fetchall()
                cursor.execute("SELECT instructor_id FROM schedules WHERE status='active' AND day=%s AND ((start_time>=%s AND start_time<=%s) OR (end_time>=%s AND end_time<=%s))",\
                            (dayofweek,start_time,end_time,start_time,end_time))
                not_available_intructor=cursor.fetchall()
                if instructor:
                    if not_available_intructor:
                        # remove the not available instructor
                        # extract 'instructor_id' values to remove
                        intructor_ids_to_remove = {d['instructor_id'] for d in not_available_intructor}
                        # Remove dictionaries with matching 'instructor_id' values
                        available_instructor = [item for item in instructor if item.get('instructor_id') not in intructor_ids_to_remove]
                        if available_instructor:
                            response['instructor']=available_instructor
                        else:
                            response['instructor']='none'
                    else:
                        response['instructor']=instructor
                else:
                    # no instructor available for this class at this time
                    response['instructor']='none'
        return response
    return redirect(url_for('manager.manager'))


@manager_blueprint.route('/edit_data', methods=['GET','POST'])
@role_required(['manager'])
def edit_data():
    if request.method=="POST":
        # set response to empty dictionary
        response ={'end_time':None}
        # get the data from ajax
        schedule_id=request.form['schedule_id']
        dayofweek = request.form['dayofweek']
        class_id = request.form['class_id']
        start_time = request.form['start_time']
        pool_id = request.form['pool']
        if class_id:
            cursor=get_cursor()
            # search the class by class id from class table
            cursor.execute("SELECT * FROM class WHERE class_id=%s",(class_id,))
            selected_class=cursor.fetchone()
        if pool_id:
            cursor=get_cursor()
            cursor.execute("SELECT name FROM pool WHERE pool_id=%s",(pool_id,))
            pool=cursor.fetchone()
            pool_name=pool['name']
            cursor.execute("SELECT lane_id FROM lane WHERE pool_id=%s",(pool_id,))
            all_lanes=cursor.fetchall()
            if all_lanes:
                response['has_lane']=True
            else:
                response['has_lane']=False
        # Process the data based on selected options
        # if both the start time and class name have value, get the end time
        if start_time and class_id:
            initial_time_format = "%H:%M"
            start_time = datetime.strptime(start_time, initial_time_format)
            # Create a timedelta
            duration = timedelta(minutes= selected_class['duration'])
            # Add duration to the start time
            end_time = start_time + duration
            # Format the new time back to a string
            end_time = end_time.strftime(initial_time_format)
            response['end_time']=end_time
            if dayofweek :
                    # get the lane for the class
                if pool_id:
                    if all_lanes:
                        cursor.execute("SELECT lane_id FROM schedules WHERE schedule_id!=%s AND status='active' AND day=%s AND ((start_time>=%s AND start_time<=%s) OR (end_time>=%s AND end_time<=%s))",\
                                    (schedule_id,dayofweek,start_time,end_time,start_time,end_time))
                        used_lanes=cursor.fetchall()
                        if used_lanes:  
                            lane_ids_to_remove = {d['lane_id'] for d in used_lanes}
                            available_lanes = [item for item in all_lanes if item.get('lane_id') not in lane_ids_to_remove]
                            if available_lanes:
                                response['lanes']=available_lanes
                            else:
                                response['lanes']=None
                        else:
                            response['lanes']=all_lanes
                    else:
                        cursor.execute("SELECT name, pool_id,start_time,end_time,day FROM schedules AS s\
                                JOIN class ON class.class_id = s.class_id\
                                WHERE schedule_id!=%s AND s.status='active' AND pool_id=%s AND day=%s AND ((start_time>=%s AND start_time<=%s) \
                                OR (end_time>=%s AND end_time<=%s))",\
                                (schedule_id,pool_id,dayofweek,start_time,end_time,start_time,end_time))
                        schedule = cursor.fetchone()
                        if schedule:
                            msg='There will have {} in {} on {} from {} to {}.<br>\
                            Please select another time!'.format(schedule['name'],pool_name,schedule['day'],schedule['start_time'],schedule['end_time'])
                            response['alert']= msg
                class_search='%'+selected_class['name']+'%'
                # select the instructor according to the availability of instructor and the expert area
                # add instructor filter that already have class at this time
                cursor.execute("SELECT i.instructor_id, first_name,family_name from instructor AS i \
                    JOIN available_time AS a ON i.instructor_id = a.instructor_id\
                    WHERE day=%s AND start_time<=%s AND end_time>=%s AND expert_area LIKE %s",(dayofweek,start_time,end_time,class_search))
                instructor=cursor.fetchall()
                cursor.execute("SELECT instructor_id FROM schedules WHERE schedule_id!=%s AND status='active' AND day=%s AND ((start_time>=%s AND start_time<=%s) OR (end_time>=%s AND end_time<=%s))",\
                            (schedule_id,dayofweek,start_time,end_time,start_time,end_time))
                not_available_intructor=cursor.fetchall()
                if instructor:
                    if not_available_intructor:
                        # remove the not available instructor
                        # extract 'instructor_id' values to remove
                        intructor_ids_to_remove = {d['instructor_id'] for d in not_available_intructor}
                        # Remove dictionaries with matching 'instructor_id' values
                        available_instructor = [item for item in instructor if item.get('instructor_id') not in intructor_ids_to_remove]
                        if available_instructor:
                            response['instructor']=available_instructor
                        else:
                            response['instructor']='none'
                    else:
                        response['instructor']=instructor
                else:
                    # no instructor available for this class at this time
                    response['instructor']='none'
        return response
    return redirect(url_for('manager.manager'))


@manager_blueprint.route('/scheduleclass', methods=['GET','POST'])
@role_required(['manager'])
def schedule_class():
    if request.method=='POST':
        dayofweek=request.form['dayofweek']
        class_id=request.form['class_id']
        start_time=request.form['start_time']
        end_time=request.form['end_time']
        pool_id=request.form['pool']
        if 'lane' in request.form:
            lane_id=request.form['lane']
        else:
            lane_id=None
        instructor_id=request.form['instructor']
        # check if the end time if later than 20:00
        if end_time>'20:00':
            flash("Please schedule class before 20:00")
            return redirect(url_for('manager.schedule_class_form'))
        cursor=get_cursor()
        cursor.execute("SELECT * FROM class WHERE class_id=%s",(class_id,))
        this_class=cursor.fetchone()
        cursor.execute("INSERT INTO schedules (day,start_time,end_time,\
            pool_id,lane_id,class_id,instructor_id,capacity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",\
            (dayofweek,start_time,end_time,pool_id,lane_id,class_id,instructor_id,this_class['capacity']))
        message='You have successfully added a schedule for class: {}'.format(this_class['name'])
        flash(message)
    return redirect(url_for('manager.schedule_class_form'))


@manager_blueprint.route('/editschedule', methods=['GET','POST'])
@role_required(['manager'])
def edit_schedule():
    if request.method=='POST':
        schedule_id=request.form['schedule_id']
        dayofweek=request.form['dayofweek']
        class_id=request.form['class_id']
        start_time=request.form['start_time']
        end_time=request.form['end_time']
        pool_id=request.form['pool']
        if 'lane' in request.form:
            lane_id=request.form['lane']
        else:
            lane_id=None
        instructor_id=request.form['instructor']
        if end_time>'20:00':
            flash("Please schedule class before 20:00")
            return redirect(url_for('manager.edit_schedule_form',schedule_id=schedule_id))
        cursor=get_cursor()
        # check if this schedule has already been booked
        today=datetime.today()
        cursor.execute("SELECT * FROM bookings AS b JOIN schedules AS s\
                    ON b.schedule_id=s.schedule_id WHERE b.schedule_id =%s AND class_date>=%s",(schedule_id,today))
        booked_schedule=cursor.fetchall()
        if booked_schedule:
            flash("This schedule has already been booked, please confirm with members before editing it")
            return redirect(url_for('manager.list_schedules'))
        cursor.execute("SELECT * FROM class WHERE class_id=%s",(class_id,))
        this_class=cursor.fetchone()
        cursor.execute("UPDATE schedules SET day=%s,start_time=%s,end_time=%s,\
            pool_id=%s,lane_id=%s,class_id=%s,instructor_id=%s,capacity=%s WHERE schedule_id=%s",\
            (dayofweek,start_time,end_time,pool_id,lane_id,class_id,instructor_id,this_class['capacity'],schedule_id))
        message='You have successfully updated the schedule for class: {}'.format(this_class['name'])
        flash(message)
    return redirect(url_for('manager.list_schedules'))

@manager_blueprint.route('/listschedules', methods=['GET','POST'])
@role_required(['manager'])
def list_schedules():
    cursor=get_cursor()
    cursor.execute("SELECT s.schedule_id, day, class.name AS class_name,start_time,end_time,\
                pool.name AS pool_name,IFNULL(s.lane_id,'') AS lane_name,\
                CONCAT(i.first_name, ' ', i.family_name) AS instructor_name \
                FROM schedules AS s\
                JOIN class ON s.class_id= class.class_id\
                LEFT JOIN lane ON s.lane_id=lane.lane_id\
                JOIN pool ON s.pool_id=pool.pool_id\
                JOIN instructor AS i ON s.instructor_id=i.instructor_id\
                WHERE s.status='active' ORDER BY FIELD(day, 'Monday', 'Tuesday',\
                'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),start_time")            
    all_schedules=cursor.fetchall()
    return render_template('schedulelist.html',all_schedules=all_schedules,active='schedule')

@manager_blueprint.route('/deleteschedule/<int:schedule_id>', methods=['GET','POST'])
@role_required(['manager'])
def delete_schedule(schedule_id):
    today=datetime.today()
    cursor=get_cursor()
    # check if this schedule has already been booked
    cursor.execute("SELECT * FROM bookings AS b JOIN schedules AS s\
                    ON b.schedule_id=s.schedule_id WHERE b.schedule_id =%s AND class_date>=%s",(schedule_id,today))
    booked_schedule=cursor.fetchall()
    if booked_schedule:
        flash("This schedule has already been booked, please confirm with members before deleting it")
        return redirect(url_for('manager.list_schedules'))
    cursor.execute("SELECT class.name FROM class \
                   JOIN schedules AS s ON s.class_id=class.class_id \
                   WHERE schedule_id=%s",(schedule_id,))
    class_name=cursor.fetchone()
    cursor.execute("UPDATE schedules SET status='inactive' WHERE schedule_id=%s",(schedule_id,))
    message="You have successfully deleted this schedule for class: {}".format(class_name['name'])
    flash(message)
    return redirect(url_for('manager.list_schedules'))

@manager_blueprint.route('/schedule_filter', methods=['GET','POST'])
@role_required(['manager'])
def schedule_filter():
    if request.method=='POST':
        filter_value=request.form['filter']
        # show th eedit and delete buttons
        show_buttons=True
        if filter_value =='dayofweek':
            query="SELECT s.schedule_id, day, class.name AS class_name,start_time,end_time,\
                pool.name AS pool_name,IFNULL(s.lane_id,'') AS lane_name,\
                CONCAT(i.first_name, ' ', i.family_name) AS instructor_name \
                FROM schedules AS s\
                JOIN class ON s.class_id= class.class_id\
                LEFT JOIN lane ON s.lane_id=lane.lane_id\
                JOIN pool ON s.pool_id=pool.pool_id\
                JOIN instructor AS i ON s.instructor_id=i.instructor_id\
                WHERE s.status='active' ORDER BY FIELD(day, 'Monday', 'Tuesday',\
                'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),start_time"
        elif filter_value == 'class_name':
            query="SELECT s.schedule_id, day, class.name AS class_name,start_time,end_time,\
                pool.name AS pool_name,IFNULL(s.lane_id,'') AS lane_name,\
                CONCAT(i.first_name, ' ', i.family_name) AS instructor_name \
                FROM schedules AS s\
                JOIN class ON s.class_id= class.class_id\
                LEFT JOIN lane ON s.lane_id=lane.lane_id\
                JOIN pool ON s.pool_id=pool.pool_id\
                JOIN instructor AS i ON s.instructor_id=i.instructor_id\
                WHERE s.status='active' ORDER BY class_name,FIELD(day, 'Monday', 'Tuesday',\
                'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),start_time"
        else:
            show_buttons=False
            query="SELECT s.schedule_id, day, class.name AS class_name,start_time,end_time,\
                pool.name AS pool_name,IFNULL(s.lane_id,'') AS lane_name,\
                CONCAT(i.first_name, ' ', i.family_name) AS instructor_name \
                FROM schedules AS s\
                JOIN class ON s.class_id= class.class_id\
                LEFT JOIN lane ON s.lane_id=lane.lane_id\
                JOIN pool ON s.pool_id=pool.pool_id\
                JOIN instructor AS i ON s.instructor_id=i.instructor_id\
                WHERE s.status='inactive' ORDER BY FIELD(day, 'Monday', 'Tuesday',\
                'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),start_time"
        cursor=get_cursor()
        cursor.execute(query)            
        all_schedules=cursor.fetchall()
        response = render_template('scheduleresponse.html',all_schedules=all_schedules,\
                    active='schedule',show_buttons=show_buttons)
        return response
    return redirect(url_for('manager.list_schedules'))

# this is the page to list all the classes and lessons
@manager_blueprint.route('/listclasses')
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def list_classes():
    cursor=get_cursor()
    # get the information of classes
    cursor.execute("SELECT class_id,name,type, description,image,duration,price,\
            capacity FROM class WHERE status='active' ORDER BY name")
    all_classes=cursor.fetchall()
    # using active to make the current view class menu active
    return render_template('classlist.html', all_classes=all_classes,active='class')

@manager_blueprint.route('/class_filter', methods=['GET','POST'])
@role_required(['manager'])
def class_filter():
    if request.method=='POST':
        filter_value=request.form['filter']
        # show the edit and delete buttons
        show_buttons=True
        if filter_value == 'class_name':
            query="SELECT class_id,name,type, description,image,duration,price,\
            capacity FROM class WHERE status='active' ORDER BY name"
        elif filter_value == 'inactive_classes':
            show_buttons=False
            query="SELECT class_id,name,type, description,image,duration,price,\
            capacity FROM class WHERE status='inactive' ORDER BY name"
        cursor=get_cursor()
        cursor.execute(query)            
        all_classes=cursor.fetchall()
        response = render_template('classresponse.html',all_classes=all_classes,\
                    active='class',show_buttons=show_buttons)
        return response
    return redirect(url_for('manager.list_classes'))

# this is the route to delete the class
@manager_blueprint.route('/deleteclass/<int:class_id>', methods=['GET','POST'])
@role_required(['manager'])
def delete_class(class_id):
    cursor=get_cursor()
    # get the class name
    cursor.execute("SELECT * FROM class WHERE class_id=%s",(class_id,))
    this_class=cursor.fetchone()
    class_name=this_class['name']
    # check if this class has been scheduled
    cursor.execute("SELECT * FROM schedules WHERE class_id=%s AND status='active'",(class_id,))
    schedules=cursor.fetchall()
    if  schedules:
        message='Failed to delete class: {}. It has already been scheduled.'.format(class_name) 
    else:
        cursor.execute("UPDATE class SET status='inactive' WHERE class_id=%s",(class_id,))
        message='You have successfully deleted class: {}'.format(class_name)
    flash(message)
    return redirect(url_for('manager.list_classes'))


# Route for the manager to delete news
@manager_blueprint.route('/manage_news', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def manage_news():
    if request.method == 'POST':
        print("POST")
                
        if 'delete_news' in request.form:
            news_id = request.form['delete_news']
            cursor = get_cursor()
            cursor.execute("DELETE FROM news WHERE id=%s", (news_id,))
            flash('News deleted successfully.')
            return redirect(url_for('manager.manage_news'))
    
    # To get all news
    
    cursor = get_cursor()
    cursor.execute("SELECT * FROM news ORDER BY publish_date")
    news = cursor.fetchall()
    
    return render_template('manage_news.html', news=news)
# add news
@manager_blueprint.route('/add_news', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def add_news():
    if request.method == 'POST':
        print("POST")
        if 'add_news' in request.form: # To add news
            title = request.form['title']
            content = request.form['content']
            publish_date = request.form['publish_date']
            cursor = get_cursor()
            cursor.execute("INSERT INTO news (title, content, publish_date) VALUES (%s, %s, %s)", (title, content, publish_date))
            flash('News created successfully.')
            return redirect(url_for('manager.manage_news'))
    else:
        return render_template('manageraddnewsform.html')

# edit news
@manager_blueprint.route('/edit_news/<int:news_id>', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['manager'])
def edit_news(news_id):
    if request.method == 'POST':
        print("POST")    
        if 'edit_news' in request.form:
            news_id = request.form['edit_news']
            title = request.form['title']
            content = request.form['content']
            publish_date = request.form['publish_date']
            cursor = get_cursor()
            cursor.execute("UPDATE news SET title=%s, content=%s, publish_date=%s WHERE id=%s", (title, content, publish_date, news_id))
            flash('News updated successfully.')
            return redirect(url_for('manager.manage_news'))
    else:
        # get the news detail
        cursor=get_cursor()
        cursor.execute("SELECT * FROM news WHERE id=%s",(news_id,))
        this_news=cursor.fetchone()
        return render_template('managereditnewsform.html', id = this_news["id"], title = this_news["title"], content = this_news["content"], publish_date = this_news["publish_date"])
      
   
# this is the route to add the deleted class back
@manager_blueprint.route('/activeclass/<int:class_id>', methods=['GET','POST'])
@role_required(['manager'])
def active_class(class_id):
    cursor=get_cursor()
    cursor.execute("UPDATE class SET status='active' WHERE class_id=%s",(class_id,))
    return redirect(url_for('manager.list_classes'))

# this is the route to edit the class
@manager_blueprint.route('/editclass/<int:class_id>', methods=['GET','POST'])
@role_required(['manager'])
def edit_class(class_id):
    if request.method=="POST":
        class_id=request.form['class_id']
        name=request.form['name']
        type=request.form['type']
        description=request.form['description']
        duration=request.form['duration']
        price=request.form['price']
        capacity=request.form['capacity']
        old_image_name=request.form['current_image']
        # set the image name = old image name first just in case no image is uploaded
        image_name=old_image_name
        # get the new image
        new_image=request.files['new_image']
        # if upload a file
        if new_image.filename:
            # if this image type meets the requirment
            if allowed_file(new_image.filename):
                # change the image name to a secure name
                seruce_image_name = secure_filename(new_image.filename)
                # create unique name of the image
                image_name=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+seruce_image_name
                # save image to the local folder
                new_image.save(os.path.join(UPLOAD_FOLDER, image_name))
                # remove the old image
                os.remove(os.path.join(UPLOAD_FOLDER, old_image_name))
            # raise a notice if the image type is not allowed
            elif new_image.filename and not allowed_file(new_image.filename):
                message='Please upload images in type of jpg, png and jpeg.'
                flash(message)
                return redirect(url_for('manager.edit_class',class_id=class_id))
        cursor=get_cursor()
        # update the class detail
        print(type)
        sql_query="UPDATE class SET name=%s,type=%s,description=%s,duration=%s,\
            price=%s,capacity=%s,image=%s WHERE class_id=%s"
        cursor.execute(sql_query, (name,type,description,duration,\
            price,capacity,image_name,class_id))
        message='You have successfully updated class {}'.format(name)
        flash(message)
        return redirect(url_for('manager.list_classes'))
    else:
    # get the class detail
        cursor=get_cursor()
        cursor.execute("SELECT * FROM class WHERE class_id=%s",(class_id,))
        this_class=cursor.fetchone()
        return render_template('classdetail.html',active='class',this_class=this_class)

# this is the route to add new class
@manager_blueprint.route('/addclass', methods=['GET','POST'])
@role_required(['manager'])
def add_class():
    if request.method=="POST":
        name=request.form['name']
        type=request.form['type']
        description=request.form['description']
        duration=request.form['duration']
        price=request.form['price']
        capacity=request.form['capacity']
        # get the upload image
        new_image=request.files['image']
        # if upload a file
        if new_image.filename:
            # if this image type meets the requirment
            if allowed_file(new_image.filename):
                # change the image name to a secure name
                seruce_image_name = secure_filename(new_image.filename)
                # create unique name of the image
                image_name=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+seruce_image_name
                # save image to the local folder
                new_image.save(os.path.join(UPLOAD_FOLDER, image_name))
            # raise a notice if the image type is not allowed
            elif new_image.filename and not allowed_file(new_image.filename):
                message='Please upload images in type of jpg, png and jpeg.'
                flash(message)
                return redirect(url_for('manager.add_class'))
        cursor=get_cursor()
        # add class
        sql_query="INSERT INTO class (name,type,description,duration,\
            price,capacity,image) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql_query, (name,type,description,duration,\
            price,capacity,image_name))
        message='You have successfully added a new class: {}'.format(name)
        flash(message)
        return redirect(url_for('manager.list_classes'))
    else:
    # get the new adding class form 
        return render_template('classform.html',active='class')
       
@manager_blueprint.route('/booking_info/<int:schedule_id>', methods=['GET'])
@role_required(['manager'])
def booking_info(schedule_id):
    cursor = get_cursor()
    # Retrieve class details
    cursor.execute('''SELECT c.name, c.description, s.day, s.start_time, s.end_time
                        FROM class c
                        JOIN schedules s ON c.class_id = s.class_id
                        WHERE s.schedule_id = %s''', (schedule_id,))
    class_info = cursor.fetchone()
    
    cursor.execute('''SELECT m.member_id, m.first_name, m.family_name, m.title, b.class_date, b.start_time, b.end_time, IFNULL(a.attended, 0) as attended
                       FROM member m 
                       JOIN bookings b ON m.member_id = b.member_id 
                       LEFT JOIN attendance a ON b.booking_id = a.booking_id
                       WHERE b.schedule_id = %s AND b.booking_status IN ('confirmed', 'completed')
                     ''', (schedule_id,))
    attendees = cursor.fetchall()

    current_date = datetime.now().date()

    return render_template('manager_bookinginfo.html', current_date=current_date, class_info=class_info, attendees=attendees, schedule_id=schedule_id, active='time_table')


@manager_blueprint.route('/record_attendance/<int:schedule_id>', methods=['GET','POST'])
@role_required(['manager'])
def record_attendance(schedule_id):
    cursor = get_cursor()
    if request.method == 'POST':
        cursor.execute("SELECT booking_id FROM bookings WHERE schedule_id = %s", (schedule_id,))
        all_booking_ids = [row['booking_id'] for row in cursor.fetchall()]
        for booking_id in all_booking_ids:
            attended = request.form.get(f'attendance_{booking_id}', '0')
            attended_value = 1 if attended == '1' else 0
                
            cursor.execute("""
                INSERT INTO attendance (booking_id, attended)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE attended = VALUES(attended)
            """, (booking_id, attended_value))
                
        flash('Attendance recorded successfully', 'success')
        return redirect(url_for('manager.booking_info', schedule_id=schedule_id))

    else:
        cursor.execute("""
            SELECT b.booking_id, m.health_info, m.first_name, m.family_name, b.class_date, IFNULL(a.attended, 0) as attended
            FROM bookings b
            JOIN member m ON b.member_id = m.member_id
            LEFT JOIN attendance a ON b.booking_id = a.booking_id
            WHERE b.schedule_id = %s AND b.booking_status IN ('confirmed', 'completed')
        """, (schedule_id,))
        members = cursor.fetchall()
        current_date = datetime.now().date()


        return render_template('manager_attendance.html', members=members, current_date=current_date, schedule_id=schedule_id)

# this is the route view the membership status
@manager_blueprint.route('/view_membership_status', methods=['GET','POST'])
@role_required(['manager'])
def view_membership_status():
    cursor=get_cursor()
    cursor.execute("SELECT COUNT(*) AS number FROM memberships")
    membership_number = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM memberships \
                   WHERE  CURDATE() > expiry_date")
    expired_number = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM memberships\
            WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)")
    expired_soon_number = cursor.fetchone()
    return render_template('view_membership_status.html',membership_number=membership_number,\
              expired_number=expired_number, expired_soon_number=expired_soon_number )

# this is the route filter the membership status
@manager_blueprint.route('/membership_filter', methods=['GET','POST'])
@role_required(['manager'])
def membership_filter():
    if request.method=='POST':
        # show the membership status according to the filter
        filter_value=request.form['filter']
        if filter_value == 'all_membership':
            query="SELECT memberships.member_id,first_name,family_name,\
                type,start_date,expiry_date,\
                CASE WHEN CURDATE() <= expiry_date THEN 'Active'\
                ELSE 'Expired' END AS status FROM memberships\
                JOIN member ON memberships.member_id=member.member_id \
                ORDER BY expiry_date, family_name,first_name"
        elif filter_value == 'expired_soon':
            query="SELECT  memberships.member_id,first_name,family_name,\
               type,start_date,expiry_date,\
                CASE WHEN CURDATE() <= expiry_date THEN 'Active'\
                ELSE 'Expired' END AS status FROM memberships\
                JOIN member ON memberships.member_id=member.member_id \
                WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)\
                ORDER BY expiry_date, family_name,first_name"
        elif filter_value == 'expired':
            query="SELECT  memberships.member_id,first_name,family_name,\
               type,start_date,expiry_date,\
                CASE WHEN CURDATE() <= expiry_date THEN 'Active'\
                ELSE 'Expired' END AS status FROM memberships\
                JOIN member ON memberships.member_id=member.member_id \
                WHERE  CURDATE() > expiry_date\
                ORDER BY expiry_date, family_name,first_name"
        cursor=get_cursor()
        cursor.execute(query)
        all_membership = cursor.fetchall()
        response=render_template('membership_status_response.html',all_membership=all_membership)
        return response
    return redirect(url_for('manager.view_membership_status'))

# this is the route send the reminder for membership is about to expire
@manager_blueprint.route('/expire_soon_reminder', methods=['GET','POST'])
@role_required(['manager'])
def expire_soon_reminder():
    # get the member information if membership is about to expire
    cursor=get_cursor()
    query="SELECT  memberships.member_id,first_name,family_name\
                FROM memberships\
                JOIN member ON memberships.member_id=member.member_id \
                WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)\
                ORDER BY expiry_date, family_name,first_name"
    cursor.execute(query)
    all_member = cursor.fetchall()
    title='Membership Expiry Reminder'
    content="Dear {} {} <br>This is a friendly reminder that your membership is about to expire.\
         <br> Please take a moment to review your membership status and \
        consider renewing it to continue enjoying the benefits of being a member of our swimming club.\
        <br> You can view and renew your membership status <a href='{}'>here</a>."
    renew_url = url_for("member.view_membership")
    for member in all_member:
        today=datetime.today() 
        formatted_content =content.format(member['first_name'],member['family_name'],renew_url)
        cursor=get_cursor()
        cursor.execute("INSERT INTO reminders (member_id,title,content,date)\
                       VALUES (%s,%s,%s,%s)",(member['member_id'],title,formatted_content,today))
    return redirect(url_for('manager.view_membership_status'))

# this is the route send the reminder for membership has already expired
@manager_blueprint.route('/expired_reminder', methods=['GET','POST'])
@role_required(['manager'])
def expired_reminder():
    # get the member information if membership has already expired
    cursor=get_cursor()
    query="SELECT  memberships.member_id,first_name,family_name\
                FROM memberships\
                JOIN member ON memberships.member_id=member.member_id \
                WHERE expiry_date < CURDATE()\
                ORDER BY expiry_date, family_name,first_name"
    cursor.execute(query)
    all_member = cursor.fetchall()
    title='Membership Expiry Reminder'
    content="Dear {} {} <br>This is a friendly reminder that your membership has already expired.\
         <br> Please renew your membership to continue accessing the privileges of our swimming club.\
        <br> You can renew your membership <a href='{}'>here</a>."
    renew_url = url_for("member.view_membership")
    for member in all_member:
        today=datetime.today() 
        formatted_content =content.format(member['first_name'],member['family_name'],renew_url)
        cursor=get_cursor()
        cursor.execute("INSERT INTO reminders (member_id,title,content,date)\
                       VALUES (%s,%s,%s,%s)",(member['member_id'],title,formatted_content,today))
    return redirect(url_for('manager.view_membership_status'))


# this is the route send the reminder for pending payment
@manager_blueprint.route('/pending_payment_reminder', methods=['GET','POST'])
@role_required(['manager'])
def pending_payment_reminder():
    # get the pending payment
    cursor=get_cursor()
    query="SELECT payment_id,payments.member_id, first_name,family_name FROM payments \
                JOIN member ON payments.member_id = member.member_id\
                WHERE payment_status='pending'\
                ORDER BY date DESC, family_name,first_name"
    cursor.execute(query)
    all_member = cursor.fetchall()
    title='Pending Payment Reminder'
    content="Dear {} {} <br>This is a friendly reminder that you have pending payment to be paid.\
         <br>Please make the payment to continue the process of booking.\
        <br> You can make the payment <a href='{}'>here</a>."
    renew_url = url_for("member.my_booking")
    for member in all_member:
        today=datetime.today() 
        formatted_content =content.format(member['first_name'],member['family_name'],renew_url)
        cursor=get_cursor()
        cursor.execute("INSERT INTO reminders (member_id,title,content,date)\
                       VALUES (%s,%s,%s,%s)",(member['member_id'],title,formatted_content,today))
    return redirect(url_for('manager.view_payments'))

# this is the page to manage the prices
@manager_blueprint.route('/manage_price',methods=['GET','POST'])
@role_required(['manager'])
def manage_price():
    if request.method=='POST':
        if 'annually_btn' in request.form:
            id=request.form['annually_id']
            price = request.form['annually_price']
            cursor=get_cursor()
            cursor.execute("UPDATE subscription SET price=%s WHERE id=%s",(price,id))
            flash("Update price for annually subscription successfully.")
        elif 'monthly_btn' in request.form:
            id=request.form['monthly_id']
            price = request.form['monthly_price']
            cursor=get_cursor()
            cursor.execute("UPDATE subscription SET price=%s WHERE id=%s",(price,id))
            flash("Update price for monthly subscription successfully.")
        elif 'lesson_btn' in request.form:
            id=request.form['id']
            price = request.form['price']
            cursor=get_cursor()
            cursor.execute("UPDATE class SET price=%s WHERE class_id=%s",(price,id))
            flash("Update price for individual lesson successfully.")
        return redirect(url_for('manager.manage_price'))
    else:
        cursor=get_cursor()
        cursor.execute("SELECT id,type, price FROM subscription")
        all_subscriptions=cursor.fetchall()
        cursor.execute("SELECT class_id,type, price FROM class WHERE type='Individual Lesson'")
        lesson=cursor.fetchone()
        return render_template('manage_price.html', lesson=lesson,\
                            all_subscriptions=all_subscriptions)


# this is the page to manage the pool
@manager_blueprint.route('/manage_pool',methods=['GET','POST'])
@role_required(['manager'])
def manage_pool():
    if request.method=='POST':
        pool_name=request.form['pool_name']
        cursor=get_cursor()
        cursor.execute("INSERT INTO pool (name) VALUES (%s)",(pool_name,))
        flash("You have added a new swimming pool successfully.")
        return redirect(url_for('manager.manage_pool'))
    else:
        cursor=get_cursor()
        cursor.execute("SELECT pool_id,name FROM pool")
        all_pools=cursor.fetchall()
        return render_template('manage_pool.html', all_pools=all_pools)

@manager_blueprint.route('/edit_pool/<int:id>',methods=['GET','POST'])
@role_required(['manager'])
def edit_pool(id):
    if request.method=='POST':
        pool_input_name='pool'+str(id)
        pool_name=request.form[pool_input_name]
        cursor=get_cursor()
        cursor.execute("UPDATE pool SET name=%s WHERE pool_id=%s",(pool_name,id))
        flash("You have updated the swimming pool successfully.")
        return redirect(url_for('manager.manage_pool'))
    return redirect(url_for('manager.manage_pool'))


@manager_blueprint.route('/delete_pool/<int:id>',methods=['GET','POST'])
@role_required(['manager'])
def delete_pool(id):
    cursor=get_cursor()
    cursor.execute("SELECT * FROM schedules WHERE pool_id=%s",(id,))
    # check if this pool has already been used in timetable
    schedules=cursor.fetchall()
    if schedules:
        flash("This pool has been used in timetable. Failed to delete it.")
        return redirect(url_for('manager.manage_pool'))
    cursor.execute("DELETE FROM pool WHERE pool_id=%s",(id,))
    flash("You have deleted this swimming pool successfully.")
    return redirect(url_for('manager.manage_pool'))


#@manager_blueprint.route('/class_detail/<int:class_id>')
#def class_detail(class_id):
    #class_info = Class.query.get_or_404(class_id)
    #return render_template('class_detail.html', class_info=class_info)


@manager_blueprint.route('/manager/financial')
def manager_financial():
    return render_template('manager_financial.html')



@manager_blueprint.route('/income_statement', methods=['GET', 'POST'])
def income_statement():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Check if both start date and end date are provided
        if not start_date or not end_date:
            return "Date range is required. Please provide both start date and end date."

        # Convert start and end dates to datetime objects
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return redirect(url_for('wrong_date'))

        # Check if end date is not before start date
        if start_datetime > end_datetime:
            return "End date cannot be before start date. Please select valid dates."

        # Get the database cursor
        cursor = get_cursor()

        # Execute the query to fetch payments within the specified date range
        query = "SELECT type, amount FROM payments WHERE date BETWEEN %s AND %s AND payment_status = 'paid'"
        cursor.execute(query, (start_datetime, end_datetime))

        # Fetch the query results
        payments = cursor.fetchall()

        # Initialize variables for total amounts of lesson and subscription
        total_lesson = 0
        total_subscription = 0

        # Calculate total income for each type
        for payment in payments:
            if payment['type'] == 'lesson':
                total_lesson += payment['amount']
            elif payment['type'] == 'subscription':
                total_subscription += payment['amount']

        # Calculate total income as the sum of total lesson and total subscription
        total_income = total_lesson + total_subscription

        # Close the cursor and database connection
        cursor.close()


        return render_template('income_statement.html', total_income=total_income, total_lesson=total_lesson, total_subscription=total_subscription)

    else:
        year = datetime.now().year

        # Get the database cursor
        cursor = get_cursor()

        # Execute the query to fetch payments for the current year
        query = "SELECT type, amount FROM payments WHERE YEAR(date) = %s AND payment_status = 'paid'"
        cursor.execute(query, (year,))

        # Fetch the query results
        payments = cursor.fetchall()

        # Initialize variables for total amounts of lesson and subscription
        total_lesson = 0
        total_subscription = 0

        # Calculate total income for each type
        for payment in payments:
            if payment['type'] == 'lesson':
                total_lesson += payment['amount']
            elif payment['type'] == 'subscription':
                total_subscription += payment['amount']

        # Calculate total income as the sum of total lesson and total subscription
        total_income = total_lesson + total_subscription

        # Close the cursor and database connection
        cursor.close()


        return render_template('income_statement.html', total_income=total_income, total_lesson=total_lesson, total_subscription=total_subscription)











@manager_blueprint.route('/class_statement')
def class_statement():
    try:
        # Initialize a dictionary to store the booking counts for each class
        class_booking_counts = {}

        # Get the database cursor
        cursor = get_cursor()

        # Execute query to fetch all paid bookings
        cursor.execute("SELECT class_id FROM bookings WHERE payment_status = 'paid'")
        paid_bookings = cursor.fetchall()

        # Update booking counts for each class based on paid bookings
        for booking in paid_bookings:
            class_id = booking['class_id']
            cursor.execute("SELECT name FROM class WHERE class_id = %s", (class_id,))
            class_name = cursor.fetchone()['name']
            class_booking_counts[class_name] = class_booking_counts.get(class_name, 0) + 1

        # Get all class names
        cursor.execute("SELECT name FROM class")
        all_classes = cursor.fetchall()

        # Close the cursor and database connection
        cursor.close()

        # Initialize booking counts for all classes to 0
        for class_name in all_classes:
            class_name = class_name['name']
            if class_name not in class_booking_counts:
                class_booking_counts[class_name] = 0

        # Extract class names and booking counts from the dictionary
        class_names = list(class_booking_counts.keys())
        booking_counts = list(class_booking_counts.values())

        return render_template('class_statement.html', class_names=class_names, booking_counts=booking_counts)

    except Exception as e:
        # Handle exceptions
        return str(e)





@manager_blueprint.route('/view_payments',methods=['GET','POST'])
@role_required(['manager'])
def view_payments():
    cursor=get_cursor()
    # get all the payments
    cursor.execute("SELECT COUNT(*) AS number FROM payments WHERE amount !=0")
    payment_number=cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM payments WHERE type='subscription'")
    sub_payment_number = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM payments WHERE type='lesson' AND amount !=0")
    lesson_payment_number = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS number FROM payments WHERE payment_status='pending'")
    pending_payment_number= cursor.fetchone()   
    return render_template('view_payments.html',payment_number=payment_number,\
            sub_payment_number=sub_payment_number, \
            lesson_payment_number=lesson_payment_number,pending_payment_number=pending_payment_number )

@manager_blueprint.route('/payment_filter',methods=['GET','POST'])
@role_required(['manager'])
def payment_filter():
    if request.method=='POST':
        # show the membership status according to the filter
        filter_value=request.form['filter']
        if filter_value == 'all_payments':
            query="SELECT payment_id, first_name,family_name, type,\
                date,amount,payment_status FROM payments \
                JOIN member ON payments.member_id = member.member_id\
                WHERE amount !=0\
                ORDER BY date DESC, family_name,first_name"
        elif filter_value == 'sub_payments':
            query="SELECT payment_id, first_name,family_name, type,\
                date,amount,payment_status FROM payments \
                JOIN member ON payments.member_id = member.member_id\
                WHERE type='subscription'\
                ORDER BY date DESC, family_name,first_name"
        elif filter_value == 'lesson_payments':
            query="SELECT payment_id, first_name,family_name, type,\
                date,amount,payment_status FROM payments \
                JOIN member ON payments.member_id = member.member_id\
                WHERE type='lesson' AND amount !=0\
                ORDER BY date DESC, family_name,first_name"
        elif filter_value == 'pending_payments':
            query="SELECT payment_id, first_name,family_name, type,\
                date,amount,payment_status FROM payments \
                JOIN member ON payments.member_id = member.member_id\
                WHERE payment_status='pending'\
                ORDER BY date DESC, family_name,first_name"
        cursor=get_cursor()
        cursor.execute(query)
        all_payments = cursor.fetchall()
        response=render_template('payment_response.html',all_payments=all_payments)
        return response
    return redirect(url_for('manager.view_payments'))
