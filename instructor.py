from flask import Blueprint, render_template, redirect, url_for,\
    session, request, flash, jsonify
from flask_hashing import Hashing
from config import get_cursor, allowed_file, UPLOAD_FOLDER, is_image_exist,TIMESLOTS
import re
import os
from datetime import datetime, timedelta
from auth import role_required
from werkzeug.utils import secure_filename

# create instructor blueprint view
instructor_blueprint = Blueprint('instructor', __name__)
#create an instance of hashing
hashing = Hashing()
 


# this is the home page for instructor
@instructor_blueprint.route('/')
# check if the role is instructor, only instructor role can access this page
@role_required(['instructor'])
def instructor():
    return render_template('instructor_dashboard.html',active='dashboard') 


# this is the profile page for instructor
@instructor_blueprint.route('/profile')
# check if the role is instructor, only instructor role can access this page
@role_required(['instructor'])
def profile():
    account_id=session['id']
    cursor=get_cursor()
    # get the information of instructor
    cursor.execute("SELECT * FROM instructor AS i\
            JOIN account AS a on i.account_id=a.account_id\
            WHERE a.account_id= %s", (account_id,))
    instructor=cursor.fetchone()
    cursor.execute("SELECT * FROM class WHERE status='active'")
    all_classes=cursor.fetchall()
    return render_template('instructorprofile.html',instructor= instructor,\
            all_classes=all_classes,active='account') 

# update the instructor's own profile 
@instructor_blueprint.route('/updateprofile', methods=['GET','POST'])
@role_required(['instructor'])
def update_profile():
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
        # get the old_image_name for removing the old image  
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
                    # save new image to the local folder
                    new_image.save(os.path.join(UPLOAD_FOLDER, image_name))
                    # remove the old image
                    os.remove(os.path.join(UPLOAD_FOLDER, old_image_name))
                # raise a notice if the new image type is not allowed
                elif new_image.filename and not allowed_file(new_image.filename):
                    message='Please upload images in type of jpg, png and jpeg.'
                    flash(message)
                    return redirect(url_for('instructor.profile'))
            cursor=get_cursor()
            # update the instructor profile
            sql_query="UPDATE instructor SET title=%s,first_name=%s,family_name=%s,position=%s,\
                phone=%s,email=%s,profile=%s,expert_area=%s,image=%s WHERE instructor_id=%s"
            cursor.execute(sql_query, (title,first_name,family_name,position,phone,email,\
                profile,expert_area,image_name,instructor_id))
            flash('You have successfully updated your profile')
    return redirect(url_for('instructor.profile'))

# update the instructor's own password 
@instructor_blueprint.route('/updatepassword', methods=['GET','POST'])
@role_required(['instructor'])
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
    return redirect(url_for('instructor.profile'))

@instructor_blueprint.route('/timeschedule', methods=['GET','POST'])
@role_required(['instructor'])
def time_schedule():
    account_id=session['id']
    cursor=get_cursor()
    cursor.execute("SELECT * FROM instructor AS i\
            JOIN account AS a on i.account_id=a.account_id\
            WHERE a.account_id= %s", (account_id,))
    instructor=cursor.fetchone()
    cursor.execute("SELECT id, day,start_time,end_time FROM available_time \
        WHERE instructor_id=%s ORDER BY FIELD(day, 'Monday', \
        'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),start_time",\
        (instructor['instructor_id'],))
    available_time=cursor.fetchall()
    return render_template('instructorschedule.html',active='time_schedule',available_time=available_time)


@instructor_blueprint.route('/addtimeschedule', methods=['GET','POST'])
@role_required(['instructor'])
def add_time_schedule():
    if request.method=="POST":
        account_id=session['id']
        cursor=get_cursor()
        cursor.execute("SELECT * FROM instructor AS i\
            JOIN account AS a on i.account_id=a.account_id\
            WHERE a.account_id= %s", (account_id,))
        instructor=cursor.fetchone()
        dayofweek=request.form['dayofweek']
        start_time=request.form['start_time']
        end_time=request.form['end_time']
        if start_time<end_time:
            cursor.execute("INSERT INTO available_time (instructor_id,day,start_time,end_time)\
                VALUE (%s,%s,%s,%s)", (instructor['instructor_id'],dayofweek,start_time,end_time))
        else:
            flash('The end time must be later than the start time!')
    return render_template('instructorscheduleform.html',active='time_schedule',timeslots=TIMESLOTS )

@instructor_blueprint.route('/edittimeschedule/<int:id>', methods=['GET','POST'])
@role_required(['instructor'])
def edit_time_schedule(id):
    if request.method=="POST":
        dayofweek=request.form['dayofweek']
        start_time=request.form['start_time']
        end_time=request.form['end_time']
        if start_time<end_time:
            cursor=get_cursor()
            cursor.execute("UPDATE available_time SET day=%s,start_time=%s,\
                end_time=%s WHERE id=%s", (dayofweek,start_time,end_time,id))
        else:
            flash('The end time must be later than the start time!')
        return redirect(url_for('instructor.time_schedule'))
    cursor=get_cursor()
    cursor.execute("SELECT * FROM available_time WHERE id=%s",(id,))
    time=cursor.fetchone()
    return render_template('instructorscheduledetail.html',active='time_schedule',time=time,timeslots=TIMESLOTS )

@instructor_blueprint.route('/deletetimeschedule/<int:id>', methods=['GET','POST'])
@role_required(['instructor'])
def delete_time_schedule(id):
    cursor=get_cursor()
    cursor.execute("DELETE FROM available_time WHERE id=%s",(id,))
    return redirect(url_for('instructor.time_schedule'))








@instructor_blueprint.route('/timetable', methods=['GET','POST'])
@role_required(['instructor'])
def view_timetable():

    cursor = get_cursor()
    cursor.execute("SELECT DISTINCT name FROM class WHERE status = 'active' ORDER BY name")
    classes = cursor.fetchall()  
    cursor.execute("""
        SELECT instructor_id, first_name, family_name
        FROM instructor
        WHERE status = 'active'
        ORDER BY family_name, first_name
    """)
    instructors = [{'full_name': f"{instructor['first_name']} {instructor['family_name']}"} for instructor in cursor.fetchall()]

    day = request.args.get('day', None)
    class_name = request.args.get('class_name', None)
    instructor_name = request.args.get('instructor_name', None)

    conditions = ["s.status = 'active'"]  
    parameters = []

    if day:
        conditions.append("s.day = %s")
        parameters.append(day)
    if class_name:
        conditions.append("c.name LIKE %s")
        parameters.append(f"%{class_name}%")
    if instructor_name:
        conditions.append("CONCAT(i.first_name, ' ', i.family_name) LIKE %s")
        parameters.append(f"%{instructor_name}%")

    condition_str = " AND ".join(conditions)

    query = f"""
        SELECT s.schedule_id, s.day, c.name AS class_name, s.start_time, s.end_time,
        p.name AS pool_name, l.name AS lane_name, 
        CONCAT(i.first_name, ' ', i.family_name) AS instructor_name,
        c.description, c.image
        FROM schedules AS s
        JOIN class AS c ON s.class_id = c.class_id
        LEFT JOIN pool AS p ON s.pool_id = p.pool_id
        LEFT JOIN lane AS l ON s.lane_id = l.lane_id
        JOIN instructor AS i ON s.instructor_id = i.instructor_id
        WHERE {condition_str}
        ORDER BY s.day, s.start_time
    """
    cursor.execute(query, tuple(parameters))
    
    all_schedules = cursor.fetchall()
    
    for schedule in all_schedules:
        print(schedule['description']) 
        schedule['image_path'] = f'/static/images/{schedule["image"]}'

    return render_template('instructor_alltimetable.html', all_schedules=all_schedules, classes=classes, instructors=instructors)




@instructor_blueprint.route('/get_week_classes', methods=['GET','POST'])
@role_required(['instructor'])
def get_week_classes():
    cursor = None
    start_day_str = request.args.get('start_day', default="")
    end_day_str = request.args.get('end_day', default="")
    class_name = request.args.get('class_name', default="")
    instructor_name = request.args.get('instructor_name', default="")

    if not start_day_str or not end_day_str:
        return jsonify([])

    try:
        start_date = datetime.strptime(start_day_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_day_str, '%Y-%m-%d') + timedelta(days=1)

        week_days = [(start_date + timedelta(days=i)).strftime('%A').upper() for i in range((end_date - start_date).days)]
        
        cursor = get_cursor()

        placeholders = ','.join(['%s' for _ in week_days])
        params = week_days

        if class_name:
            params.append(f'%{class_name}%')
        if instructor_name:
            params.append(f'%{instructor_name}%')

        class_name_condition = "AND c.name LIKE %s" if class_name else ""
        instructor_name_condition = "AND CONCAT(i.first_name, ' ', i.family_name) LIKE %s" if instructor_name else ""

        query = f"""
        SELECT s.schedule_id, s.day, c.name AS class_name,
        TIME_FORMAT(s.start_time, '%H:%i') AS start_time,
        TIME_FORMAT(s.end_time, '%H:%i') AS end_time,
        p.name AS pool_name, l.name AS lane_name,
        CONCAT(i.first_name, ' ', i.family_name) AS instructor_name,
        (s.capacity - COUNT(b.schedule_id)) AS class_capacity
        FROM schedules AS s
        LEFT JOIN bookings AS b ON s.schedule_id = b.schedule_id AND b.class_date = s.day
        JOIN class AS c ON s.class_id = c.class_id
        LEFT JOIN pool AS p ON s.pool_id = p.pool_id
        LEFT JOIN lane AS l ON s.lane_id = l.lane_id
        JOIN instructor AS i ON s.instructor_id = i.instructor_id
        WHERE s.day IN ({placeholders})
        {class_name_condition}
        {instructor_name_condition}
        AND s.status = 'active'
        GROUP BY s.schedule_id, s.day
        ORDER BY FIELD(s.day, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'), s.start_time
        """

        cursor.execute(query, params)
        classes = cursor.fetchall()
        
        return jsonify(classes)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify([]), 500
    finally:
        if cursor:
            cursor.close()




@instructor_blueprint.route('/mytimetable', methods=['GET'])
@role_required(['instructor'])
def mytimetable():
    account_id = session['id']
    cursor = get_cursor()
    try:
        # Get the instructor id using account id
        cursor.execute("SELECT * FROM instructor AS i\
                JOIN account AS a on i.account_id=a.account_id\
                WHERE a.account_id= %s", (account_id,))
        instructor = cursor.fetchone()
        instructor_id = instructor['instructor_id']
        # Retrieve all schedules with class details
        cursor.execute('''SELECT s.schedule_id, s.start_time, s.end_time, s.day, s.pool_id, s.lane_id, s.class_id,
                       c.name AS class_name, c.duration AS class_duration, c.type AS class_type,
                       CONCAT_WS(' ', i.first_name, i.family_name) AS instructor_name,
                       p.name AS pool_name, l.name AS lane_name
                        FROM schedules s
                        LEFT JOIN class c ON s.class_id = c.class_id
                        LEFT JOIN instructor i ON s.instructor_id = i.instructor_id
                        LEFT JOIN pool AS p ON s.pool_id = p.pool_id
                        LEFT JOIN lane AS l ON s.lane_id = l.lane_id
                        WHERE s.instructor_id = %s
                        ORDER BY s.day, s.start_time''', (instructor_id,))
        my_timetable = cursor.fetchall()

        return render_template('instructor_mytimetable.html', my_timetable=my_timetable, active='timetable')
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()


@instructor_blueprint.route('/view_mytimetable', methods=['GET','POST'])
@role_required(['instructor'])
def view_mytimetable():
    account_id = session['id']
    cursor = get_cursor()
    try:
        # Get the instructor id using account id
        cursor.execute("SELECT * FROM instructor AS i\
                JOIN account AS a on i.account_id=a.account_id\
                WHERE a.account_id= %s", (account_id,))
        instructor = cursor.fetchone()
        instructor_id = instructor['instructor_id']
        # Retrieve all schedules with class details
        cursor.execute('''SELECT s.schedule_id, s.start_time, s.end_time, s.day, s.pool_id, s.lane_id, s.class_id,
                       c.name AS class_name, c.duration AS class_duration, c.type AS class_type,
                       CONCAT_WS(' ', i.first_name, i.family_name) AS instructor_name,
                       p.name AS pool_name, l.name AS lane_name
                        FROM schedules s
                        LEFT JOIN class c ON s.class_id = c.class_id
                        LEFT JOIN instructor i ON s.instructor_id = i.instructor_id
                        LEFT JOIN pool AS p ON s.pool_id = p.pool_id
                        LEFT JOIN lane AS l ON s.lane_id = l.lane_id
                        WHERE s.instructor_id = %s
                        ORDER BY s.day, s.start_time''', (instructor_id,))
        my_timetable = cursor.fetchall()
        
        # Convert schedule data to list of dictionaries
        timetable_data = []
        for schedule in my_timetable:
            timetable_data.append({
                'schedule_id': schedule['schedule_id'],
                'day': schedule['day'],
                'start_time': str(schedule['start_time']),
                'end_time': str(schedule['end_time']),
                'class_name': schedule['class_name'],
                'instructor_name': schedule['instructor_name'],
                'pool_name': schedule['pool_name'],
                'lane_name': schedule['lane_name'],
                'class_type': schedule['class_type']
            })

        return jsonify(timetable_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify([]), 500
    finally:
        cursor.close()


@instructor_blueprint.route('/booking_info/<int:schedule_id>', methods=['GET'])
@role_required(['instructor'])
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
                       ORDER BY b.class_date DESC
                     ''', (schedule_id,))
    attendees = cursor.fetchall()


    current_date = datetime.now().date()

    return render_template('instructor_bookinginfo.html', class_info=class_info, attendees=attendees, schedule_id=schedule_id, current_date=current_date, active='time_table')



@instructor_blueprint.route('/record_attendance/<int:schedule_id>', methods=['GET', 'POST'])
@role_required(['instructor'])
def record_attendance(schedule_id):
    cursor = get_cursor()

    if request.method == 'POST':
        cursor.execute("SELECT booking_id FROM bookings WHERE schedule_id = %s ", (schedule_id,))
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
        return redirect(url_for('instructor.booking_info', schedule_id=schedule_id))

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


        return render_template('instructor_attendance.html', members=members, current_date=current_date, schedule_id=schedule_id)





# Instructor view news categorised by titles
@instructor_blueprint.route('/view_news', methods=['GET'])
# Check if the role is instructor, only instructor role can access this page
@role_required(['instructor'])
def view_news():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM news")
    news = cursor.fetchall()
    return render_template('instructor_view_news.html', news=news)

# Instructor search news by keyword
@instructor_blueprint.route('/search_news', methods=['GET', 'POST'])
# Check if the role is instructor, only instructor role can access this page
@role_required(['instructor'])
def search_news():
    if request.method == 'POST':
        search_keyword = request.form['search_keyword']
        cursor = get_cursor()
        # Assuming 'title' and 'content' are the columns to search for keywords
        cursor.execute("SELECT * FROM news WHERE title LIKE %s OR content LIKE %s", (f'%{search_keyword}%', f'%{search_keyword}%'))
        news = cursor.fetchall()
        return render_template('instructor_view_news.html', news=news, search_keyword=search_keyword)
    else:
        return render_template('instructor_view_news.html')
