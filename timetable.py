from flask import Blueprint, jsonify
from app import *
from db import getCursor
from datetime import datetime, date, timedelta, time

timetable_page = Blueprint('timetable_page', __name__,
                        template_folder='templates',
                        static_folder='static')

#Showing the calendar
@timetable_page.route('/timetable')
def view_timetable():
    return render_template('timetable.html')

@timetable_page.route('/get_course_info')
def get_course_info():
    cursor = getCursor()
    query = """
        SELECT l.lesson_id AS session_id, l.name AS session_name, l.date, l.start_time, l.end_time, 'Lesson' AS type, i.first_name, i.last_name
        FROM lessons l
        JOIN instructor i ON l.instructor_id = i.instructor_id
        UNION ALL
        SELECT w.workshop_id AS session_id, w.title AS session_name, w.date, w.start_time, w.end_time, 'Workshop' AS type, i.first_name, i.last_name
        FROM workshops w
        JOIN instructor i ON w.instructor_id = i.instructor_id;
    """
    cursor.execute(query)

    courses = cursor.fetchall()

    course_data = []
    for course in courses:
        # Convert timedelta to time object for start_time
        if isinstance(course['start_time'], timedelta):
            seconds = course['start_time'].seconds
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            start_time_obj = time(hour=hours, minute=minutes, second=seconds)
        else:
            start_time_obj = course['start_time']  # Fallback if not a timedelta

        # Similarly for end_time
        if isinstance(course['end_time'], timedelta):
            seconds = course['end_time'].seconds
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            end_time_obj = time(hour=hours, minute=minutes, second=seconds)
        else:
            end_time_obj = course['end_time']  # Fallback if not a timedelta

        start_datetime = datetime.combine(course['date'], start_time_obj).isoformat()
        end_datetime = datetime.combine(course['date'], end_time_obj).isoformat()

        title = f"{course['session_name']} ({course['type']}) - {course['first_name']} {course['last_name']}"
        course_data.append({
            'title': title,
            'start': start_datetime,
            'end': end_datetime,
            'id': course['session_id'],  # Include session ID
            'type': course['type'].lower()  # Include session type and make it lowercase for consistency
        })
        
    return jsonify(course_data)
