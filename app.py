from flask import Flask
from auth import auth_blueprint
from guest import guest_blueprint
from manager import manager_blueprint
from instructor import instructor_blueprint
from member import member_blueprint
from flask_hashing import Hashing

app = Flask(__name__)
# add secret_key to use session
app.secret_key = 'Group AP'

# create an instance of hashing
hashing = Hashing(app)

# register the blueprints: auth, manager, instructor and member 
app.register_blueprint(auth_blueprint)
app.register_blueprint(guest_blueprint)
app.register_blueprint(manager_blueprint, url_prefix='/manager') 
app.register_blueprint(instructor_blueprint, url_prefix='/instructor') 
app.register_blueprint(member_blueprint, url_prefix='/member') 


if __name__=='__main__':

    app.run(debug=True)