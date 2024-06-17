from flask import Blueprint
from db import getCursor
from app import *
import base64
from datetime import datetime



schedule_page = Blueprint('schedule_page', __name__,
                        template_folder='templates',
                        static_folder='static')




@schedule_page.route('/instructors', methods=['GET'])

def show_instructors():
    instructor_id = request.args.get('instructor_id', None)
    search_term = request.args.get('search', None) 

    cursor = getCursor()
    cursor.execute("SELECT instructor_id, CONCAT(title, ' ', first_name, ' ', last_name) AS name FROM instructor")
    instructors = cursor.fetchall()

    lessons_query = """
    SELECT l.lesson_id, l.name, CONCAT(i.title, ' ', i.first_name, ' ', i.last_name) AS instructor_name, l.date, CONCAT(l.start_time, ' - ', l.end_time) AS time, l.status
    FROM lessons l
    JOIN instructor i ON l.instructor_id = i.instructor_id
    """
    if instructor_id:
        lessons_query += " WHERE l.instructor_id = %s"
        cursor.execute(lessons_query, (instructor_id,))
    elif search_term: 
        lessons_query += " WHERE l.name LIKE %s"
        search_term = f"%{search_term}%"
        cursor.execute(lessons_query, (search_term,))
    else: 
        cursor.execute(lessons_query)
    lessons = cursor.fetchall()

    return render_template('dashboard.html', instructors=instructors, lessons=lessons)


@schedule_page.route('/view_instructors_list')
def view_instructors_list():
    cursor = getCursor()
    cursor.execute("""SELECT * FROM instructor left join images on instructor.image_id=images.image_id ; """)
    instructors_list = cursor.fetchall()
    for instructor in instructors_list:
        instructor_id = instructor['instructor_id']
        cursor.execute("""
            SELECT lesson_id, name, date, start_time, end_time, status 
            FROM lessons 
            WHERE instructor_id = %s
        """, (instructor_id,))
        instructor['lessons'] = cursor.fetchall()
        if instructor['profile_image']:
            instructor['image_data'] = base64.b64encode(instructor['profile_image']).decode('utf-8')
        else:
            instructor['image_data'] = None
    print(instructors_list)
    return render_template('instructors_list.html', instructors_list=instructors_list)

@schedule_page.route('/manage_lessons', methods=['GET', 'POST'])
def manage_lessons():
    # Ensure the user is logged in and is an instructor or manager
    if 'loggedin' in session:
        cursor = getCursor()
        user_id = session['user_id']
        if session['role'] == 'Instructor':
            # First, find the instructor_id associated with the user_id
            cursor.execute("SELECT instructor_id FROM instructor WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            instructor_id = result['instructor_id'] if result else None

            # If we have found an instructor_id, fetch their lessons
            if instructor_id:
                cursor.execute("""
                    SELECT l.*, CONCAT(i.first_name, ' ', i.last_name) AS instructor_name
                    FROM lessons l
                    JOIN instructor i ON l.instructor_id = i.instructor_id
                    WHERE l.instructor_id = %s
                    ORDER BY date, start_time
                """, (instructor_id,))
                lessons = cursor.fetchall()
        elif session['role'] == 'Manager' or session['role'] == 'Member':
            cursor.execute("""SELECT l.*, CONCAT(i.first_name, ' ', i.last_name) AS instructor_name
                            FROM lessons l
                            JOIN instructor i ON l.instructor_id = i.instructor_id; ORDER BY date, start_time""" )
            lessons = cursor.fetchall()

        return render_template('manage_lessons.html', lessons=lessons, today = date.today())

    else:
        flash("Please log in to view this page.", "danger")
        return redirect(url_for('account_page.login'))


@schedule_page.route('/lesson_detail/<int:lesson_id>')
def lesson_detail(lesson_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT l.*, im.*, i.first_name AS instructor_first_name, i.last_name AS instructor_last_name, 
        i.instructor_id, loc.name as location_name, loc.location_id, m.first_name AS member_first_name, m.last_name AS member_last_name
        FROM lessons l
        JOIN instructor i ON l.instructor_id = i.instructor_id
        JOIN locations loc ON l.location_id = loc.location_id
        LEFT JOIN images im ON l.image_id = im.image_id
        LEFT JOIN member m ON l.member_id = m.member_id
        WHERE l.lesson_id = %s
    """, (lesson_id,))
    lesson = cursor.fetchone()

    # Fetch all locations
    cursor.execute("SELECT location_id, name FROM locations")
    locations = cursor.fetchall()

    # Fetch all instructors
    cursor.execute("SELECT instructor_id, CONCAT(first_name, ' ', last_name) AS name FROM instructor")
    instructors = cursor.fetchall()

    # Fetch lesson types
    cursor.execute("SELECT DISTINCT type FROM lessons")
    lesson_types = cursor.fetchall()

    # Fetch the image data for the lesson
    cursor.execute("SELECT lesson_image FROM lessons WHERE lesson_id = %s", (lesson_id,))
    result = cursor.fetchone()
    image_data_base64 = ""
    if result and result['lesson_image']:
        image_data_base64 = base64.b64encode(result['lesson_image']).decode('utf-8')  

    # Determine if the logged-in user is the one who reserved the lesson
    is_users_lesson = False
    if 'loggedin' in session:
        user_id = session['user_id']
        cursor.execute("SELECT member_id FROM member WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            member_id = result['member_id']
            is_users_lesson = (lesson and lesson.get('member_id') == member_id)

    # Determine if the logged-in user is the instructor who hold the lesson
    is_instructor_lesson = False
    if 'loggedin' in session:
        user_id = session['user_id']
        cursor.execute("SELECT instructor_id FROM instructor WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            instructor_id = result['instructor_id']
            is_instructor_lesson = (lesson and lesson.get('instructor_id') == instructor_id)

    # Get the details of the member who reserved the lesson
    member = None
    if lesson and lesson.get('member_id'):
        cursor.execute("SELECT * FROM member WHERE member_id = %s", (lesson['member_id'],))
        member = cursor.fetchone()

    return render_template('lesson_detail.html', lesson=lesson, lesson_types=lesson_types, locations=locations, instructors=instructors, 
                           member=member, is_users_lesson=is_users_lesson, is_instructor_lesson=is_instructor_lesson, image_data=image_data_base64)


@schedule_page.route('/edit_lesson/<int:lesson_id>', methods=['POST'])
def edit_lesson(lesson_id):
    name = request.form.get('name')
    details = request.form.get('details')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    location_id = request.form.get('location_id')
    type = request.form.get('type')
    price = request.form.get('price')
    cursor = getCursor()

    # Validations for dates and times
    # Parsing start and end times
    start_time_obj = parse_time(start_time)
    end_time_obj = parse_time(end_time)

    if not start_time_obj or not end_time_obj:
        flash("Invalid start or end time format.", 'danger')
        return redirect(url_for('schedule_page.lesson_detail', lesson_id=lesson_id))

    business_start = datetime.strptime('06:00', '%H:%M').time()
    business_end = datetime.strptime('23:59', '%H:%M').time()
    if start_time_obj < business_start or end_time_obj > business_end or start_time_obj >= end_time_obj:
        flash('Schedule time must be within business hours (06:00 - 23:59) and start time must be before end time.', 'danger')
        return redirect(url_for('schedule_page.lesson_detail', lesson_id=lesson_id))
    
    # Check if the duration is exactly one hour
    start_datetime = datetime.combine(datetime.today(), start_time_obj)  # Temporary combine for calculation
    end_datetime = datetime.combine(datetime.today(), end_time_obj)  # Temporary combine for calculation
    if (end_datetime - start_datetime) != timedelta(hours=1):
        flash('Lesson only lasts for an hour.', 'danger')
        return redirect(url_for('schedule_page.lesson_detail', lesson_id=lesson_id))

    if session['role'] == 'Instructor':
        cursor.execute("""
            UPDATE lessons SET name = %s, date = %s, start_time = %s, end_time = %s, location_id = %s, type = %s, details = %s, price = %s
            WHERE lesson_id = %s
        """, (name, date, start_time, end_time, location_id, type, details, price, lesson_id))
    elif session['role'] == 'Manager':
        instructor_id = request.form.get('instructor_id')
        cursor.execute("""
            UPDATE lessons SET name = %s, instructor_id = %s, date = %s, start_time = %s, end_time = %s, location_id = %s, type = %s, details = %s, price = %s
            WHERE lesson_id = %s
        """, (name, instructor_id, date, start_time, end_time, location_id, type, details, price, lesson_id))

    flash('Lesson updated successfully!', 'success')
    return redirect(url_for('schedule_page.lesson_detail', lesson_id=lesson_id))

@schedule_page.route('/add_lesson', methods=['GET', 'POST'])
def add_lesson():
    cursor = getCursor()

    if request.method == 'POST':
        if session['role'] == 'Instructor':
            #Fetch instructor ID based on the logged in user
            cursor.execute("SELECT instructor_id FROM instructor WHERE user_id = %s", (session['user_id'],))
            result = cursor.fetchone()
            instructor_id = result['instructor_id']
            lesson_name = request.form['lessonName']
            location_id = request.form['locationId']
            date = request.form['date']
            start_time = request.form['startTime']
            end_time = request.form['endTime']
            status = 'Available'
            type = request.form.get('type', '') 
            details = request.form.get('details', '')
            price = request.form.get('price', 0.0) 

        elif session['role'] == 'Manager':
            lesson_name = request.form['lessonName']
            instructor_id = request.form['instructorId']
            location_id = request.form['locationId']
            date = request.form['date']
            start_time = request.form['startTime']
            end_time = request.form['endTime']
            status = 'Available'
            type = request.form.get('type', '') 
            details = request.form.get('details', '')
            price = request.form.get('price', 0.0) 
            
        # Validations for dates and times
        if date < datetime.now().strftime('%Y-%m-%d'):
            flash('Lesson date cannot be in the past.', 'danger')
            return redirect(url_for('schedule_page.add_lesson'))
        
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        business_start = datetime.strptime('06:00', '%H:%M').time()
        business_end = datetime.strptime('23:59', '%H:%M').time()
        if start_time_obj < business_start or end_time_obj > business_end or start_time_obj >= end_time_obj:
            flash('Schedule time must be within business hours (06:00 - 23:59) and start time must be before end time.', 'danger')
            return redirect(url_for('schedule_page.add_lesson'))
        
        # Check if the duration is exactly one hour
        start_datetime = datetime.combine(datetime.today(), start_time_obj)  # Temporary combine for calculation
        end_datetime = datetime.combine(datetime.today(), end_time_obj)  # Temporary combine for calculation
        if (end_datetime - start_datetime) != timedelta(hours=1):
            flash('Lesson duration must be exactly one hour.', 'danger')
            return redirect(url_for('schedule_page.add_lesson'))
    
        #Update the lesson details in the database
        cursor.execute("""
                INSERT INTO lessons (name, instructor_id, location_id, date, start_time, end_time, status, type, details, price) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (lesson_name, instructor_id, location_id, date, start_time, end_time, status, type, details, float(price)))
        flash('Lesson added successfully!')
        return redirect(url_for('schedule_page.manage_lessons'))

    cursor.execute("SELECT i.instructor_id, CONCAT(i.first_name, ' ', i.last_name) AS name FROM instructor as i\
                    INNER JOIN user ON i.user_id = user.user_id \
                    WHERE user.status = 'Active'")    
    instructors = cursor.fetchall()
    cursor.execute("SELECT location_id, name FROM locations WHERE status = 'Active'")
    locations = cursor.fetchall()
    # Fetch lesson types
    cursor.execute("SELECT DISTINCT type FROM lessons")
    lesson_types = cursor.fetchall()

    return render_template('add_lesson.html', instructors=instructors, locations=locations, lesson_types=lesson_types)


@schedule_page.route('/delete_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def delete_lesson(lesson_id):
    if request.method == 'POST':
        cursor = getCursor()
        cursor.execute("DELETE FROM lessons WHERE lesson_id = %s", (lesson_id,))
        # Update booking status
        cursor.execute("DELETE FROM bookings WHERE lesson_id = %s", (lesson_id))
        # Handle payments
        cursor.execute("DELETE FROM payments WHERE lesson_id = %s", ( lesson_id))
        flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('schedule_page.manage_lessons')) 



@schedule_page.route('/reserve_lesson/<int:lesson_id>', methods=['POST'])
def reserve_lesson(lesson_id):
    if 'role' in session :
        cursor = getCursor()
        user_id = session.get('user_id')
        cursor.execute("""
            SELECT member_id FROM member WHERE user_id = %s
        """, (user_id,))
        member_result = cursor.fetchone()

        #Fetch details of subscription
        cursor.execute("""SELECT * FROM subscriptions WHERE user_id = %s """, (user_id,))
        subscription = cursor.fetchone()

        #Fetch details of lesson
        cursor.execute("""SELECT * FROM lessons WHERE lesson_id = %s""", (lesson_id,))
        lesson = cursor.fetchone()

        if subscription['status'] != 'Active':
            flash("Your subscription is not active. You cannot make booking at this time.", "danger")
        elif member_result:
            member_id = member_result['member_id']
            cursor.execute("""
                UPDATE lessons SET status = 'Reserved', member_id = %s
                WHERE lesson_id = %s
            """, (member_id, lesson_id))

            #Insert record into payment table
            price = lesson["price"]
            payment_type = 'One-on-One Lesson Fee'
            payment_date = date.today()
            payment_status = 'Pending'
            cursor.execute('INSERT INTO payments (user_id, lesson_id, amount, payment_type, payment_date, status) VALUES (%s, %s, %s, %s, %s, %s)', 
                           (user_id, lesson_id, price, payment_type, payment_date, payment_status))
            
            cursor.execute('INSERT INTO bookings (user_id, lesson_id, booking_date, status)\
                            VALUE (%s,%s,%s,%s)', (session['user_id'], lesson_id, date.today(), 'Reserved'))
            
            flash(f'Lesson reserved successfully! ${lesson["price"]} has been deducted from you account.' , 'success')
        else:
            flash('Member ID not found.', 'danger')
    else:
        flash('You need to be logged in as a member to reserve a lesson.', 'danger')
    return redirect(url_for('schedule_page.lesson_detail', lesson_id=lesson_id))


@schedule_page.route('/cancel_lesson/<int:lesson_id>', methods=['POST'])
def cancel_lesson(lesson_id):
    if 'loggedin' not in session:
        flash('You need to be logged in to cancel a lesson.', 'danger')
        return redirect(url_for('login'))

    cursor = getCursor()
    user_id = session.get('user_id')

    # Fetch details of the lesson
    cursor.execute("SELECT * FROM lessons WHERE lesson_id = %s", (lesson_id,))
    lesson = cursor.fetchone()
    if not lesson:
        flash('Lesson not found.', 'danger')
        return redirect(url_for('home'))

    if session['role'] == 'Member':
        # Member cancels their own booking
        cursor.execute("SELECT member_id FROM member WHERE user_id = %s", (user_id,))
        member_result = cursor.fetchone()
        
        if member_result and lesson['member_id'] == member_result['member_id']:
            # Update lesson status and member_id
            cursor.execute("UPDATE lessons SET status = 'Available', member_id = NULL WHERE lesson_id = %s", (lesson_id,))
            # Update booking status
            cursor.execute("DELETE FROM bookings WHERE user_id = %s AND lesson_id = %s", (user_id, lesson_id))
            # Handle payments
            cursor.execute("DELETE FROM payments WHERE user_id = %s AND lesson_id = %s", (user_id, lesson_id))
            flash('Lesson booking canceled successfully! Refund issued.', 'success')
        else:
            flash('You can only cancel your own lesson bookings.', 'danger')

    elif session['role'] == 'Instructor':
        # Instructor cancels the lesson they are supposed to lead
        cursor.execute("SELECT instructor_id FROM instructor WHERE user_id = %s", (user_id,))
        instructor_result = cursor.fetchone()
        if instructor_result and lesson['instructor_id'] == instructor_result['instructor_id']:
            cursor.execute("UPDATE lessons SET status = 'Available', member_id = NULL WHERE lesson_id = %s", (lesson_id,))
            cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE lesson_id = %s", (lesson_id,))
            # Handle payments for all users booked this lesson
            cursor.execute("DELETE FROM payments WHERE user_id = %s AND lesson_id = %s", (user_id, lesson_id,))
            flash('You have successfully cancelled the lesson. All bookings refunded.', 'success')
        else:
            flash('You can only cancel lessons that you are scheduled to lead.', 'danger')
            
    elif session['role'] == 'Manager':
        # Manager cancels the lesson
        cursor.execute("UPDATE lessons SET status = 'Available', member_id = NULL WHERE lesson_id = %s", (lesson_id,))
        cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE lesson_id = %s", (lesson_id,))
        # Handle payments for all users booked this lesson
        cursor.execute("DELETE FROM payments WHERE user_id = %s AND lesson_id = %s", (user_id, lesson_id,))
        flash('You have successfully cancelled the lesson. All bookings refunded.', 'success')
    else:
        flash('Unauthorized action.', 'danger')
    
    return redirect(url_for('schedule_page.lesson_detail', lesson_id=lesson_id))

@schedule_page.route('/upload_primary_image_lesson/<int:lesson_id>', methods=['POST'])
def upload_lesson_image(lesson_id):
    file = request.files['image']
    if file:
        image_data = file.read()
        cursor = getCursor()
        cursor.execute('UPDATE lessons SET lesson_image = %s WHERE lesson_id = %s', (image_data, lesson_id))
    
    cursor.execute("SELECT * FROM lessons WHERE lesson_id = %s", (lesson_id,))
    return redirect(url_for('schedule_page.lesson_detail',lesson_id=lesson_id))

@schedule_page.route('/delete_image_lesson/<int:lesson_id>', methods=['POST'])
def delete_lesson_image(lesson_id):
    cursor = getCursor()
    # Update the image status if using an image table
    cursor.execute("UPDATE lessons LEFT JOIN images ON lessons.image_id = images.image_id SET lessons.lesson_image = NULL, images.image_status = 'Inactive' WHERE lesson_id = %s", (lesson_id,))
    return redirect(url_for('schedule_page.lesson_detail',lesson_id=lesson_id))

def parse_time(time_str):
    """Try to parse the time string with or without seconds."""
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return None  # returns None if the time format is incorrect
        
