from flask import Blueprint, jsonify
from db import getCursor
from app import *
import base64
from datetime import datetime, date, timedelta, time
from collections import defaultdict
from decimal import Decimal


account_page = Blueprint('account_page', __name__,
                        template_folder='templates',
                        static_folder='static')

def image_to_base64(image_data):
    if image_data:
        return base64.b64encode(image_data).decode('utf-8')
    return None
@account_page.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Please login to view the dashboard.', 'info')
        return redirect(url_for('account_page.login'))

    user_id = session.get('user_id')
    role = session.get('role', '')
    order = request.args.get('order', 'desc')
    total_instructors = count_entities('instructor')
    total_members = get_total_members()
    workshops = get_workshops(user_id, session['role'])
    news_items = get_news_items(order)
    member_details = None
    lessons = []
    workshop_trend = {}

    # Common variables for all roles
    total_workshops = get_total_workshops()
    total_lessons = get_total_lessons()
    upcoming_workshops = get_upcoming_workshops()
    upcoming_lessons = get_upcoming_lessons()
    my_bookings = get_my_bookings(user_id)
    workshop_popularity = get_workshop_popularity()
    chart_data = get_financial_chart_data()
    yearly_revenue = get_yearly_revenue()

    
    if role == 'Member':
        member_id = get_member_id(user_id)
        lessons = get_lessons(order)
        member_details = get_member_details(user_id)
        subscriptions = get_subscription_details(user_id)

    elif role == 'Instructor':
        instructor_id = get_instructor_id(user_id)
        lessons = get_lessons_by_instructor(instructor_id, order)
        subscriptions = get_subscription_details(user_id)

    elif role == 'Manager':
        lessons = get_all_lessons(order)
        subscriptions = get_members_subscription_details()
        workshop_trend = get_workshop_trend()

    order_description = "Oldest First" if order == 'asc' else "Newest First"
    return render_template('dashboard.html', subscriptions=subscriptions, member_details=member_details, news=news_items, lessons=lessons, 
                            order_description=order_description, total_instructors=total_instructors, total_members=total_members, workshops=workshops, 
                            workshop_trend = workshop_trend, total_workshops=total_workshops, total_lessons=total_lessons
                            , upcoming_workshops=upcoming_workshops, upcoming_lessons=upcoming_lessons, my_bookings=my_bookings, workshop_popularity=workshop_popularity,
                            chart_data=chart_data, yearly_revenue=yearly_revenue)

#profile
@account_page.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session and session['role'] == 'Member':
        cursor = getCursor()
        user_id = session['user_id']
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            address = request.form.get('address')
            date_of_birth= request.form.get('date_of_birth')
            gardening_experience = request.form.get('gardening_experience')

            # Convert date_of_birth from form (string) to a datetime object
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
            today = datetime.today()

             # Calculate age
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if dob > today:
                # Date of birth is in the future
                flash("Date of birth cannot be in the future.", "danger")
                return redirect(url_for('account_page.profile'))
            
            if age < 18:
                # User is under 18
                flash("User must be 18 years or older.", "danger")
                return redirect(url_for('account_page.profile'))
            
            cursor.execute("SELECT * FROM member WHERE email = %s AND user_id != %s", (email, user_id))
            if cursor.fetchone():
                flash("This email is already used by another account.", "danger")
            else:
                password = request.form.get('password')
                if password:
                    hashed = hashing.hash_value(password, salt='abcd')
                    cursor.execute('''UPDATE user SET password= %s
                                            WHERE user_id = %s''', (hashed,user_id))
                else:
                    cursor.execute("""
                                    UPDATE member 
                                    SET title=%s, first_name=%s, last_name=%s, position=%s, phone_number=%s,email=%s, 
                                    address=%s, date_of_birth=%s,gardening_experience=%s
                                    WHERE user_id = %s""", (title, first_name, last_name, position, phone_number, email, address, date_of_birth, gardening_experience, user_id))
                flash("Profile updated successfully!", "success")
        cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM member natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()
        print(profile)
        return render_template('profile.html', profile=profile, image_data=image_data_base64)

    if 'loggedin' in session and session['role'] == 'Instructor':
        cursor = getCursor()
        user_id = session['user_id']
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            address = request.form.get('address')
            profile = request.form.get('instructor_profile')
        
            cursor.execute("SELECT * FROM instructor WHERE email = %s AND user_id != %s", (email, user_id))
            if cursor.fetchone():
                flash("This email is already used by another account.", "danger")
            else:
                password = request.form.get('password')
                if password:
                    hashed = hashing.hash_value(password, salt='abcd')
                    cursor.execute('''UPDATE user SET password= %s
                                            WHERE user_id = %s''', (hashed,user_id))
                else:
                    cursor.execute("""
                        UPDATE instructor 
                        SET title=%s, first_name=%s, last_name=%s, position=%s, email=%s, address=%s, phone_number=%s
                        WHERE user_id = %s
                    """, (title, first_name, last_name, position, email, address, phone_number, user_id))

                flash("Profile updated successfully!", "success")

        cursor.execute("SELECT profile_image FROM instructor WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM instructor natural join user LEFT JOIN images ON instructor.image_id = images.image_id  WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()
        return render_template('/profile.html', profile=profile, image_data=image_data_base64)
    
    if 'loggedin' in session and session['role'] == 'Manager':
        user_id = session['user_id']
        cursor = getCursor()
        if request.method == 'POST':
            title = request.form.get('title')   
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            
            cursor.execute("SELECT * FROM manager WHERE email = %s AND user_id != %s", (email, user_id))
            if cursor.fetchone():
                flash("This email is already used by another account.", "danger")
            else:
                password = request.form.get('password')
                if password:
                    hashed = hashing.hash_value(password, salt='abcd')
                    cursor.execute('''UPDATE user SET password= %s
                                            WHERE user_id = %s''', (hashed,user_id))
                else:
                    cursor.execute('''UPDATE manager SET title= %s, first_name= %s, last_name= %s, position= %s,  phone_number= %s, email= %s
                                        WHERE user_id = %s''', (title,first_name,last_name,position,phone_number,email,user_id))
            
                flash("Profile updated successfully!", "profile_update")
        cursor.execute("SELECT profile_image FROM manager WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')    
        cursor.execute("SELECT * FROM manager natural join user WHERE user.user_id=%s", (user_id,))
        profile = cursor.fetchone()
        return render_template('profile.html', profile=profile, image_data=image_data_base64)

    else:
        return redirect(url_for('account_page.login'))
    
@account_page.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('account_page.login'))
     # Handles password change logic, including validation and updating the database
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        cursor = getCursor()
        cursor.execute("SELECT password FROM user WHERE user_id = %s", (session['user_id'],))
        account = cursor.fetchone()

        if not account:
            flash('User not found.', 'error')
            return redirect(url_for('admin.change_password'))

        # Check if the old password matches
        if not current_app.hashing.check_value(account['password'], old_password, salt='abcd'):
            flash('Invalid current password!', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
        else:
            # Define the password regex pattern
            password_pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$'

            # Check if the new password meets the criteria
            if not re.match(password_pattern, new_password):
                flash("Password must contain at least 8 characters, including at least one digit, one lowercase letter, one uppercase letter, and one special character.", "danger")
            else:
                # Hash the new password and update it in the database
                hashed_new_password = current_app.hashing.hash_value(new_password, salt='abcd')
                cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (hashed_new_password, session['user_id'],))
                flash('Your password has been updated successfully.', 'success')

        return redirect(url_for('account_page.profile'))
    return render_template('profile.html')

#upload image
@account_page.route('/upload_primary_image/<int:user_id>', methods=['POST'])
def upload_primary_image(user_id):
    if request.method == 'POST':
        file = request.files['image']
        if file:
            image_data = file.read()
            cursor = getCursor()
            if session['role'] == 'Instructor':
                cursor.execute('UPDATE instructor SET profile_image = %s WHERE user_id = %s', (image_data, user_id))
            elif session['role'] == 'Member':
                cursor.execute('UPDATE member SET profile_image = %s WHERE user_id = %s', (image_data, user_id))
            elif session['role'] == 'Manager':
                cursor.execute('UPDATE manager SET profile_image = %s WHERE user_id = %s', (image_data, user_id))
            cursor.close()
    return redirect(url_for('account_page.profile'))

#delete image
@account_page.route('/delete_image/<int:user_id>', methods=['POST'])
def delete_image(user_id):
    cursor = getCursor()
    if session['role'] == 'Instructor':
        cursor.execute("UPDATE instructor LEFT JOIN images ON instructor.image_id = images.image_id SET profile_image = NULL, image_status = 'Inactive' WHERE user_id = %s", (user_id,))
    elif session['role'] == 'Member':
        cursor.execute("UPDATE member SET profile_image = NULL WHERE user_id = %s", (user_id,))
    elif session['role'] == 'Manager':
        cursor.execute("UPDATE manager LEFT JOIN images ON instructor.image_id = images.image_id SET profile_image = NULL, image_status = 'Inactive' WHERE user_id = %s", (user_id,))
    cursor.close()
    return redirect(url_for('account_page.profile'))

@account_page.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'user_name' in request.form and 'password' in request.form:
        # Create variables for easy access
        user_name = request.form['user_name']
        user_password = request.form['password']
        # Check if account exists using MySQL
        cursor = getCursor()
        cursor.execute('SELECT * FROM user WHERE user_name = %s AND status = "Active"', (user_name,))
        # Fetch one record and return result
        account = cursor.fetchone()
        
        if account is not None:
            password = account['password']
            if current_app.hashing.check_value(password, user_password, salt='abcd'):
            # If account exists in accounts table 
            # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['user_id'] = account['user_id']
                session['user_name'] = account['user_name']
                session['role'] = account['role']
                # Fetch additional user details based on role
                if session['role'] == 'Member':
                    cursor.execute('SELECT first_name, last_name, position,reminder_date FROM member WHERE user_id = %s', (account['user_id'],))
                elif session['role'] == 'Instructor':
                    cursor.execute('SELECT first_name, last_name, position FROM instructor WHERE user_id = %s', (account['user_id'],))
                elif session['role'] == 'Manager':
                    cursor.execute('SELECT first_name, last_name, position FROM manager WHERE user_id = %s', (account['user_id'],))
                
                personal_info = cursor.fetchone()
                if personal_info:
                    session['first_name'] = personal_info['first_name']
                    session['last_name'] = personal_info['last_name']
                    session['position'] = personal_info['position']
                
                if personal_info and personal_info.get('reminder_date') is not None:
                    cursor.execute('SELECT end_date FROM subscriptions WHERE user_id = %s', (account['user_id'],))
                    end_date = cursor.fetchone()
                    if end_date and end_date['end_date'] >= date.today():
                        flash('Your membership is about to expire!',"danger")
                    else:
                        flash('Your membership is expired!',"danger")
                    cursor.execute("UPDATE member SET reminder_date = %s WHERE user_id = %s", (None, account['user_id'],))
                    
                 # Redirect user based on role
                return redirect(url_for('account_page.dashboard'))
            else:
                #password incorrect
                flash('Incorrect password!', 'danger')
        else:
            # Account doesnt exist or username incorrect
            flash('Incorrect username!', 'danger')
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)
    pass

@account_page.route('/register', methods=['GET', 'POST'])
def register():
    # Initialize message and user data dictionary
    cursor = getCursor()
    msg = ''
    user_data = {
        'user_name': '',
        'password': '',
        'title': '',
        'first_name': '',
        'last_name': '',
        'position': '',
        'phone_number': '',
        'email': '',
        'address': '',
        'date_of_birth': '',
        'is_student_or_csc': False
    }

    if request.method == 'POST':
        # Update user_data dictionary with form data
        user_data.update({key: request.form.get(key, '') for key in user_data.keys()})
        user_data['is_student_or_csc'] = 'is_student_or_csc' in request.form

        # Convert date_of_birth from form (string) to a datetime object
        try:
            dob = datetime.strptime(user_data['date_of_birth'], "%Y-%m-%d")
        except ValueError:
            dob = None
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")

        today = datetime.today()

        # Check if email is taken
        cursor.execute('''
            SELECT email FROM member WHERE email = %s
            UNION
            SELECT email FROM instructor WHERE email = %s
            UNION
            SELECT email FROM manager WHERE email = %s
        ''', (user_data['email'], user_data['email'], user_data['email']))
        email_exists = cursor.fetchone()

        # Perform validations
        
        cursor.execute('SELECT user_name FROM user WHERE user_name = %s', (user_data['user_name'],))
        match = cursor.fetchone()
        if match:
            flash("Username has been taken.", "danger")
        elif email_exists:
            flash('Email already taken!', 'danger')
        elif dob and dob > today:
            flash("Date of birth cannot be in the future.", "danger")
        elif dob and (today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))) < 18:
            flash("You must be 18 years or older to register.", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', user_data['email']):
            flash('Invalid email address!', 'danger')
        elif not re.match(r'[A-Za-z0-9]+', user_data['user_name']):
            flash('Username must contain only characters and numbers!', 'danger')
        elif not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}', user_data['password']):
            flash('Password must be at least 8 characters long and mix of character types!', 'danger')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            hashed_password = current_app.hashing.hash_value(user_data['password'], salt='abcd')
            user_data['password'] = hashed_password
            # Redirect if all validations pass
            session['registration_info'] = user_data
            # Redirect to the payment page
            return redirect(url_for('payment_page.payment_on_register'))
            
     # Show registration form with message (if any) and pre-filled data
    return render_template('register.html', msg=msg, **user_data)

@account_page.route('/faq')
def faq():
    #Render the faq.html template upon accessing the root URL
    return render_template('faq.html')

@account_page.route('/contact')
def contact():
    #Render the faq.html template upon accessing the root URL
    return render_template('contact.html')

#User list
@account_page.route('/userList', methods=['GET', 'POST'])
def userList():
    cursor = getCursor()
    if request.method == "POST":
        instructorProfile = None
        memberProfile = None
        search = request.form.get('search')
        searchProfile = f"%{search}%"
        cursor.execute("""SELECT * FROM instructor WHERE first_name LIKE %s OR last_name LIKE %s        
                        """, (searchProfile, searchProfile,))
        instructorProfile = cursor.fetchall()
        cursor.execute("""SELECT * FROM member WHERE first_name LIKE %s OR last_name LIKE %s;
                        """, (searchProfile, searchProfile,))
        memberProfile = cursor.fetchall()
        cursor.execute('SELECT * FROM subscriptions;')
        subscriptions = cursor.fetchall()
        return render_template("userlist.html", instructorProfile=instructorProfile, memberProfile=memberProfile, subscriptions = subscriptions)
    elif 'loggedin' in session and session['role'] == 'Manager':
        
        cursor.execute('SELECT * FROM instructor JOIN user ON instructor.user_id = user.user_id WHERE user.status = "Active"')
        instructorProfile = cursor.fetchall()
        cursor.execute('SELECT * FROM member JOIN user ON member.user_id = user.user_id WHERE user.status = "Active"')
        memberProfile = cursor.fetchall()
        cursor.execute('SELECT * FROM subscriptions;')
        subscriptions = cursor.fetchall()

        return render_template('userlist.html', instructorProfile=instructorProfile, memberProfile=memberProfile, subscriptions=subscriptions)

    else:
        return redirect(url_for('account_page.dashboard'))

@account_page.route('/adduser', methods=['GET', 'POST'])
def adduser():
    cursor = getCursor()
    msg = ''
    if request.method == 'GET':
        return render_template('manager/add_newUser.html', msg=msg)
    
    if request.method == "POST":
        user_details = {
            'role': request.form.get('role'),
            'user_name': request.form.get('user_name'),
            'password': request.form.get('password'),  
            'title': request.form.get('title'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'position': request.form.get('position'),
            'phone_number': request.form.get('phone_number'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'membership_type': request.form.get('type'),
            'dob': request.form.get('dob'),
            'gardenExp': request.form.get('gardenExp'),
            'is_student_or_csc': request.form.get('is_student_or_csc') == 'on',
            'instructor_profile': request.form.get('instructor_profile')
        }

        # Convert date_of_birth from form (string) to a datetime object
        try:
            dob = datetime.strptime(user_details['dob'], "%Y-%m-%d")
        except ValueError:
            dob = None

        today = datetime.today()

        # Perform validations
        # Check if email is taken
        cursor.execute('''
            SELECT email FROM member WHERE email = %s
            UNION
            SELECT email FROM instructor WHERE email = %s
            UNION
            SELECT email FROM manager WHERE email = %s
        ''', (user_details['email'], user_details['email'], user_details['email']))
        email_exists = cursor.fetchone()

        cursor.execute('SELECT user_name FROM user WHERE user_name = %s', (user_details['user_name'],))
        match = cursor.fetchone()
        if match:
            flash("Username has been taken.", "danger")
        elif email_exists:
            flash('Email already taken!', 'danger')
        elif dob and dob > today:
            flash("Date of birth cannot be in the future.", "danger")
        elif dob and (today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))) < 18:
            flash("You must be 18 years or older to register.", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', user_details['email']):
            flash('Invalid email address!', 'danger')
        elif not re.match(r'[A-Za-z0-9]+', user_details['user_name']):
            flash('Username must contain only characters and numbers!', 'danger')
        elif not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}', user_details['password']):
            flash('Password must be at least 8 characters long and mix of character types!', 'danger')
        else:
            # Password Hashing
            hashed_password = current_app.hashing.hash_value(user_details['password'], salt='abcd')
            user_details['password'] = hashed_password
            # Insert into user table
            cursor.execute("INSERT INTO user (user_name, password, role, status) VALUES (%s, %s, %s, 'Active')", 
                            (user_details['user_name'], hashed_password, user_details['role']))
            user_id = cursor.lastrowid


            if user_details['role'] == 'Member':
                # Fetch price based on type
                cursor.execute('SELECT * FROM prices;')
                prices = cursor.fetchall()

                if user_details['membership_type'] == 'Annual':
                    price = Decimal(prices[0]['price']) * Decimal(0.7) if user_details['is_student_or_csc'] else prices[0]['price']  # Apply a 30% discount if applicable
                elif user_details['membership_type'] == 'Monthly':
                    price = Decimal(prices[1]['price']) * Decimal(0.7) if user_details['is_student_or_csc'] else prices[1]['price']  # Apply a 30% discount if applicable

                # Insert into member table
                cursor.execute("INSERT INTO member (user_id, title, first_name, last_name, phone_number, email, address, position, date_of_birth, gardening_experience, is_student_or_csc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                (user_id, user_details['title'], user_details['first_name'], user_details['last_name'], user_details['phone_number'], user_details['email'], 
                                user_details['address'], user_details['position'], user_details['dob'], user_details['gardenExp'], user_details['is_student_or_csc']))
                
                # Insert into subscriptions table
                cursor.execute("""
                    INSERT INTO subscriptions (user_id, type, start_date, end_date, status, price) 
                    VALUES (%s, %s, CURDATE(), CURDATE(), 'Inactive', %s)
                    """, 
                    (user_id, user_details['membership_type'], price)
                )

            elif user_details['role'] == 'Instructor':
                # Insert into instructor table
                cursor.execute("INSERT INTO instructor (user_id, title, first_name, last_name, phone_number, email, address, position, instructor_profile) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                (user_id, user_details['title'], user_details['first_name'], user_details['last_name'], user_details['phone_number'], user_details['email'], user_details['address'], user_details['position'], user_details['instructor_profile']))

            flash("User added successfully!", "success")
            return redirect(url_for('account_page.userList'))

    return render_template('manager/add_newUser.html', msg=msg, **user_details)

#Delete User
@account_page.route('/deleteUser', methods=['POST'])
def deleteUser():
    cursor = getCursor()
    user_id = request.form.get('user_id')
    cursor.execute("SELECT user.role, instructor.instructor_id FROM user \
                    LEFT JOIN instructor ON user.user_id = instructor.user_id \
                    WHERE user.user_id = %s", (user_id,))
    user = cursor.fetchone()
    if user['role'] == "Member":
        cursor.execute('UPDATE user SET status = "Inactive" WHERE user_id = %s', (user_id,))
        flash('Member deleted successfully!', 'success')
    else:
        cursor.execute('SELECT * FROM workshops WHERE instructor_id = %s AND date >= CURDATE()', (user['instructor_id'],))
        workshop_match = cursor.fetchall()
        cursor.execute('SELECT * FROM lessons WHERE instructor_id = %s AND date >= CURDATE()', (user['instructor_id'],))
        lesson_match = cursor.fetchall()
        if workshop_match or lesson_match:
            flash('The instructor cannot be deleted as he/she is holding workshops or lessons. ', 'danger')
        else:
            cursor.execute('UPDATE user SET status = "Inactive" WHERE user = %s', (user_id,))
            flash('Instructor deleted successfully!', 'success')

    

    return redirect(url_for('account_page.userList'))

#Edit User
@account_page.route('/editUser', methods=['GET', 'POST'])
def editUser():
        cursor = getCursor()
        user_id = request.form.get('user_id')
        role = request.form.get('role')
        cursor.execute("SELECT status FROM subscriptions WHERE user_id = %s", (user_id,))

        status = cursor.fetchone()
        if role == 'Member':
            cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            image_data_base64 = ""
            if result and result['profile_image']:
                image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
            cursor.execute("SELECT * FROM member natural join user WHERE  user.user_id = %s", (user_id,))
            profile = cursor.fetchone()

        elif role == 'Instructor':
            cursor.execute("SELECT profile_image FROM instructor WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            image_data_base64 = ""
            if result and result['profile_image']:
                image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
            cursor.execute("SELECT * FROM instructor NATURAL JOIN user LEFT JOIN images ON instructor.image_id = images.image_id WHERE user.user_id = %s", (user_id,))
            profile = cursor.fetchone()

        return render_template('/manager/edit_userProfile.html', profile=profile, image_data=image_data_base64, status= status)

@account_page.route('/editUserProfile', methods=['POST'])
def editUserProfile():
    user_id = request.form.get('user_id')
    title = request.form.get('title')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    position = request.form.get('position')
    phone_number = request.form.get('phone_number')
    email = request.form.get('email')
    address = request.form.get('address')
    date_of_birth = request.form.get('date_of_birth')
    gardening_experience = request.form.get('gardening_experience')
    instructor_profile = request.form.get('instructor_profile')
    user_name = request.form.get('user_name')
    role = request.form.get('role')
    status = request.form.get('status')
    cursor = getCursor()
    cursor.execute('''UPDATE subscriptions SET status= %s WHERE user_id = %s''', (status, user_id))

    cursor.execute("SELECT email FROM member WHERE email = %s AND user_id != %s UNION SELECT email FROM instructor WHERE email = %s AND user_id != %s;", (email, user_id,email,user_id))

    if cursor.fetchone():
        flash("This email is already used by another account.", "profile_update")
    else:
        password = request.form.get('password')
        if password:
            hashed = hashing.hash_value(password, salt='abcd')
            cursor.execute('''UPDATE user SET password= %s,user_name=%s WHERE user_id = %s''', (hashed,user_name, user_id))
        else:
            if role == 'Member':
                cursor.execute("""
                    UPDATE member 
                    SET title=%s, first_name=%s, last_name=%s, position=%s, phone_number=%s,email=%s, 
                    address=%s, date_of_birth=%s,gardening_experience=%s
                    WHERE user_id = %s""", (title, first_name, last_name, position, phone_number, email, address, date_of_birth, gardening_experience, user_id))
                cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                image_data_base64 = ""
                if result and result['profile_image']:
                    image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
                cursor.execute("SELECT * FROM member natural join user WHERE  user.user_id = %s", (user_id,))
                profile = cursor.fetchone()

            elif role == 'Instructor':
                cursor.execute("""
                    UPDATE instructor 
                    SET title=%s, first_name=%s, last_name=%s, position=%s, phone_number=%s,email=%s, 
                    address=%s,instructor_profile=%s
                    WHERE user_id = %s""", (title, first_name, last_name, position, phone_number, email, address, instructor_profile, user_id))
                cursor.execute("""SELECT profile_image FROM instructor WHERE user_id = %s""", (user_id,))
                result = cursor.fetchone()
                image_data_base64 = ""
                if result and result['profile_image']:
                    image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
                cursor.execute("""SELECT i.*, u.*, im.*
                                FROM instructor i
                                natural join user u
                                JOIN images im ON i.image_id = im.image_id WHERE u.user_id = %s""", (user_id,))
                profile = cursor.fetchone()

        cursor.execute("SELECT status FROM subscriptions WHERE user_id = %s", (user_id,))

        status = cursor.fetchone()

        flash("Profile updated successfully!", "success")
        return render_template('/manager/edit_userProfile.html', profile=profile, image_data=image_data_base64 , status= status)
    

    if role == 'Member':
        cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM member natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    elif role == 'Instructor':
        cursor.execute("SELECT profile_image FROM instructor WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM instructor natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    return render_template('/manager/edit_userProfile.html', profile=profile, image_data=image_data_base64) 


#upload image when edit user
@account_page.route('/upload_primary_image_user/<int:user_id>', methods=['POST'])
def upload_primary_image_user(user_id):
    role = request.form.get('role')
    file = request.files['image']
    if file:
        image_data = file.read()
        cursor = getCursor()
        if role == 'Instructor':
            cursor.execute('UPDATE instructor SET profile_image = %s WHERE user_id = %s', (image_data, user_id))
        elif role == 'Member':
            cursor.execute('UPDATE member SET profile_image = %s WHERE user_id = %s', (image_data, user_id))

    
    cursor.execute("SELECT status FROM subscriptions WHERE user_id = %s", (user_id,))

    status = cursor.fetchone()
    if role == 'Member':
        cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM member natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    elif role == 'Instructor':
        cursor.execute("SELECT profile_image FROM instructor WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM instructor natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    
    return render_template('/manager/edit_userProfile.html', profile=profile, image_data=image_data_base64, status= status)

#delete image for user
@account_page.route('/delete_image_user/<int:user_id>', methods=['POST'])
def delete_image_user(user_id):
    role = request.form.get('role')
    cursor = getCursor()
    if role == 'Instructor':
        cursor.execute("UPDATE instructor LEFT JOIN images ON instructor.image_id = images.image_id SET profile_image = NULL, image_status = 'Inactive' WHERE user_id = %s", (user_id,))
    elif role == 'Member':
        cursor.execute('UPDATE member SET profile_image = NULL WHERE user_id = %s', (user_id,))
    cursor.execute("SELECT status FROM subscriptions WHERE user_id = %s", (user_id,))

    status = cursor.fetchone()
    if role == 'Member':
        cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM member natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    elif role == 'Instructor':
        cursor.execute("SELECT profile_image FROM instructor WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM instructor natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    
    return render_template('/manager/edit_userProfile.html', profile=profile, image_data=image_data_base64, status= status)


@account_page.route('/change_password_user', methods=['POST'])
def change_password_user():
    user_id = request.form.get('user_id')
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    cursor = getCursor()
    cursor.execute("SELECT password FROM user WHERE user_id = %s", (user_id,))
    account = cursor.fetchone()

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
    else:
        cursor = getCursor()
        hashed_new_password = current_app.hashing.hash_value(new_password, salt='abcd')
        cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (hashed_new_password, user_id,))
        flash('Your password has been updated successfully.', 'success')

  
    role = request.form.get('role')
    cursor = getCursor()
    if role == 'Instructor':
        cursor.execute('UPDATE instructor SET profile_image = NULL WHERE user_id = %s', (user_id,))
    elif role == 'Member':
        cursor.execute('UPDATE member SET profile_image = NULL WHERE user_id = %s', (user_id,))
    cursor.execute("SELECT status FROM subscriptions WHERE user_id = %s", (user_id,))

    status = cursor.fetchone()
    if role == 'Member':
        cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM member natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    elif role == 'Instructor':
        cursor.execute("SELECT profile_image FROM instructor WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['profile_image']:
            image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')        
        cursor.execute("SELECT * FROM instructor natural join user WHERE  user.user_id = %s", (user_id,))
        profile = cursor.fetchone()

    
    return render_template('/manager/edit_userProfile.html', profile=profile, image_data=image_data_base64, status= status)

@account_page.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('role', None)
   session.pop('user_name', None)
   session.pop('first_name', None)
   session.pop('last_name', None)
   session.pop('position', None)
   session.pop('reminder', None)
   # Redirect to login page
   return redirect(url_for('home'))
   pass

# Functions to extract data from the database and pass to the dashboard
def get_subscription_details(user_id):
    with getCursor() as cursor:
        # Fetch subscription details for a user
        cursor.execute("""SELECT *, DATEDIFF(end_date, CURDATE()) AS days_to_expiration
                            FROM subscriptions
                            WHERE user_id = %s""", (user_id,))
        result = cursor.fetchone()
    return result if result else None

# Functions to extract data from the database and pass to the dashboard
def get_members_subscription_details():
    with getCursor() as cursor:
        # Fetch all subscription details for a manager
        cursor.execute("""SELECT s.*, DATEDIFF(s.end_date, CURDATE()) AS days_to_expiration, CONCAT(m.first_name, ' ', m.last_name) AS member_name
                        FROM subscriptions s
                        JOIN member m ON s.user_id = m.user_id
                        ORDER BY days_to_expiration;
                        """)
        results = cursor.fetchall()
    return results if results else None

def get_member_details(user_id):
    with getCursor() as cursor:
        cursor.execute("""SELECT m.*, s.*
                          FROM member m
                          JOIN subscriptions s ON m.user_id = s.user_id
                          WHERE m.user_id = %s""", (user_id,))
        result = cursor.fetchone()
    return result if result else None

def count_entities(entity_name):
    with getCursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) AS total_{entity_name} FROM {entity_name};")
        result = cursor.fetchone()
    return result[f'total_{entity_name}'] if result else 0

def get_total_members():
    with getCursor() as cursor:
        cursor.execute("""
                        SELECT 
                        COUNT(DISTINCT m.user_id) AS total_members,
                        SUM(CASE WHEN s.status = 'Active' AND s.end_date >= CURDATE() THEN 1 ELSE 0 END) AS total_active_members
                        FROM member m
                        LEFT JOIN (SELECT user_id, status, end_date
                        FROM subscriptions
                        WHERE (user_id, end_date) IN 
                        (SELECT user_id, MAX(end_date) 
                        FROM subscriptions 
                        GROUP BY user_id)
                        ) s ON m.user_id = s.user_id;
                        """)
        result = cursor.fetchone()
    return result if result else 0

def get_workshops(user_id, role):
    with getCursor() as cursor:
        if role == "Manager":
            cursor.execute('''
                SELECT workshop_id, title, date, CONCAT(start_time, ' - ', end_time) AS time 
                FROM workshops
                WHERE date >= CURDATE()
                ORDER BY date ASC
            ''')
        elif role == "Instructor":
            cursor.execute('''
                SELECT workshop_id, title, date, CONCAT(start_time, ' - ', end_time) AS time 
                FROM workshops
                WHERE date >= CURDATE() and workshop_id = %s
                ORDER BY date ASC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT bookings.*, workshops.title, CONCAT(workshops.start_time, ' - ', workshops.end_time) AS time 
                FROM bookings
                JOIN workshops ON bookings.workshop_id = workshops.workshop_id
                WHERE bookings.user_id = %s AND date >= CURDATE()
                ORDER BY date ASC
            ''', (user_id,))
        return cursor.fetchall()


def get_news_items(order):
    with getCursor() as cursor:
        cursor.execute(f"SELECT * FROM news ORDER BY date_published {order}")
        news_items = cursor.fetchall()
    for item in news_items:
        item['image_data'] = image_to_base64(item['news_image'])
    return news_items

def get_member_id(user_id):
    with getCursor() as cursor:
        cursor.execute("SELECT member_id FROM member WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
    return result['member_id'] if result else None

def get_instructor_id(user_id):
    with getCursor() as cursor:
        cursor.execute("SELECT instructor_id FROM instructor WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
    return result['instructor_id'] if result else None

def get_lessons(order):
    with getCursor() as cursor:
        cursor.execute(f"""
            SELECT l.lesson_id, l.name, CONCAT(i.title, ' ', i.first_name, ' ', i.last_name) AS instructor_name, 
            l.date, CONCAT(l.start_time, ' - ', l.end_time) AS time, l.status
            FROM lessons l
            JOIN instructor i ON l.instructor_id = i.instructor_id
            ORDER BY l.date {order}
        """)
        return cursor.fetchall()

def get_lessons_by_instructor(instructor_id, order):
    with getCursor() as cursor:
        if not instructor_id:
            return []
        cursor.execute(f"""
            SELECT l.lesson_id, l.name, l.date, CONCAT(l.start_time, ' - ', l.end_time) AS time, l.status
            FROM lessons l
            WHERE l.instructor_id = %s
            ORDER BY l.date {order}
        """, (instructor_id,))
        return cursor.fetchall()


def get_all_lessons(order):
    with getCursor() as cursor:
        cursor.execute(f"""
            SELECT l.lesson_id, l.name, CONCAT(i.title, ' ', i.first_name, ' ', i.last_name) AS instructor_name, 
            l.date, CONCAT(l.start_time, ' - ', l.end_time) AS time, l.status
            FROM lessons l
            JOIN instructor i ON l.instructor_id = i.instructor_id
            ORDER BY l.date {order}
        """)
        return cursor.fetchall()
    
def get_total_workshops():
    with getCursor() as cursor:
        cursor.execute(f"""
            SELECT 
                (SELECT COUNT(*) FROM workshops) as total_workshops,
                (SELECT COUNT(*) FROM workshops WHERE slots > 0) as available_workshops
            FROM dual 
        """)
        return cursor.fetchone()  
    
def get_total_lessons():
    with getCursor() as cursor:
        cursor.execute(f"""
            SELECT 
                (SELECT COUNT(*) FROM lessons) as total_lessons,
                (SELECT COUNT(*) FROM lessons WHERE status = 'Available') as available_lessons
            FROM dual 
        """)
        return cursor.fetchone()  
    
def get_total_instructors():
    with getCursor() as cursor:
        cursor.execute(f"""
                SELECT COUNT(*) FROM instructor as total_instructors
        """)
        return cursor.fetchone()  
    
def get_upcoming_workshops():
    with getCursor() as cursor:
        cursor.execute("""SELECT w.*, b.status, concat(i.first_name, ' ', i.last_name) AS instructor_name
                        FROM workshops w
                        LEFT JOIN bookings b ON w.workshop_id = b.workshop_id
                        LEFT JOIN instructor i ON w.instructor_id = i.instructor_id
                        WHERE WEEK(date) = WEEK(CURDATE()) AND YEAR(date) = YEAR(CURDATE());
                        """)
        return cursor.fetchall()
    
def get_upcoming_lessons():
    with getCursor() as cursor:
        cursor.execute("""SELECT l.*, concat(i.first_name, ' ', i.last_name) AS instructor_name
                        FROM lessons l
                        LEFT JOIN instructor i ON l.instructor_id = i.instructor_id
                        WHERE WEEK(date) = WEEK(CURDATE())
                        AND YEAR(date) = YEAR(CURDATE());
                        """)
        return cursor.fetchall()
    
def get_my_bookings(user_id):
    with getCursor() as cursor:
        cursor.execute("""SELECT 
                            b.*,
                            COALESCE(w.title, l.name) AS title,
                            COALESCE(w.date, l.date) AS date,
                            COALESCE(w.start_time, l.start_time) AS start_time,
                            COALESCE(w.end_time, l.end_time) AS end_time,
                            COALESCE(w.slots, '') AS workshop_slots,  -- Assuming no equivalent for slots in lessons
                            l.status AS lesson_status,
                            i.first_name AS instructor_first_name, 
                            i.last_name AS instructor_last_name, 
                            i.title AS instructor_title
                        FROM 
                            bookings b
                        LEFT JOIN 
                            workshops w ON b.workshop_id = w.workshop_id
                        LEFT JOIN
                            lessons l ON b.lesson_id = l.lesson_id 
                        LEFT JOIN 
                            instructor i ON (w.instructor_id = i.instructor_id OR l.instructor_id = i.instructor_id)
                        WHERE b.user_id = %s""", (user_id,))
        return cursor.fetchall()
    
def get_workshop_popularity():
    with getCursor() as cursor:
        cursor.execute("""
            SELECT w.title, COUNT(b.workshop_id) AS popularity
            FROM workshops w
            LEFT JOIN bookings b ON w.workshop_id = b.workshop_id
            GROUP BY w.workshop_id
            ORDER BY popularity DESC
            LIMIT 5
        """)
        return cursor.fetchall()
    
def get_yearly_revenue():
    current_year = datetime.now().year
    previous_year = current_year - 1
    with getCursor() as cursor:
        # SQL query to sum up revenue for the current and previous year and calculate the percentage variation
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN YEAR(payment_date) = %s THEN amount ELSE 0 END) AS this_year_revenue,
                SUM(CASE WHEN YEAR(payment_date) = %s THEN amount ELSE 0 END) AS last_year_revenue,
                ROUND(
                    100.0 * (SUM(CASE WHEN YEAR(payment_date) = %s THEN amount ELSE 0 END) - 
                             SUM(CASE WHEN YEAR(payment_date) = %s THEN amount ELSE 0 END)) / 
                    NULLIF(SUM(CASE WHEN YEAR(payment_date) = %s THEN amount ELSE 0 END), 0),
                    2) AS revenue_variation_percent
            FROM payments
            WHERE status = 'Completed'
        """, (current_year, previous_year, current_year, previous_year, previous_year))
        results = cursor.fetchone()
    return results

def get_financial_chart_data():
    today = datetime.today()
    twelve_months_ago = today - timedelta(days=365)
    # Adjusting the dictionary keys to match your requirements
    chart_data = defaultdict(lambda: {'Donation': 0, 'Membership Fee': 0, 'Workshop Fee': 0, 'One-on-One Lesson Fee': 0})

    with getCursor() as cursor:
        cursor.execute("""
            SELECT payment_type, SUM(amount) AS amount, MONTH(payment_date) AS month, YEAR(payment_date) AS year
            FROM payments
            WHERE payment_date BETWEEN %s AND %s AND status = 'Completed'
            GROUP BY payment_type, month, year
            ORDER BY year, month
        """, (twelve_months_ago, today))
        payments = cursor.fetchall()

        # Populating the dictionary with payment data
        for payment in payments:
            key = f"{payment['year']}-{str(payment['month']).zfill(2)}"
            if payment['payment_type'] in chart_data[key]:
                chart_data[key][payment['payment_type']] += payment['amount']

    # Convert to the format needed for the ApexCharts series
    formatted_chart_data = defaultdict(list)
    months = sorted(chart_data.keys())
    for month in months:
        for category in ['Donation', 'Membership Fee', 'Workshop Fee', 'One-on-One Lesson Fee']:
            formatted_chart_data[category].append(chart_data[month][category])

    return {
        'categories': months,
        'series': [{'name': category, 'data': data} for category, data in formatted_chart_data.items()]
    }

def get_workshop_trend():
    cursor = getCursor()
    cursor.execute('SELECT w.title, SUM(b.status = "Completed" OR b.status = "Waitlist") as count \
                    FROM bookings AS b \
                    RIGHT JOIN workshops AS w ON b.workshop_id = w.workshop_id \
                    GROUP BY w.title \
                    HAVING count > 0 \
                    ORDER BY count DESC')
    byTitle = cursor.fetchall()
    cursor.execute('SELECT w.type, SUM(b.status = "Completed" OR b.status = "Waitlist") as count \
                    FROM bookings AS b \
                    RIGHT JOIN workshops AS w ON b.workshop_id = w.workshop_id \
                    GROUP BY w.type \
                    HAVING count > 0 \
                    ORDER BY count DESC')
    byType = cursor.fetchall()
    cursor.execute('SELECT MONTHNAME(w.date) AS months, SUM(b.status = "Completed" OR b.status = "Waitlist") as count \
                    FROM bookings AS b \
                    RIGHT JOIN workshops AS w ON b.workshop_id = w.workshop_id \
                    GROUP BY months \
                    HAVING count > 0 \
                    ORDER BY count DESC;')
    byMonth = cursor.fetchall()
    data = {}
    data['byTitle'] = byTitle
    data['byType'] = byType
    data['byMonth'] = byMonth
    return data

