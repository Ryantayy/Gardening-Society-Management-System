from flask import Blueprint
from app import *
from db import getCursor
import base64
import time
from datetime import datetime

workshop_page = Blueprint('workshop_page', __name__,
                        template_folder='templates',
                        static_folder='static')

@workshop_page.route('/workshop_list')
def workshop_list():
    # Get list from database
    cursor = getCursor()
    cursor.execute("""SELECT w.*, 
                            CONCAT(i.first_name, ' ', i.last_name) AS instructor_name,
                            l.name AS location
                            FROM workshops w
                            JOIN instructor i ON w.instructor_id = i.instructor_id
                            JOIN locations l ON w.location_id = l.location_id
                            WHERE w.date >= %s
                            ORDER BY w.date, w.start_time""", (date.today(),))
    workshops = cursor.fetchall()
    if 'loggedin' in session:
        if session['role'] == "Manager":
            cursor.execute("""SELECT w.*, 
                    CONCAT(i.first_name, ' ', i.last_name) AS instructor_name,
                    l.name AS location
                    FROM workshops w
                    JOIN instructor i ON w.instructor_id = i.instructor_id
                    JOIN locations l ON w.location_id = l.location_id
                    ORDER BY w.date, w.start_time""")
        loggedin = True
    else:
        loggedin = False
    workshops = cursor.fetchall()

    return render_template('workshop_list.html', workshops=workshops, loggedin = loggedin, today = date.today())

@workshop_page.route('/workshop/<int:workshop_id>')
def workshop(workshop_id):
    cursor = getCursor()
    # Fetch workshop details with location and image information
    cursor.execute("""
        SELECT w.*, im.filename as image_filename, im.image_status as image_status, lo.name as location_name
        FROM workshops w
        LEFT JOIN locations lo ON w.location_id = lo.location_id
        LEFT JOIN images im ON w.image_id = im.image_id
        WHERE w.workshop_id = %s
    """, (workshop_id,))
    workshop = cursor.fetchone()
    
    # Fetch instructor details
    if workshop and workshop['instructor_id']:
        cursor.execute('SELECT * FROM instructor WHERE instructor_id = %s', (workshop['instructor_id'],))
        instructor = cursor.fetchone()
    else:
        instructor = None

    # Fetch all locations
    cursor.execute("SELECT location_id, name FROM locations")
    locations = cursor.fetchall()

    # Fetch all instructors
    cursor.execute("SELECT instructor_id, CONCAT(first_name, ' ', last_name) AS name FROM instructor")
    instructors = cursor.fetchall()

    # Fetch workshop types
    cursor.execute("SELECT DISTINCT type FROM workshops")
    workshop_types = cursor.fetchall()

    # Fetch participants of the selected workshop
    cursor.execute("""
        SELECT b.*, m.first_name, m.last_name, m.email, m.phone_number
        FROM bookings b
        LEFT JOIN member m ON b.user_id = m.user_id
        WHERE b.workshop_id = %s
    """, (workshop_id,))
    participants = cursor.fetchall()

    cursor.execute("SELECT workshop_image FROM workshops WHERE workshop_id = %s", (workshop_id,))
    result = cursor.fetchone()
    image_data_base64 = ""
    if result and result['workshop_image']:
        image_data_base64 = base64.b64encode(result['workshop_image']).decode('utf-8')  
    loggedin = 'loggedin' in session
    role = session.get('role', '')
    joined = None
    if loggedin:
        # Check if user has already booked the workshop
        cursor.execute('SELECT status FROM bookings WHERE workshop_id = %s AND user_id = %s', (workshop_id, session['user_id']))
        joined = cursor.fetchone()
    print(workshop)
    return render_template('workshop_detail.html', workshop=workshop, instructor=instructor, instructors=instructors,
                           locations=locations, workshop_types=workshop_types, role=role, workshop_id=workshop_id,
                           joined=joined, loggedin=loggedin, participants=participants,image_data=image_data_base64, today = date.today())




@workshop_page.route('/upload_primary_image_workshop/<int:workshop_id>', methods=['POST'])
def upload_workshop_image(workshop_id):
    file = request.files['image']
    if file:
        image_data = file.read()
        cursor = getCursor()
        cursor.execute('UPDATE workshops SET workshop_image = %s WHERE workshop_id = %s', (image_data, workshop_id))
    
    cursor.execute("SELECT * FROM workshops WHERE workshop_id = %s", (workshop_id,))
    return redirect(url_for('workshop_page.workshop',workshop_id=workshop_id))

@workshop_page.route('/delete_image_workshop/<int:workshop_id>', methods=['POST'])
def delete_workshop_image(workshop_id):
    cursor = getCursor()
    # Update the image status if using an image table
    cursor.execute("UPDATE workshops LEFT JOIN images ON workshops.image_id = images.image_id SET workshops.workshop_image = NULL, images.image_status = 'Inactive' WHERE workshop_id = %s", (workshop_id,))
    return redirect(url_for('workshop_page.workshop',workshop_id=workshop_id))



@workshop_page.route('/workshop/<workshop_id>/book', methods = ['POST', 'GET'])
def book_workshop(workshop_id):
    if request.method == 'POST' and 'role' in session :
        cursor = getCursor()

        user_id = session.get('user_id')
        cursor.execute("""
            SELECT member_id FROM member WHERE user_id = %s
        """, (user_id,))
        member_result = cursor.fetchone()

        # Check if subscribed
        cursor.execute('SELECT start_date, end_date, status FROM subscriptions WHERE user_id = %s ORDER BY end_date DESC LIMIT 1', (session['user_id'],))
        subscription = cursor.fetchone()

        # Fetch workshop details
        cursor.execute('SELECT * FROM workshops WHERE workshop_id = %s', (workshop_id,))
        workshop = cursor.fetchone()

        if subscription['status'] == "Active" and subscription['start_date'] <= workshop['date'] <= subscription['end_date']:
            member_id = member_result['member_id']
            cursor.execute("""UPDATE workshops SET slots = slots - 1
                           WHERE workshop_id = %s""", (workshop_id,))

            cursor.execute('SELECT title, capacity, slots, price FROM workshops where workshop_id = %s', (workshop_id,))
            workshop = cursor.fetchone()
            title = workshop['title']

            if workshop['slots'] > 0:
                status = "Reserved"
                cursor.execute('INSERT INTO payments (user_id, workshop_id, amount, payment_type, payment_date, status)\
                                VALUE (%s, %s, %s, %s, %s, %s)', (session['user_id'], workshop_id, workshop['price'], "Workshop Fee", date.today(), "Completed",))
                flash(f'Booking made successfully. ${workshop["price"]} has been charged.', 'success')
            else:
                status = "Waitlist"
                cursor.execute('INSERT INTO payments (user_id, workshop_id, amount, payment_type, payment_date, status)\
                                VALUE (%s, %s, %s, %s, %s, %s)', (session['user_id'], workshop_id, workshop['price'], "Workshop Fee", date.today(), "Pending",))
                flash(f'Waitlist joined in workshop {title}')
            cursor.execute('INSERT INTO bookings (user_id, workshop_id, booking_date, status)\
                            VALUE (%s,%s,%s,%s)', (session['user_id'], workshop_id, date.today(), status, ))
            return redirect(url_for('workshop_page.workshop', workshop_id=workshop_id))
        
        else:
            flash('Subscription must be active on the date of the workshop for joining.')
    return redirect(url_for('workshop_page.workshop', workshop_id=workshop_id))

@workshop_page.route('/workshop/<workshop_id>/cancel_booking', methods=['POST'])
def cancel_booking(workshop_id):
    if 'loggedin' in session and session['role'] == 'Member':
        cursor = getCursor()
        user_id = session.get('user_id')

        try:
            #Fetch details of workshop
            cursor.execute("""SELECT * FROM workshops WHERE workshop_id = %s """, (workshop_id,))
            workshop = cursor.fetchone()

            if workshop:
                # Update workshop capacity and remove member
                cursor.execute("""
                    UPDATE workshops SET slots = slots + 1
                    WHERE workshop_id = %s
                """, (workshop_id,))

                # Delete booking record
                cursor.execute("""DELETE FROM bookings 
                  WHERE user_id = %s AND workshop_id = %s
                """, (user_id, workshop_id))

                # Delete record from payment table
                cursor.execute("""
                    DELETE FROM payments 
                    WHERE user_id = %s AND workshop_id = %s
                """, (user_id, workshop_id))

                flash(f'Booking cancelled successfully! ${workshop["price"]} has been refunded to you account.' , 'success')
                return redirect(url_for('workshop_page.workshop', workshop_id=workshop_id))

            else:
                flash('You can only cancel workshops that you have enrolled in.', 'danger')
                cursor.execute("ROLLBACK")
                return redirect(url_for('workshop_page.workshop', workshop_id=workshop_id))
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            flash('Failed to cancel the workshop due to a system error.', 'danger')
            return redirect(url_for('workshop_page.workshop', workshop_id=workshop_id))

    else:
        flash('You need to be logged in as a member to cancel a booking.', 'danger')

    return redirect(url_for('workshop_page.workshop', workshop_id=workshop_id))

@workshop_page.route('/new_workshop', methods = ('GET', 'POST'))
def new_workshop():
    cursor = getCursor()

    if request.method == 'POST':
        if session['role'] == "Manager":
            workshop_name = request.form['workshopName']
            instructor_id = request.form['instructorId']
            location_id = request.form['locationId']
            date = request.form['date']
            start_time = request.form['startTime']
            end_time = request.form['endTime']
            type = request.form.get('type', '') 
            details = request.form.get('details', '')
            price = request.form.get('price', 0.0)
            capacity = request.form.get('capacity')
            slots = capacity

            # Validations for dates and times
            if date < datetime.now().strftime('%Y-%m-%d'):
                flash('Workshop date cannot be in the past.', 'danger')
                return redirect(url_for('schedule_page.add_lesson'))
            
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            business_start = datetime.strptime('06:00', '%H:%M').time()
            business_end = datetime.strptime('23:59', '%H:%M').time()
            if start_time_obj < business_start or end_time_obj > business_end or start_time_obj >= end_time_obj:
                flash('Schedule time must be within business hours (06:00 - 23:59) and start time must be before end time.', 'danger')
                return redirect(url_for('workshop_page.new_workshop'))

            #Update the lesson details in the database
            cursor.execute("""
                    INSERT INTO workshops (title, type, details, location_id, instructor_id, price, capacity, slots, date, start_time, end_time) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (workshop_name, type, details, location_id, instructor_id, float(price), capacity, slots, date, start_time, end_time))
            flash('Workshop added successfully!', 'success')
    
    # Fetch all instructors
    cursor.execute("SELECT i.instructor_id, CONCAT(i.first_name, ' ', i.last_name) AS name FROM instructor as i\
                    INNER JOIN user ON i.user_id = user.user_id \
                    WHERE user.status = 'Active'")
    instructors = cursor.fetchall()
    # Fetch all locations
    cursor.execute("SELECT location_id, name FROM locations WHERE status = 'Active'")
    locations = cursor.fetchall()
    # Fetch workshop types
    cursor.execute("SELECT DISTINCT type FROM workshops")
    workshop_types = cursor.fetchall()

    return render_template('add_workshop.html', instructors = instructors, locations = locations, workshop_types = workshop_types)

@workshop_page.route('/<workshop_id>/edit', methods = ('GET', 'POST'))
def edit_workshop(workshop_id):
    if request.method == 'POST':
        # Get database cursor
        cursor = getCursor()
        try:
            # Retrieve data from form
            title = request.form['name']
            details = request.form['details']
            instructor_id = request.form['instructor_id']
            location_id = request.form['location_id']
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            type = request.form['type']
            price = request.form['price']
            capacity = int(request.form['capacity'])
            
            # Validations for dates and times
            start_time_obj = parse_time(start_time)
            end_time_obj = parse_time(end_time)

            if not start_time_obj or not end_time_obj:
                flash("Invalid start or end time format.", 'danger')
                return redirect(url_for('workshop_page.workshop', workshop_id = workshop_id))

            business_start = datetime.strptime('06:00', '%H:%M').time()
            business_end = datetime.strptime('23:59', '%H:%M').time()
            if start_time_obj < business_start or end_time_obj > business_end or start_time_obj >= end_time_obj:
                flash('Schedule time must be within business hours (06:00 - 23:59) and start time must be before end time.', 'danger')
                return redirect(url_for('workshop_page.workshop', workshop_id= workshop_id))

            # Validate Capacity 
            # Fetch participants' details
            cursor.execute("""
                SELECT b.*, m.*
                FROM bookings b
                LEFT JOIN member m ON b.user_id = m.user_id
                WHERE b.workshop_id = %s
            """, (workshop_id,))
            participants = cursor.fetchall()

            # Count participants
            participants_count = len(participants)

            if workshop and capacity < participants_count:
                flash('The capacity cannot be set lower than the current number of enrolled participants.', 'danger')
                return redirect(url_for('workshop_page.workshop', workshop_id = workshop_id))
            
            # Update the workshop details in the database
            cursor.execute("""
                UPDATE workshops
                SET title = %s, details = %s, instructor_id = %s, location_id = %s, 
                    date = %s, start_time = %s, end_time = %s, type = %s, price = %s, capacity = %s
                WHERE workshop_id = %s
            """, (title, details, instructor_id, location_id, date, start_time, end_time, type, price, capacity, workshop_id))

            flash('Workshop updated successfully!', 'success')
        except Exception as e:

            flash(f'Error updating workshop: {str(e)}', 'danger')

        # Redirect to the edited workshop's detail page or wherever you see fit
        return redirect(url_for('workshop_page.workshop', workshop_id= workshop_id))

    # If it's not a POST request or some other issue, redirect to the home or an error page
    return redirect(url_for('home'))


@workshop_page.route('/<workshop_id>/delete', methods = ('GET', 'POST'))
def delete_workshop(workshop_id):
    if request.method == 'POST':
        cursor = getCursor()
        cursor.execute('DELETE FROM workshops WHERE workshop_id = %s', (workshop_id, ))
        # Delete booking record
        cursor.execute("""DELETE FROM bookings WHERE workshop_id = %s""", (workshop_id, ))

        # Delete record from payment table
        cursor.execute("""DELETE FROM payments WHERE workshop_id = %s""", (workshop_id, ))
        flash("Workshop deleted.")
        return redirect(url_for('workshop_page.workshop_list'))
    flash("Invalid request.")
    return redirect(url_for('home'))

def parse_time(time_str):
    """Try to parse the time string with or without seconds."""
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return None  # returns None if the time format is incorrect