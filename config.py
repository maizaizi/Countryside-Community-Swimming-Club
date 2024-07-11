import connect
import mysql.connector
import os
#accept image type when uploading  images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
#the folder for the uploaded images, this is for the local app
UPLOAD_FOLDER = 'static/images/'
#the folder for the uploaded images, this is for the pythonanywhere webapp
#UPLOAD_FOLDER = '/home/groupAP/COMP639S1_Group_AP/static/images/'
# the time slots for the class and instructor available time
TIMESLOTS = ['06:00','06:30','07:00','07:30','08:00','08:30','09:00','09:30',\
                '10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30',\
                '14:00','14:30','15:00','15:30','16:00','16:30','17:00','17:30',\
                '18:00','18:30','19:00','19:30']

dbconn = None
connection = None
# connect with database, and get the cursor function
def get_cursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost,\
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor(dictionary=True)
    return dbconn

# function to get user's id according to the account id
def get_user_id(account_id):
    cursor=get_cursor()
    cursor.execute("SELECT member_id AS id FROM member WHERE account_id=%s\
            UNION SELECT instructor_id AS id FROM instructor WHERE account_id=%s\
            UNION SELECT manager_id AS id FROM manager WHERE account_id=%s",\
            (account_id,account_id,account_id))
    user=cursor.fetchone()
    return user['id']

# check the upload file mainly images to check 
# if this image's name is in the image type 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_exist(image_name):
    # Construct the full path to the image file
    image_path = os.path.join(UPLOAD_FOLDER, image_name)
    # Check if the file exists
    if os.path.exists(image_path):
        return True
    else:
        return False
