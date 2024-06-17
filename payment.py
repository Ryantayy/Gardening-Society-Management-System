from flask import Blueprint
from db import getCursor
from app import *
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

payment_page = Blueprint('payment_page', __name__,
                        template_folder='templates',
                        static_folder='static')

@payment_page.route('/payment_on_register', methods=['GET', 'POST'])
def payment_on_register():
    cursor = getCursor()
    cursor.execute('SELECT * FROM prices;')
    prices = cursor.fetchall()
    if request.method == 'POST':
      
        payment_successful = True  
        # Initialize donation_amount to zero
        donation_amount = 0
        if payment_successful:
            # Retrieve temporary saved data
            registration_info = session.pop('registration_info', None)
            if registration_info:
                # Insert user data into the database
                user_name = registration_info.get('user_name')
                password = registration_info.get('password')  
                title = registration_info.get('title')
                first_name = registration_info.get('first_name')
                last_name = registration_info.get('last_name')
                position = registration_info.get('position')
                phone_number = registration_info.get('phone_number')
                email = registration_info.get('email')
                address = registration_info.get('address')
                date_of_birth = registration_info.get('date_of_birth')
                is_student_or_csc = registration_info.get('is_student_or_csc')

                start_date = date.today()
                type = request.form.get('type')
                if type == 'Annual':
                    end_date = date.today() + relativedelta(years=1)
                    amount = Decimal(prices[0]['price']) * Decimal(0.7) if is_student_or_csc else prices[0]['price']  # Apply a 30% discount if applicable
                elif type == 'Monthly':
                    end_date = date.today() + relativedelta(months=1)
                    amount = Decimal(prices[1]['price']) * Decimal(0.7) if is_student_or_csc else prices[1]['price']  # Apply a 30% discount if applicable

                payment_type = 'Membership Fee'
                payment_date = date.today()
                subscription_status = "Active"
                payment_status = 'Completed'

                # Insert into user table
                cursor.execute('INSERT INTO user (user_name, password, role, status) VALUES (%s, %s, %s, "Active")', (user_name, password, 'Member'))
                user_id = cursor.lastrowid

                #Insert data into the Member Table
                cursor.execute('INSERT INTO member (user_id, title, first_name, last_name, position, phone_number, email, address, date_of_birth, is_student_or_csc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (user_id, title, first_name, last_name, position, phone_number, email, address, date_of_birth, is_student_or_csc))
                #Insert data into the Subscriptions Table
                cursor.execute('INSERT INTO subscripations (user_id, type, start_date, end_date, status,price) VALUES (%s, %s, %s, %s, %s,%s)', (user_id, type, start_date, end_date, subscription_status,amount))

                #Insert data into the Payments Table
                cursor.execute('INSERT INTO payments (user_id, amount, payment_type, payment_date, status) VALUES (%s, %s, %s, %s, %s)', (user_id, amount, payment_type, payment_date, payment_status))

                # Check if user made a donation
                donation = request.form.get('donation')
                if donation:
                    donation_amount = abs(float(donation))
                    payment_type = 'Donation'
                    # Insert donation data into the database
                    cursor.execute('INSERT INTO payments (user_id, amount, payment_type, payment_date, status) VALUES (%s, %s, %s, %s, %s)', (user_id, donation_amount, payment_type, payment_date, payment_status))

                rounded_amount = round(float(amount), 2)

                flash(f'You have successfully registered! ${rounded_amount + donation_amount} has been deducted from your account.', 'success')
                # Redirect to login page or wherever you'd like after successful registration
                return redirect(url_for('account_page.login'))
            else:
                flash('Session expired or invalid access.', 'danger')
                return redirect(url_for('account_page.register'))

        else:
            # Handle payment failure
            flash('Payment failed. Please try again.', 'danger')

    # If it's a GET request or payment hasn't been processed yet, show the payment form
    return render_template('payment_on_register.html', prices = prices)

@payment_page.route('/plan_renewal', methods=['GET', 'POST'])
def plan_renewal():
    # Ensure the user is logged in
    if 'loggedin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('account_page.login'))
    
    user_id = session['user_id']  
    cursor = getCursor()
    # Fetch the user's subscription details
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
    subscription = cursor.fetchone()

    # Fetch the user's member details
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    member = cursor.fetchone()
    
    if request.method == 'POST':
        renewal_period = int(request.form.get('renewal_period', 0))

        # Ensure that `subscription['end_date']` is a date object
        current_end_date = subscription['end_date']
        if isinstance(current_end_date, str):
            current_end_date = datetime.strptime(current_end_date, "%Y-%m-%d").date()

        discount = 0.7 if member['is_student_or_csc'] else 1  # Apply a 30% discount if applicable
        
        # Calculate the new end date and amount based on the subscription type
        if subscription['type'] == 'Annual':
            new_end_date = current_end_date + relativedelta(years=renewal_period/12)
            amount = 50 * renewal_period / 12 * discount
        elif subscription['type'] == 'Monthly':
            new_end_date = current_end_date + relativedelta(months=renewal_period)
            amount = 5 * renewal_period * discount  # Corrected the monthly cost calculation
        else:
            # Handle unexpected subscription type
            flash('Invalid subscription type.', 'danger')
            return redirect(url_for('payment_page.plan_renewal'))

        payment_type = 'Membership Fee'
        payment_date = date.today()
        payment_status = 'Completed'

        
        # Update subscription end date and status
        subscription_status = 'Active' if new_end_date > date.today() else 'Inactive'
        cursor.execute('UPDATE subscriptions SET end_date = %s, status = %s WHERE user_id = %s', 
                       (new_end_date, subscription_status, user_id))

        # Insert payment record for the renewal
        cursor.execute('INSERT INTO payments (user_id, amount, payment_type, payment_date, status) VALUES (%s, %s, %s, %s, %s)',
                       (user_id, amount, payment_type, payment_date, payment_status))

        flash(f'Subscription renewal successful. ${amount} has been deducted from your account.', 'success')
        return redirect(url_for('subscription_page.manage_subscription'))
    else:
        # For a GET request, render the renewal form
        return render_template('plan_renewal.html', subscription=subscription)
    
@payment_page.route('/payment_management', methods=['GET', 'POST'])
def payment_management():
    # Ensure the user is logged in
    if 'loggedin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('account_page.login'))
    
    cursor = getCursor()
    query = """
    SELECT p.payment_id,p.user_id, u.user_name, l.type AS lesson_type, l.date, l.start_time, l.end_time, p.amount, p.status  
    FROM payments p
    JOIN user u ON p.user_id = u.user_id
    JOIN lessons l ON p.lesson_id = l.lesson_id
    WHERE p.lesson_id IS NOT NULL;
    """
    cursor.execute(query)
    lessons_payments = cursor.fetchall()

    query = """
    SELECT p.payment_id, p.user_id, u.user_name, w.title AS workshop_title, w.date, w.start_time, w.end_time, p.amount, p.status
    FROM payments p
    JOIN user u ON p.user_id = u.user_id
    JOIN workshops w ON p.workshop_id = w.workshop_id
    WHERE p.workshop_id IS NOT NULL;
    """
    cursor.execute(query)
    workshops_payments = cursor.fetchall()

    return render_template('payment_management.html', lessons_payments=lessons_payments, workshops_payments=workshops_payments)

@payment_page.route('/confirm_payment/<int:payment_id>', methods=['GET', 'POST'])
def confirm_payment(payment_id):
    if 'loggedin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))

    cursor = getCursor()
    cursor.execute('UPDATE payments SET status = %s WHERE payment_id = %s', ('Completed', payment_id))
    cursor.execute('SELECT payment_type FROM payments WHERE payment_id = %s', (payment_id,))
    payment_type = cursor.fetchone()['payment_type']
    return redirect(url_for('payment_page.payment_management'))
    
@payment_page.route('/cancel_payment/<int:payment_id>', methods=['GET', 'POST'])
def cancel_payment(payment_id):
    if 'loggedin' not in session:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))

    cursor = getCursor()
    cursor.execute('UPDATE payments SET status = %s WHERE payment_id = %s', ('Pending', payment_id))
    cursor.execute('SELECT payment_type FROM payments WHERE payment_id = %s', (payment_id,))
    payment_type = cursor.fetchone()['payment_type']
    cursor.close()

    return redirect(url_for('payment_page.payment_management'))

@payment_page.route('/financial_report',methods=['GET'])
def financial_report():
    if 'loggedin' in session and session['role'] == 'Manager':
        cursor = getCursor()
        filter_conditions = "status='Completed'"
        year_filter = request.args.get('totalYearFilter')
        month_filter = request.args.get('totalMonthFilter')
        if year_filter and year_filter != 'All':
            filter_conditions += f" AND YEAR(payment_date)={year_filter}"
        if month_filter and month_filter!= 'All':
            filter_conditions += f" AND monthname(payment_date)='{month_filter}'"

        cursor.execute(f'''SELECT SUM(amount) AS membership_revenue FROM payments
                        WHERE {filter_conditions} and payment_type = 'Membership Fee';''')
        membership_revenue = cursor.fetchone()['membership_revenue']

        cursor.execute(f'''SELECT SUM(amount) AS workshop_revenue FROM payments
                        WHERE {filter_conditions} and payment_type = 'Workshop Fee' ;''')
        workshop_revenue = cursor.fetchone()['workshop_revenue']

        cursor.execute(f'''SELECT SUM(amount) AS lesson_revenue FROM payments
                        WHERE {filter_conditions} and payment_type = 'One-on-One Lesson Fee';''')
        lesson_revenue = cursor.fetchone()['lesson_revenue']

        cursor.execute(f'''SELECT SUM(amount) AS total_revenue FROM payments
                        WHERE {filter_conditions};''')
        total_revenue = cursor.fetchone()['total_revenue']

        return render_template('financial_report.html', membership_revenue=membership_revenue,workshop_revenue=workshop_revenue,lesson_revenue=lesson_revenue,total_revenue=total_revenue, year=year_filter, month=month_filter)

    else:
        flash('Unauthorized Access.', 'danger')
        return redirect(url_for('account_page.dashboard'))