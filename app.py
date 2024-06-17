from flask import Flask, render_template, request, redirect, url_for, session, flash, g, current_app, jsonify
from datetime import datetime, timedelta, date
from mysql.connector import FieldType
from flask_hashing import Hashing
import re
import os
from account import account_page # login, register, profile management
from schedule import schedule_page #
from payment import payment_page
from subscription import subscription_page
from news import news_page
from manage import manage_page # manage user, staff account 
from reports import reports_page
from workshop import workshop_page
from timetable import timetable_page
from location import location_page
from db import getCursor
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
import base64
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'GreenByte'
app.register_blueprint(account_page, url_prefix="/account")
app.register_blueprint(schedule_page, url_prefix="/schedule")
app.register_blueprint(payment_page, url_prefix="/payment")
app.register_blueprint(subscription_page, url_prefix="/subscription")
app.register_blueprint(news_page, url_prefix="/news")
app.register_blueprint(manage_page, url_prefix="/manage")
app.register_blueprint(reports_page, url_prefix="/reports")
app.register_blueprint(workshop_page, urlprefix="/workshop")
app.register_blueprint(timetable_page, url_prefix="/timetable")
app.register_blueprint(location_page, url_prefix="/location")

hashing = Hashing(app)
app.hashing = hashing  # Attach hashing to the app

@app.route('/')
def index():
    #Render the home.thml template upon accessing the root URL
    return redirect(url_for('home'))

@app.route('/home')
def home():
    cursor = getCursor()
    cursor.execute("""SELECT w.*, i.*
                    FROM workshops w
                    JOIN images i ON w.image_id = i.image_id;""")
    workshops = cursor.fetchall()

    cursor.execute("""SELECT i.*, im.*
                    FROM instructor i
                    LEFT JOIN images im ON i.image_id = im.image_id;""")
    instructors = cursor.fetchall()


    # Encoding image data to base64 and handling image availability
    for instructor in instructors:
        if instructor['profile_image']:
            image_data = base64.b64encode(instructor['profile_image']).decode('utf-8')
            instructor['profile_image'] = f"data:image/jpeg;base64,{image_data}"
        else:
            instructor['profile_image'] = None  # No image data available

    #Render the home.thml template upon accessing the root URL
    return render_template('home.html', workshops = workshops, instructors = instructors)

@app.context_processor
def inject_login_info():
    cursor = getCursor()
    login_info = None
    if 'role' in session:
        user_id = session['user_id']
        if session['role'] == 'Instructor': 
            cursor.execute("""SELECT *
                              FROM instructor
                              LEFT JOIN images ON instructor.image_id = images.image_id
                              WHERE instructor.user_id = %s""", (user_id,))
        elif session['role'] == 'Member':
            cursor.execute("""SELECT *
                              FROM member
                              WHERE member.user_id = %s""", (user_id,))
        elif session['role'] == 'Manager':
            cursor.execute("""SELECT *
                              FROM manager
                              WHERE manager.user_id = %s""", (user_id,))
        login_info = cursor.fetchone()
        image_data_base64 = ""
        if login_info and login_info['profile_image']:
            image_data_base64 = base64.b64encode(login_info['profile_image']).decode('utf-8')

        login_info['image_data_base64'] = image_data_base64
    cursor.close()
    return dict(login=login_info)



if __name__ == '__main__':
    app.run(debug=True)