from flask import Blueprint
from db import getCursor
from app import *
from werkzeug.datastructures import ImmutableMultiDict


manage_page = Blueprint('manage_page', __name__,
                        template_folder='templates',
                        static_folder='static')

@manage_page.route('/attendance')
def attendance():
    if 'loggedin' in session:
        cursor = getCursor()
        if session['role'] == "Manager":
            cursor.execute('SELECT w.workshop_id, w.title, w.date, w.start_time, w.end_time, lo.name\
                            FROM workshops as w \
                            LEFT JOIN locations as lo ON w.location_id = lo.location_id\
                            ORDER BY w.date ASC, w.start_time ASC')
            workshops = cursor.fetchall()
            cursor.execute('SELECT l.lesson_id, l.name, l.date, l.start_time, l.end_time, lo.name AS location, l.member_id, b.status, m.user_id, m.title, m.first_name, m.last_name\
                           FROM lessons as l \
                           LEFT JOIN locations as lo ON l.location_id = lo.location_id\
                           LEFT JOIN bookings as b ON l.lesson_id = b.lesson_id\
                           LEFT JOIN member as m ON l.member_id = m.member_id \
                           ORDER BY l.date ASC, l.start_time ASC')
            lessons = cursor.fetchall()
        elif session['role'] == "Instructor":
            cursor.execute('SELECT w.workshop_id, w.title, w.date, w.start_time, w.end_time, lo.name\
                            FROM workshops as w \
                            LEFT JOIN locations as lo ON w.location_id = lo.location_id\
                            INNER JOIN instructor AS i ON w.instructor_id = i.instructor_id\
                            WHERE i.user_id = %s\
                            ORDER BY w.date ASC, w.start_time ASC', (session['user_id'],))
            workshops = cursor.fetchall()
            cursor.execute('SELECT l.lesson_id, l.name, l.date, l.start_time, l.end_time, lo.name AS location, l.member_id, b.status, m.user_id, m.title, m.first_name, m.last_name\
                           FROM lessons as l \
                           LEFT JOIN locations as lo ON l.location_id = lo.location_id\
                           LEFT JOIN bookings as b ON l.lesson_id = b.lesson_id\
                           LEFT JOIN member as m ON l.member_id = m.member_id \
                           INNER JOIN instructor AS i ON l.instructor_id = i.instructor_id\
                            WHERE i.user_id = %s\
                           ORDER BY l.date ASC, l.start_time ASC', (session['user_id'],))
            lessons = cursor.fetchall()
        return render_template('attendance_list.html', workshops = workshops, lessons = lessons, role = session['role'])
    flash("Please sign in to continue.")
    return redirect(url_for('home'))

@manage_page.route('/attendance/workshop/<wid>')
def attendance_workshop(wid):
    if 'loggedin' in session:
        if session['role'] == "Instructor" or session['role'] == "Manager":
            cursor = getCursor()
            cursor.execute('SELECT instructor.user_id FROM workshops \
                           INNER JOIN instructor ON workshops.instructor_id = instructor.instructor_id \
                           WHERE workshop_id = %s', (wid,))
            workshopInstructorUserID = cursor.fetchone()
            # Check if instructor holds that workshop
            if session['user_id'] == workshopInstructorUserID['user_id'] or session['role'] == "Manager":
                cursor.execute('SELECT w.workshop_id, w.title, w.date, w.start_time, w.end_time, lo.name\
                                FROM workshops as w \
                                LEFT JOIN locations as lo ON w.location_id = lo.location_id\
                                WHERE w.workshop_id = %s', (wid,))
                workshop = cursor.fetchone()
                cursor.execute('SELECT m.user_id, m.member_id, m.title, m.first_name, m.last_name, b.status FROM bookings AS b\
                               INNER JOIN member AS m ON b.user_id = m.user_id  \
                               WHERE workshop_id = %s ORDER BY m.last_name', (wid,))
                members = cursor.fetchall()
                return render_template('attendance_workshop.html', members = members, workshop = workshop)
    return redirect(url_for('home'))

@manage_page.route('/attendance/workshop/<wid>/<user_id>', methods = ['GET', 'POST'])
def workshop_member_attend(wid, user_id):
    if request.method == 'POST':
        cursor = getCursor()
        try: 
            cursor.execute('UPDATE bookings SET status = %s WHERE workshop_id = %s AND user_id = %s', ("Completed", wid, user_id, ))
            flash('Attendance updated.')
        except:
            flash('Error: user not found.')
        return redirect(url_for('manage_page.attendance_workshop', wid = wid))   
    return redirect(url_for('home'))

@manage_page.route('/attendance/lesson/<lid>/attend', methods = ['GET', 'POST'])
def lesson_attend(lid):
    if request.method == 'POST':
        cursor = getCursor()
        cursor.execute('UPDATE bookings SET status = %s WHERE lesson_id = %s ', ("Completed", lid, ))
        flash('Attendance recorded.')
        return redirect(url_for('manage_page.attendance'))
    return redirect(url_for('home'))

def calculateAttendance(completed, all):
    if all:
        return ("%.0f" % (completed * 100 / all))
    else: 
        return "No Data"

@manage_page.route('/attendance/report')
def attendance_report():
    if 'loggedin' in session:
        if session['role'] == 'Manager':
            cursor = getCursor()
            cursor.execute('SELECT b.booking_id, b.user_id, m.first_name, m.last_name, b.status, \
                            IF(ISNULL(l.name), w.title, l.name) AS wlname, \
                            IF(ISNULL(l.name), w.workshop_id, l.lesson_id) AS wlid, \
                            IF(ISNULL(l.name), "Workshop", "Lesson") AS type,  \
                            IF(ISNULL(l.date), w.date, l.date) AS wldate \
                            FROM bookings as b \
                            INNER JOIN member as m ON b.user_id = m.user_id \
                            LEFT JOIN workshops as w ON b.workshop_id = w.workshop_id \
                            LEFT JOIN lessons as l ON b.lesson_id = l.lesson_id \
                            WHERE l.date <= CURDATE() OR w.date <= CURDATE() \
                            ORDER BY b.booking_id ASC')
            list = cursor.fetchall()
            cursor.execute('SELECT IFNULL(SUM(CASE WHEN b.status="Completed" THEN 1 ELSE 0 END), 0) AS completed, COUNT(*) AS allStatus \
                            FROM bookings as b\
                            LEFT JOIN workshops as w ON b.workshop_id = w.workshop_id \
                            LEFT JOIN lessons as l ON b.lesson_id = l.lesson_id \
                            WHERE l.date <= CURDATE() OR w.date <= CURDATE()')
            data = cursor.fetchone()
            attendance = calculateAttendance(data['completed'], data['allStatus'])
            return render_template('attendance_report.html', list = list, data = data, attendance = attendance, start_date = "", end_date = "", mode = "date")
    return redirect(url_for('home'))

@manage_page.route('/attendace/report/<type>/<int:id>', methods = ['GET', 'POST'])
def attendance_individual_report(type, id):
    if 'loggedin' in session:
        if session['role'] == 'Manager':
            cursor = getCursor()
            if type == "member":
                cursor.execute('SELECT b.booking_id, b.user_id, m.first_name, m.last_name, b.status, \
                                IF(ISNULL(l.name), w.title, l.name) AS wlname, \
                                IF(ISNULL(l.name), w.workshop_id, l.lesson_id) AS wlid, \
                                IF(ISNULL(l.name), "Workshop", "Lesson") AS type,  \
                                IF(ISNULL(l.date), w.date, l.date) AS wldate \
                                FROM bookings AS b \
                                INNER JOIN member AS m ON b.user_id = m.user_id \
                                LEFT JOIN workshops AS w ON b.workshop_id = w.workshop_id \
                                LEFT JOIN lessons AS l ON b.lesson_id = l.lesson_id \
                                WHERE b.user_id = %s AND (w.date <= CURDATE()) OR (l.date <=CURDATE())', (id,))
                list = cursor.fetchall()
                cursor.execute('SELECT IFNULL(SUM(CASE WHEN b.status="Completed" THEN 1 ELSE 0 END),0) AS completed, COUNT(*) AS allStatus \
                                FROM bookings as b \
                                LEFT JOIN workshops as w ON b.workshop_id = w.workshop_id \
                                LEFT JOIN lessons as l ON b.lesson_id = l.lesson_id \
                                WHERE b.user_id = %s AND (l.date <= CURDATE() OR w.date <= CURDATE())', (id,))
                data = cursor.fetchone()
                attendance = calculateAttendance(data['completed'], data['allStatus'])
                return render_template('attendance_report.html', list = list, data = data, attendance = attendance, mode = "member")
            elif type == "Lesson":
                cursor.execute('SELECT b.booking_id, b.user_id, m.first_name, m.last_name, l.name AS wlname, l.date, b.status, "Lesson" AS type, l.lesson_id AS wlid\
                                FROM bookings AS b \
                                INNER JOIN member AS m ON b.user_id = m.user_id \
                                INNER JOIN lessons AS l ON b.lesson_id = l.lesson_id \
                                WHERE b.lesson_id = %s', (id,))
                list = cursor.fetchall()
                cursor.execute('SELECT IFNULL(SUM(CASE WHEN status="Completed" THEN 1 ELSE 0 END),0) AS completed, COUNT(*) AS allStatus \
                                FROM bookings as b \
                                INNER JOIN lessons as l ON b.lesson_id = l.lesson_id \
                                WHERE b.lesson_id = %s AND l.date <= CURDATE()', (id,))
                data = cursor.fetchone()
                attendance = calculateAttendance(data['completed'], data['allStatus'])
                return render_template('attendance_report.html', list = list, data = data, attendance = attendance, mode = "lesson")
            elif type == "Workshop":
                cursor.execute('SELECT b.booking_id, b.user_id, m.first_name, m.last_name, w.title AS wlname, w.date, b.status, "Workshop" AS type, w.workshop_id AS wlid \
                                FROM bookings AS b \
                                INNER JOIN member AS m ON b.user_id = m.user_id \
                                INNER JOIN workshops AS w ON b.workshop_id = w.workshop_id \
                                WHERE b.workshop_id = %s', (id,))
                list = cursor.fetchall()
                cursor.execute('SELECT IFNULL(SUM(CASE WHEN status="Completed" THEN 1 ELSE 0 END),0) AS completed, COUNT(*) AS allStatus \
                                FROM bookings as b \
                                INNER JOIN workshops as w ON b.workshop_id = w.workshop_id \
                                WHERE b.workshop_id = %s AND w.date <= CURDATE()', (id,))
                data = cursor.fetchone()
                attendance = calculateAttendance(data['completed'], data['allStatus'])
                return render_template('attendance_report.html', list = list, data = data, attendance = attendance, mode = "workshop")
            else:
                return redirect(url_for('workshop_page.attendance_report'))
    return redirect(url_for('home'))

@manage_page.route('/attendace/report/date', methods = ['GET', 'POST'])
def attendance_report_date():
    if request.method == 'POST':
        cursor = getCursor()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        print(start_date)
        print(type(start_date))
        cursor.execute('SELECT b.booking_id, b.user_id, m.first_name, m.last_name, b.status, \
                        IF(ISNULL(l.name), w.title, l.name) AS wlname, \
                        IF(ISNULL(l.name), w.workshop_id, l.lesson_id) AS wlid, \
                        IF(ISNULL(l.name), "Workshop", "Lesson") AS type,  \
                        IF(ISNULL(l.date), w.date, l.date) AS date \
                        FROM bookings as b \
                        INNER JOIN member as m ON b.user_id = m.user_id \
                        LEFT JOIN workshops as w ON b.workshop_id = w.workshop_id \
                        LEFT JOIN lessons as l ON b.lesson_id = l.lesson_id \
                        WHERE IF(ISNULL(l.name), w.date, l.date) >= %s AND IF(ISNULL(l.name), w.date, l.date) <= %s',  \
                        (start_date, end_date, ))
        list = cursor.fetchall()
        cursor.execute('SELECT IFNULL(SUM(CASE WHEN b.status="Completed" THEN 1 ELSE 0 END), 0) AS completed, COUNT(*) AS allStatus \
                        FROM bookings as b\
                        LEFT JOIN workshops as w ON b.workshop_id = w.workshop_id \
                        LEFT JOIN lessons as l ON b.lesson_id = l.lesson_id \
                        WHERE IF(ISNULL(l.name), w.date, l.date) >= %s AND IF(ISNULL(l.name), w.date, l.date) <= %s ', \
                        (start_date, end_date,))
        data = cursor.fetchone()
        attendance = calculateAttendance(data['completed'], data['allStatus'])
        return render_template('attendance_report.html', list = list, data = data, attendance = attendance, start_date = start_date, end_date = end_date, mode = "date")
    return redirect(url_for('home'))



@manage_page.route('/priceManagement', methods=['GET', 'POST'])
def priceManagement():
    cursor = getCursor()
    if 'loggedin' in session and session['role'] == 'Manager':
        # Fetch current prices to display in forms
        cursor.execute('SELECT * FROM prices;')
        prices = cursor.fetchall()
        cursor.execute('SELECT * FROM lessons;')
        lessonPrice = cursor.fetchall()
        cursor.execute('SELECT * FROM workshops;')
        workshopPrice = cursor.fetchall()

        if request.method == 'POST':
            # Update membership prices only if fields are present and not empty
            membershipPriceAnnual = request.form.get('annual_subscription', None)
            membershipPriceMonthly = request.form.get('monthly_subscription', None)
            if membershipPriceAnnual is not None:
                cursor.execute('''UPDATE prices SET price = %s WHERE price_type = 'annual_subscription' ''', (membershipPriceAnnual,))
            if membershipPriceMonthly is not None:
                cursor.execute('''UPDATE prices SET price = %s WHERE price_type = 'monthly_subscription' ''', (membershipPriceMonthly,))

            # Update lesson and workshop prices
            for key, value in request.form.items():
                if key.startswith('lesson') and value:
                    lesson_id = key.replace('lesson', '')
                    cursor.execute('''UPDATE lessons SET price = %s WHERE lesson_id = %s''', (value, lesson_id))
                elif key.startswith('workshop') and value:
                    workshop_id = key.replace('workshop', '')
                    cursor.execute('''UPDATE workshops SET price = %s WHERE workshop_id = %s''', (value, workshop_id))

            flash("Price updated successfully!", "success")
            return redirect(url_for('manage_page.priceManagement'))

        return render_template('price_management.html', prices=prices, lessonPrice=lessonPrice, workshopPrice=workshopPrice)
    else:
        return redirect(url_for('account_page.dashboard'))

    
@manage_page.route('/location_management', methods=['GET', 'POST'])
def location_management():
    pass

