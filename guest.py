from flask import Flask, render_template, Blueprint, request, flash, jsonify
from auth import auth_blueprint
from config import get_cursor
from flask_wtf import FlaskForm
from datetime import datetime,date,timedelta
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message

app = Flask(__name__)




app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'bright.tech.ap@gmail.com'  
app.config["MAIL_PASSWORD"] = 'xupijwvjmgygqljg'
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

mail = Mail(app)



# create instructor blueprint view
guest_blueprint = Blueprint('guest', __name__)

#this is the home page


@guest_blueprint.route('/')
def home():
    cursor = get_cursor()
    cursor.execute("SELECT class_id as id, name, type, description, image, duration, price, capacity FROM class")
    classes = cursor.fetchall()
    cursor.close()

    indexed_classes = list(enumerate(classes))

    cursor = get_cursor()
    cursor.execute("SELECT first_name, family_name, expert_area, image, profile FROM instructor")
    instructors = cursor.fetchall()
    cursor.close()

    return render_template('index.html', classes=indexed_classes, instructors=instructors)



@guest_blueprint.route('/class')
def class_guest():
    
    return render_template('class_guest.html',)


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Please enter your name.")])
    email = StringField("Email", validators=[DataRequired(message="Please enter your email address"), Email()])
    subject = StringField("Subject", validators=[DataRequired(message="Please enter a subject.")])
    message = TextAreaField("Message", validators=[DataRequired(message="Please enter a message.")])
    submit = SubmitField("Send")

@guest_blueprint.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit():
           
            msg = Message(form.subject.data, sender='bright.tech.ap@gmail.com', recipients=['bright.tech.ap@gmail.com'])
            msg.body = f"""
            From: {form.name.data} <{form.email.data}>
            {form.message.data}
            """
            print("Subject:", msg.subject)
            print("Body:", msg.body)
            mail.send(msg)
            #flash('Your message has been sent successfully!', 'success')
            return render_template('contact_success.html', form=form, success=True)
    return render_template('contact.html', form=form, success=False)

@guest_blueprint.route('/contact_success', methods=['GET'])
def contact_success():
    return render_template('contact_success.html')

@guest_blueprint.route('/findus')
def find_us():
    return render_template('findus.html')







@guest_blueprint.route('/view_weeklytimetable')
def view_weeklytimetable():
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

    return render_template('timetable.html', all_schedules=all_schedules, classes=classes, instructors=instructors)








@guest_blueprint.route('/get_week_classes', methods=['GET'])
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


@guest_blueprint.route('/showclass/<int:class_id>')
def show_class(class_id):
    cursor = get_cursor()
    cursor.execute("SELECT class_id as id, name, type, description, image, duration, price, capacity FROM class WHERE class_id = %s", (class_id,))
    this_class = cursor.fetchone()
    cursor.close()

    if this_class is None:
        return render_template('404.html'), 404  

    return render_template('showclass.html', this_class=this_class)


