from flask import Blueprint
from db import getCursor
from app import *
from werkzeug.datastructures import ImmutableMultiDict


location_page = Blueprint('location_page', __name__,
                        template_folder='templates',
                        static_folder='static')

@location_page.route('/location_list', methods=['GET', 'POST'])
def location_list():
    cursor = getCursor()
    if 'loggedin' in session and session['role'] == 'Manager':
        
        cursor.execute('SELECT location_id, name, address, capacity FROM locations WHERE status = "Active";')
        locations = cursor.fetchall()
        return render_template('location_list.html',locations=locations)

    else:
        return redirect(url_for('account_page.dashboard'))
    
@location_page.route('/location_detail/<int:location_id>',methods=['GET', 'POST'])
def location_detail(location_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT *
        FROM locations
        WHERE location_id = %s
    """, (location_id,))
    location = cursor.fetchone()
    return render_template('/manager/edit_locations.html', location=location)


@location_page.route('/edit_location_detail/<int:location_id>', methods=['GET', 'POST'])
def edit_location_detail(location_id):
    name = request.form.get('name')
    address = request.form.get('address')
    capacity = request.form.get('capacity')
    cursor = getCursor()
    cursor.execute("""
            UPDATE locations SET name = %s, address = %s, capacity = %s
            WHERE location_id = %s
        """, (name, address, capacity,location_id,))
    flash('Location updated successfully!', 'success')
    return redirect(url_for('location_page.location_list', location_id=location_id))

@location_page.route('/add_location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        capacity = request.form.get('capacity')
        cursor = getCursor()
        cursor.execute("""
            INSERT INTO locations (name, address, capacity, status)
            VALUES (%s, %s, %s, "Active")
        """, (name, address, capacity,))
        flash('Location added successfully!', 'success')
        return redirect(url_for('location_page.location_list'))
    return render_template('/manager/add_new_location.html')

@location_page.route('/delete_location/<int:location_id>', methods=['GET', 'POST'])
def delete_location(location_id):
    cursor = getCursor()
    cursor.execute('SELECT * FROM workshops WHERE location_id = %s AND date >= CURDATE()', (location_id,))
    workshop_match = cursor.fetchall()
    cursor.execute('SELECT * FROM lessons WHERE location_id = %s AND date >= CURDATE()', (location_id,))
    lesson_match = cursor.fetchall()
    if workshop_match or lesson_match:
        flash('The location cannot be deleted as it is holding workshops and lessons. ', 'danger')
    else:
        cursor.execute('UPDATE locations SET status = "Inactive" WHERE location_id = %s', (location_id,))
        flash('Location deleted successfully!', 'success')
    
    return redirect(url_for('location_page.location_list'))
