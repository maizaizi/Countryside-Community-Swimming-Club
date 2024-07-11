from flask import Blueprint, render_template, redirect, url_for,\
    session, request, flash, jsonify
from flask_hashing import Hashing
from config import get_cursor, get_user_id, allowed_file,UPLOAD_FOLDER
from werkzeug.utils import secure_filename
from zoneinfo import ZoneInfo 
import re
import os
from datetime import date


from auth import role_required
from datetime import datetime,date,timedelta
#the folder for the uploaded images, this is for the local app
# create the member blueprint view
member_blueprint = Blueprint('member', __name__)

# create an instance of hashing
hashing = Hashing()


@member_blueprint.route('/')
@role_required(['member'])
def member():
    account_id=session['id']
    member_id=get_user_id(account_id)
    cursor=get_cursor()
    cursor.execute("SELECT COUNT(*) AS number FROM reminders \
                   WHERE member_id=%s AND status='unread'",\
                   (member_id,))
    unread_number=cursor.fetchone()
    return render_template('member_dashboard.html',unread_number=unread_number,active='dashboard') 

@member_blueprint.route('/memberdetail/<int:member_id>')
@role_required(['member'])
def get_member_detail(member_id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM member WHERE member_id = %s", (member_id,))
    member = cursor.fetchone()
    cursor.execute("SELECT * FROM account AS a\
            JOIN member AS m ON a.account_id = m.account_id\
            WHERE member_id= %s", (member_id,))
    account=cursor.fetchone()
    return render_template('member_profile.html', member= member,account=account,active='members')

@member_blueprint.route('/profile', methods=['GET', 'POST'])
@role_required(['member'])
def profile():
    account_id = session['id']
    if request.method == 'POST':
        # Extract data from the form
        member_id=request.form['member_id']
        title = request.form['title']
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        position = request.form['position']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        dob = request.form['dob']
        health_info = request.form['health_info']

        # Get the old image name
        old_image_name=request.form['old_image']
        image_name = old_image_name

        # Get the new image 
        new_image = request.files['new_image']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            # flash message 
            flash('Invalid email address!')
        else:
            if allowed_file(new_image.filename):
                # Change the image name to a secure name
                    secure_image_name = secure_filename(new_image.filename)
                # Create a unique name for the image
                    image_name = datetime.now().strftime("%d%m%Y%H%M%S") + '_' + secure_image_name
                # Save image to the local folder
                    new_image.save(os.path.join(UPLOAD_FOLDER, image_name))
                # If the old image is not null, remove the old image
                    if old_image_name:
                        os.remove(os.path.join(UPLOAD_FOLDER, old_image_name))
        
            elif new_image.filename and not allowed_file(new_image.filename):
                flash('Please upload images in type of jpg, png, and jpeg.')
                return redirect(url_for('member.profile',member_id=member_id))

        cursor = get_cursor()
        # Update the member profile
        sql_query = """
        UPDATE member
        SET title = %s, first_name = %s, family_name = %s, position = %s, 
        phone = %s, email = %s, address = %s, dob = %s, image = %s, health_info = %s
        WHERE account_id = %s
        """
        cursor.execute(sql_query, (title, first_name, family_name, position, phone, email, address, dob, image_name, health_info, account_id))

        message = 'Your profile has been updated.'
        flash(message)

        # Get the updated member data
        cursor.execute("SELECT * FROM member WHERE account_id = %s", (account_id,))
        member_data = cursor.fetchone()
        cursor.execute("SELECT * FROM account WHERE account_id = %s", (account_id,))
        account_data = cursor.fetchone()
        return render_template('member_profile.html', member=member_data,account=account_data)
    
    else:
        # get the member profile
        cursor = get_cursor()
        cursor.execute("SELECT * FROM member WHERE account_id= %s", (account_id,))
        member_data = cursor.fetchone()

        cursor.execute("SELECT * FROM account WHERE account_id = %s", (account_id,))
        account_data = cursor.fetchone()
        
        return render_template('member_profile.html',active='account', member=member_data, account=account_data)
    
# change the member's password
@member_blueprint.route('/updatememberpassword', methods=['POST'])
@role_required(['member'])
def update_member_password():
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
            message='You have successfully updated your password.'
            flash(message)
           
    return redirect(url_for('member.profile'))


@member_blueprint.route('/viewinstructors', methods=['GET'])
@role_required(['member'])
def view_instructors():
    cursor = get_cursor()

    cursor.execute("SELECT instructor_id, title, first_name, family_name, \
                    position, phone, email, profile, expert_area, image, status \
                    FROM instructor ORDER BY family_name, first_name")
    instructor_list = cursor.fetchall()

    instructor_lessons = {}

    for instructor in instructor_list:
        instructor_id = instructor['instructor_id']
        cursor.execute("SELECT schedules.*,pool.name as pool_name, class.name as class_name FROM schedules \
                        JOIN class ON schedules.class_id = class.class_id \
                        JOIN pool ON schedules.pool_id=pool.pool_id\
                        WHERE instructor_id = %s ORDER BY day", (instructor_id,))
        lessons = cursor.fetchall()
        instructor_lessons[instructor_id] = lessons

    return render_template('member_view_instructors.html', instructor_list=instructor_list, instructor_lessons=instructor_lessons, active='instructors')

@member_blueprint.route('/searchinstructor', methods=['GET','POST'])
# check if the role is manager, only manager role can access this page
@role_required(['member'])
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
        return render_template('member_view_instructors.html', instructor_list=instructor_list,active='members') 
     


@member_blueprint.route('/manage_subscription', methods=['GET', 'POST'])
@role_required(['member'])
def manage_subscription():
    if request.method == 'POST':
        if 'renew_subscription' in request.form:  # To renew subscription
            member_id = session['id']
            cursor = get_cursor()
            # Renew subscription logic here
            flash('Subscription renewed successfully.')  # Optionally provide a success message
            return redirect(url_for('member.manage_subscription'))

    if 'id' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in
    
    member_id = session['id']
    cursor = get_cursor()
    cursor.execute("SELECT expiry_date FROM memberships WHERE member_id = %s", (member_id,))
    dates = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT date, amount, type FROM payment WHERE member_id = %s", (member_id,))
    history = cursor.fetchall()
    return render_template('manage_subscription.html', dates=dates, history=history)


@member_blueprint.route('/view_class')
@role_required(['member'])
def view_class():
    cursor = get_cursor()

    cursor.execute("SELECT * FROM class")
    all_classes = cursor.fetchall()
    class_schedules = {}
    for class_info in all_classes:
        class_id = class_info['class_id']
        cursor.execute("SELECT * FROM schedules AS s JOIN pool AS p ON s.pool_id=p.pool_id\
                       JOIN instructor AS i ON s.instructor_id=i.instructor_id\
                       WHERE class_id = %s ORDER BY day, start_time", (class_id,))
        schedules = cursor.fetchall()
        class_schedules[class_id] = schedules

    return render_template('member_view_class.html', all_classes=all_classes, class_schedules=class_schedules)


@member_blueprint.route('/member_timetable', methods=['GET'])
@role_required(['member'])
def member_timetable():
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


    conditions = ["s.status = 'active'"]  # Ensure active status
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
    CONCAT(i.first_name, ' ', i.family_name) AS instructor_name
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

    return render_template('member_view_timetable.html', active='booking',\
        all_schedules=all_schedules, classes=classes, instructors=instructors)




weekdays_mapping = {
    0: 'MONDAY',
    1: 'TUESDAY',
    2: 'WEDNESDAY',
    3: 'THURSDAY',
    4: 'FRIDAY',
    5: 'SATURDAY',
    6: 'SUNDAY',
}

@member_blueprint.route('/get_classes')
@role_required(['member'])
def get_classes():
    day_str = request.args.get('day', default="")
    class_name = request.args.get('class_name', default="")
    instructor_name = request.args.get('instructor_name', default="")
    
    if day_str.lower() in ['null', 'undefined']:
        day_str = None
    
    if class_name.lower() == 'undefined':
        class_name = ""
    
    if instructor_name.lower() == 'undefined':
        instructor_name = ""
    
    if day_str:
        try:
            date_obj = datetime.strptime(day_str, '%Y-%m-%d').replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Pacific/Auckland'))
            weekday = date_obj.weekday()
            day_of_week = weekdays_mapping[weekday]
        except ValueError:
            return jsonify([])  
    else:
        return jsonify([])
    
    cursor = None
    try:
        cursor = get_cursor()

        query = """
        SELECT s.schedule_id, s.day, c.name AS class_name,
        TIME_FORMAT(s.start_time, '%H:%i') AS start_time,
        TIME_FORMAT(s.end_time, '%H:%i') AS end_time,
        p.name AS pool_name, l.name AS lane_name,
        CONCAT(i.first_name, ' ', i.family_name) AS instructor_name,
        (s.capacity-COUNT(b.schedule_id)) AS class_capacity
        FROM schedules AS s
        LEFT JOIN bookings AS b on s.schedule_id=b.schedule_id and  b.class_date >= CURDATE()
        AND b.class_date < DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        JOIN class AS c ON s.class_id = c.class_id
        LEFT JOIN pool AS p ON s.pool_id = p.pool_id
        LEFT JOIN lane AS l ON s.lane_id = l.lane_id
        JOIN instructor AS i ON s.instructor_id = i.instructor_id
        WHERE s.day = %s
        AND (%s = '' OR c.name LIKE %s)
        AND (%s = '' OR CONCAT(i.first_name, ' ', i.family_name) LIKE %s)
        AND s.status = 'active'  
        GROUP BY s.schedule_id
        ORDER BY s.day, s.start_time
        """
        cursor.execute(query, (day_of_week, class_name, f'%{class_name}%' if class_name != 'undefined' else '', instructor_name, f'%{instructor_name}%' if instructor_name != 'undefined' else ''))
        classes = cursor.fetchall()

        classes_serializable = [{
            'schedule_id': cls['schedule_id'],
            'day': cls['day'],
            'class_name': cls['class_name'],
            'start_time': cls['start_time'],  
            'end_time': cls['end_time'],
            'pool_name': cls['pool_name'],
            'lane_name': cls['lane_name'],
            'instructor_name': cls['instructor_name'],
            'class_capacity': cls['class_capacity'] 
        } for cls in classes]

    finally:
        if cursor is not None:
            cursor.close()
    
    return jsonify(classes_serializable)



def day_to_weekday(day):
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    return days.index(day)
def find_next_class_date(selected_date, scheduled_weekday):
    selected_date_dt = datetime.strptime(selected_date, "%Y-%m-%d")
    selected_weekday = selected_date_dt.weekday()
    days_until_next_class = (scheduled_weekday - selected_weekday) % 7
    
    class_date = selected_date_dt + timedelta(days=days_until_next_class)
    return class_date.strftime("%Y-%m-%d")

@member_blueprint.route('/book_timetable/<int:schedule_id>', methods=['POST'])
@role_required(['member'])
def book_timetable(schedule_id):
    response = {'status': '', 'message': ''}
    try:
        data = request.get_json()
        selected_date = data.get('selected_date') if data else None

        if not selected_date:
            response['status'] = 'error'
            response['message'] = 'Selected date is required.'
            return jsonify(response), 400

        account_id = session['id']
       
        cursor = get_cursor()
        cursor.execute("""
            SELECT m.member_id, mem.expiry_date 
            FROM member m 
            JOIN memberships mem ON m.member_id = mem.member_id 
            WHERE m.account_id = %s 
            AND mem.expiry_date >= CURDATE()
        """, (account_id,))
        membership_result = cursor.fetchone()

        if not membership_result:
            response['status'] = 'redirect'
            response['message'] = 'Your membership has expired or is inactive. Please renew to book classes.'
            response['redirect_url'] = '/member/renew_membership'
            return jsonify(response)

        cursor.execute("""
            SELECT s.class_id, s.instructor_id, s.start_time, s.end_time, s.day, c.type AS class_type, c.price AS class_price
            FROM schedules s 
            JOIN class c ON s.class_id = c.class_id 
            WHERE s.schedule_id = %s
        """, (schedule_id,))
        schedule_result = cursor.fetchone()

        if schedule_result:
            scheduled_weekday = day_to_weekday(schedule_result['day'])
            class_date = find_next_class_date(selected_date, scheduled_weekday)
            cursor = get_cursor()
            cursor.execute("""
            SELECT s.schedule_id,(s.capacity-COUNT(b.schedule_id)) AS class_capacity
            FROM schedules AS s
            LEFT JOIN bookings AS b on s.schedule_id=b.schedule_id AND  b.class_date >= CURDATE()
            AND b.class_date < DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            WHERE s.schedule_id=%s""",(schedule_id,))
            capacity=cursor.fetchone()
            cursor.execute("""
                SELECT * 
                FROM bookings 
                WHERE member_id = %s 
                AND schedule_id = %s AND class_date >= CURDATE()
                AND class_date < DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            """, (membership_result['member_id'], schedule_id))
            already_booked=cursor.fetchone()
            selected_date_format=datetime.strptime(selected_date, '%Y-%m-%d').date()
            if membership_result['expiry_date']<selected_date_format:
                response['status'] = 'redirect'
                response['message'] = 'Your membership has expired for booking this class. Please renew to book classes.'
                response['redirect_url'] = '/member/renew_membership'
                return jsonify(response)
            if already_booked:
                response['status'] = 'error'
                response['message'] = 'You have already booked this class.'
            else:
                if capacity['class_capacity']:

                    booking_status, payment_status = ('confirmed', 'paid') if schedule_result['class_type'] == 'Group Class' else ('pending', 'pending')
                    payment_amount = schedule_result['class_price']  
                    cursor = get_cursor()
                    cursor.execute("""
                        INSERT INTO bookings (member_id, class_id, instructor_id, schedule_id, class_date, start_time, end_time, booking_status, payment_status, payment_amount) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (membership_result['member_id'], schedule_result['class_id'], schedule_result['instructor_id'], schedule_id, class_date, schedule_result['start_time'], schedule_result['end_time'], booking_status, payment_status, payment_amount))
                    booking_id = cursor.lastrowid 
                    cursor.execute("""
                        INSERT INTO payments (type, member_id, booking_id, date, amount, payment_status) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, ('lesson', membership_result['member_id'], booking_id, selected_date, schedule_result['class_price'], payment_status))
                    response['status'] = 'success'
                    response['message'] = 'Class booked successfully.'

                else:
                    response['status'] = 'error'
                    response['message'] = 'This class is fully booked, please choose another one.'
                    
        else:
            response['status'] = 'error'
            response['message'] = 'Failed to find the class for this schedule.'
    except Exception as e:
        response['status'] = 'error'
        response['message'] = f'Failed to book class. Please try again later. Error: {str(e)}'

    return jsonify(response)



@member_blueprint.route('/my_booking')
@role_required(['member'])  
def my_booking():
   
    try:
        account_id = session.get('id')
        cursor = get_cursor()
        cursor.execute("SELECT member_id FROM member WHERE account_id = %s", (account_id,))
        result = cursor.fetchone()

        if result:
            member_id = result['member_id']
            cursor.execute("SELECT * FROM bookings WHERE member_id = %s ORDER BY class_date DESC", (member_id,))
            bookings = cursor.fetchall()
            
            if bookings:
                booked_classes = []
                for booking in bookings:
                    class_date = booking['class_date']
                    if class_date < date.today():
                        cursor.execute("UPDATE bookings SET booking_status = 'completed' WHERE booking_id = %s", (booking['booking_id'],))
                    cursor.execute("""
                                   SELECT c.*, b.class_date, b.booking_status, s.start_time, s.end_time, CONCAT(i.first_name, ' ', i.family_name) AS instructor_name
                                   FROM bookings b
                                   INNER JOIN schedules s ON b.schedule_id = s.schedule_id
                                   INNER JOIN class c ON s.class_id = c.class_id
                                   INNER JOIN instructor i ON s.instructor_id = i.instructor_id
                                   WHERE b.booking_id = %s
                                   """, (booking['booking_id'],))
                    schedule_info = cursor.fetchone()
                    if schedule_info:
                        booked_classes.append({
                            'class_name': schedule_info['name'],
                            'class_type': schedule_info['type'],
                            'time': f"{schedule_info['start_time']} - {schedule_info['end_time']}",
                            'class_image': schedule_info['image'],
                            'class_date': schedule_info['class_date'],
                            'instructor': schedule_info['instructor_name'],
                            'price': schedule_info['price'],
                            'class_id': schedule_info['class_id'],
                            'booking_id': booking['booking_id'],
                            'booking_status': schedule_info['booking_status'],
                            'class_id': schedule_info['class_id']

                            })
                        
                return render_template('member_check_booking.html', booked_classes=booked_classes)
            else:
      
                flash('You have not booked any classes yet.', 'info')
                return render_template('member_check_booking.html', booked_classes=[])  
        else:
      
            flash('Member ID not found.', 'error')
            return render_template('member_check_booking.html', booked_classes=[]) 

    except Exception as e:
        flash('Failed to fetch booking information. Please try again later.', 'error')
        print("Error fetching booking information:", str(e))

        return render_template('member_check_booking.html', booked_classes=[])

@member_blueprint.route('/cancel_booking/<int:booking_id>', methods=['GET', 'POST'])
def cancel_booking(booking_id):
    try:
        cursor = get_cursor()
        cursor.execute("SELECT schedule_id FROM bookings WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            raise ValueError("Booking not found")

        delete_query = "DELETE FROM bookings WHERE booking_id = %s"
        cursor.execute(delete_query, (booking_id,))


        cursor.close()
        return jsonify({'success': True, 'message': 'Booking canceled successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to cancel booking. Please try again later.'})




@member_blueprint.route('/show_payment_form/<int:booking_id>')
@role_required(['member'])
def show_payment_form(booking_id):
    try:
        cursor = get_cursor()
        cursor.execute("SELECT payment_status, class_id FROM bookings WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()
        
        if booking['payment_status'] == 'paid':
            flash('This booking has already been paid for. No further payment is required.', 'success')
            return redirect(url_for('member.my_booking')) 
        else:
            cursor.execute("SELECT price FROM class WHERE class_id = %s", (booking['class_id'],))
            class_info = cursor.fetchone()
            price = class_info['price'] if class_info else 'N/A'
            
            return render_template('member_lesson_payment.html', booking_id=booking_id, class_id=booking['class_id'], price=price)
    except Exception as e:
        flash('Failed to load payment information. Please try again later.', 'error')
        print(e) 
        return redirect(url_for('member.my_booking'))  
    finally:
        if cursor:
            cursor.close()

    
    
@member_blueprint.route('/lesson_payment', methods=['POST'])
@role_required(['member'])
def lesson_payment():
    try:
        booking_id = request.form.get('booking_id')
        class_id = request.form.get('class_id')
        card_number = request.form.get('card_number')
        expiry_m = request.form.get('expiry_m')
        expiry_y = request.form.get('expiry_y')

        current_year = datetime.now().year
        current_month = datetime.now().month

        if not re.match(r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$', card_number):
            flash('Invalid credit card number')
            return render_template('member_lesson_payment.html', booking_id=booking_id, class_id=class_id)

        if int('20' + expiry_y) < current_year or (int('20' + expiry_y) == current_year and int(expiry_m) < current_month):
            flash('The credit card has expired.', 'error')
            return render_template('member_lesson_payment.html', booking_id=booking_id, class_id=class_id)

        cursor = get_cursor()
        cursor.execute("SELECT member_id FROM bookings WHERE booking_id = %s", (booking_id,))
        booking_record = cursor.fetchone()
        if booking_record:
            member_id = booking_record['member_id']
        else:
            flash('Booking record not found.', 'error')
            return redirect(url_for('member.my_booking'))

        cursor.execute("SELECT * FROM payments WHERE booking_id = %s", (booking_id,))
        if cursor.fetchone():
            update_query = """
                UPDATE payments 
                SET payment_status = 'paid', amount = (SELECT price FROM class WHERE class_id = %s) 
                WHERE booking_id = %s
            """
            cursor.execute(update_query, (class_id, booking_id))
        else:
            payment_date = datetime.now().strftime('%Y-%m-%d')
            insert_query = """
                INSERT INTO payments (date, amount, type, payment_status, booking_id, member_id) 
                VALUES (%s, (SELECT price FROM class WHERE class_id = %s), 'lesson', 'paid', %s, %s)
            """
            cursor.execute(insert_query, (payment_date, class_id, booking_id, member_id))

        update_booking_query = """
            UPDATE bookings
            SET payment_status = 'paid', booking_status = 'confirmed'
            WHERE booking_id = %s
        """
        cursor.execute(update_booking_query, (booking_id,))

        flash('Payment successful.', 'success')
    except Exception as e:
        flash('Failed to process payment. Please try again later.', 'error')
        print(e) 
    finally:
        if cursor:
            cursor.close()

    return redirect(url_for('member.my_booking'))


@member_blueprint.route('/viewmembership', methods=['GET','POST'])
@role_required(['member'])
def view_membership():
    # get the member id according to the session account id
    account_id=session['id']
    member_id=get_user_id(account_id)
    cursor=get_cursor()
    cursor.execute("SELECT membership_id,type,start_date,expiry_date,\
                CASE WHEN CURDATE() <= expiry_date THEN 'Active'\
                ELSE 'Expired' END AS status\
                FROM memberships WHERE member_id=%s",(member_id,))
    membership=cursor.fetchone()
    cursor.execute("SELECT date, type, amount,payment_status, booking_id \
            FROM payments WHERE member_id=%s AND amount!=0 ORDER BY date DESC",(member_id,))
    all_payments=cursor.fetchall()
    return render_template('viewmembership.html',membership= membership,\
            all_payments=all_payments,active='membership') 


@member_blueprint.route('/subscription_payment',methods=['GET','POST'])
@role_required(['member'])
def subscription_payment():
    if request.method=='POST':
        member_id=request.form['member_id']
        subscription_type=request.form['subscription_type']
        amount=request.form['payment_amount']
        if 'months' in request.form:
            number_of_month=int(request.form['months'])
        today=date.today()
        current_month = today.month
        current_year = today.year
        pyment_type='subscription'
        cursor=get_cursor()
        cursor.execute("SELECT * FROM subscription WHERE type=%s",(subscription_type,))
        selected_subscription=cursor.fetchone()
        #get the credit card information
        card_number=request.form['card_number']
        #name=request.form['card_holder']
        expiry_m=int(request.form['expiry_m'])
        expiry_y=int(request.form['expiry_y'])
        #cvc=request.form['cvc']
        # check if the credit card information is correct
        if not re.match(r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$', card_number):
            flash('Invalid credit card number')
            return render_template('payment_subscription.html',subscription=selected_subscription,member_id=member_id)
        elif expiry_y < current_year or (expiry_y == current_year and expiry_m <= current_month):
            flash('Expiry date is not valid')
            return render_template('payment_subscription.html',subscription=selected_subscription,member_id=member_id)
        else:
            payment_status='paid'
            cursor=get_cursor()
            cursor.execute("INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES (%s,%s,%s,%s,%s)",\
                           (pyment_type,member_id,today,amount,payment_status))
            # check if this member already has a membership sucscription
            cursor.execute("SELECT * FROM memberships WHERE member_id=%s",(member_id,))
            membership=cursor.fetchone()
            if membership:
                current_membership_expiry_date = max(today, membership['expiry_date'])
                if subscription_type == 'Annually':
                    expiry_date = current_membership_expiry_date + timedelta(days=365) 
                elif subscription_type == 'Monthly':
                    expiry_date = current_membership_expiry_date + timedelta(days=30*number_of_month)
                cursor.execute("UPDATE memberships SET type=%s, expiry_date=%s WHERE membership_id=%s",(subscription_type,expiry_date,membership['membership_id'],))
                flash("You have renew your membership successfully!")
            else:
                # get the end date according to the subscription type
                # Assuming one month has 30 days and one year has 365 days
                if subscription_type == 'Annually':
                    expiry_date = today + timedelta(days=365) 
                elif subscription_type == 'Monthly':
                    expiry_date = today + timedelta(days=30*number_of_month) 
                cursor.execute("INSERT INTO memberships (member_id,type,start_date,expiry_date) \
                               VALUES(%s,%s,%s,%s)",(member_id,subscription_type,today,expiry_date))
                flash("You have subscribed with us successfully!")
        return redirect(url_for('member.view_membership'))
    return redirect(url_for('member.member'))

# ajax resonse from front end to process the data
@member_blueprint.route('/get_payment_amount', methods=['GET','POST'])
@role_required(['member'])
def get_payment_amount():
    if request.method=="POST":
        # set response to empty dictionary
        response={}
        # get the subscription type and months of membership 
        subscription_type = request.form['subscription_type']
        months = int(request.form['months'])
        cursor=get_cursor()
        cursor.execute("SELECT * FROM subscription WHERE type=%s",(subscription_type,))
        subscription=cursor.fetchone()
        # check the total cost for each type of subscription
        if subscription_type=='Annually':
            amount = subscription['price']
        else:
            amount = subscription['price']*months
        response['amount']=amount
        return response
    return redirect(url_for('auth.user'))


# this is the membership renew page, direct to the payment page
@member_blueprint.route('/renew_membership',methods=['GET','POST'])
@role_required(['member'])
def renew_membership():
    account_id=session['id']
    member_id=get_user_id(account_id)
    cursor=get_cursor()
    # get the membership detail according to the member id
    cursor.execute("SELECT * FROM memberships WHERE member_id=%s",(member_id,))
    membership=cursor.fetchone()
    # check if member has already subscribed 
    if membership:
        cursor.execute("SELECT * FROM subscription WHERE type=%s",(membership['type'],))
        selected_subscription=cursor.fetchone()
    else:
        subscription_type='Annually'
        cursor.execute("SELECT * FROM subscription WHERE type=%s",(subscription_type,))
        selected_subscription=cursor.fetchone()
    return render_template('payment_subscription.html',subscription=selected_subscription,member_id=member_id)


# this is the membership cancellation page
@member_blueprint.route('/cancel_membership',methods=['GET','POST'])
@role_required(['member'])
def cancel_membership():
    if request.method=="POST":
        membership_id=request.form['membership_id']
        cursor=get_cursor()
        cursor.execute("DELETE FROM memberships WHERE membership_id=%s",(membership_id,))
        flash("You have successfully cancelled your membership.")
        return redirect(url_for('member.view_membership'))
    return redirect(url_for('member.view_membership'))


# this is the membership cancellation page
@member_blueprint.route('/payment_filter',methods=['GET','POST'])
@role_required(['member'])
def payment_filter():
    if request.method=="POST":
        account_id=session['id']
        member_id=get_user_id(account_id)
        filter=request.form['filter']
        cursor=get_cursor()
        if filter == 'order_by_date':
            query="SELECT date, type, amount,payment_status,booking_id \
            FROM payments WHERE member_id=%s AND amount!=0 ORDER BY date DESC"
            cursor.execute(query,(member_id,))
        elif filter == 'subscription':
            query="SELECT date, type, amount,payment_status,booking_id \
            FROM payments WHERE member_id=%s AND type=%s ORDER BY date DESC"
            cursor.execute(query,(member_id,filter))
        else:
            query="SELECT date, type, amount,payment_status,booking_id \
            FROM payments WHERE member_id=%s AND type=%s AND amount!=0 ORDER BY date DESC"
            cursor.execute(query,(member_id,filter))
        all_payments=cursor.fetchall()
        return render_template('paymentresponse.html',all_payments=all_payments)
    return redirect(url_for('member.view_membership'))



@member_blueprint.route('/view_news', methods=['GET'])
# Check if the role is member, only instructor role can access this page
@role_required(['member'])
def view_news():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM news")
    news = cursor.fetchall()
    return render_template('member_view_news.html', news=news)

# Member search news by keyword
@member_blueprint.route('/search_news', methods=['GET', 'POST'])
# Check if the role is member, only members can access this page
@role_required(['member'])
def search_news():
    if request.method == 'POST':
        search_keyword = request.form['search_keyword']
        cursor = get_cursor()
        # Assuming 'title' and 'content' are the columns to search for keywords
        cursor.execute("SELECT * FROM news WHERE title LIKE %s OR content LIKE %s", (f'%{search_keyword}%', f'%{search_keyword}%'))
        news = cursor.fetchall()
        return render_template('member_view_news.html', news=news, search_keyword=search_keyword)
    else:
        return render_template('member_view_news.html')

# this is the page to view the message (reminder)
@member_blueprint.route('/view_message',methods=['GET','POST'])
@role_required(['member'])
def view_message():
    account_id=session['id']
    member_id=get_user_id(account_id)
    cursor=get_cursor()  
    cursor.execute("SELECT ROW_NUMBER() OVER (ORDER BY date) AS number, id,title,\
                   content,date,status FROM reminders WHERE member_id=%s",(member_id,))
    all_messages=cursor.fetchall()
    return render_template('message_list.html',all_messages=all_messages)
    
# this is the page to delete the message (reminder)
@member_blueprint.route('/delete_message/<int:id>',methods=['GET','POST'])
@role_required(['member'])
def delete_message(id):
    cursor=get_cursor()  
    cursor.execute("DELETE FROM reminders WHERE id=%s",(id,))
    return redirect(url_for('member.view_message'))

# this is the page to mark the message to read
@member_blueprint.route('/mark_message_read',methods=['GET','POST'])
@role_required(['member'])
def mark_message_read():
    if request.method=="POST":
        message_id=request.form['message_id']
        cursor=get_cursor()  
        cursor.execute("UPDATE reminders SET status='read' WHERE id=%s",(message_id,))
    return redirect(url_for('member.view_message'))
    

