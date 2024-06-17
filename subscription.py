from flask import Blueprint
from db import getCursor
from app import *
from datetime import date
import base64
from decimal import Decimal


subscription_page = Blueprint('subscription_page', __name__,
                        template_folder='templates',
                        static_folder='static')

@subscription_page.route('/manage_subscription', methods=['GET', 'POST'])
def manage_subscription():
    if 'loggedin' not in session:
        return redirect(url_for('login_page'))  # Redirect to login if not logged in

    user_id = session['user_id']
    cursor = getCursor()

    # Common code for fetching user profile and payment history
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()
    cursor.execute("SELECT * FROM payments WHERE user_id = %s ORDER BY payment_date DESC", (user_id,))
    payment_history = cursor.fetchall()

    cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    image_data_base64 = ""
    if result and result['profile_image']:
        image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')    

    if session['role'] == 'Member':
        cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
        subscription = cursor.fetchone()
        
        if not subscription:
            flash("You do not have an active subscription.", "danger")
            return redirect(url_for('subscription_page.manage_subscription'))  

        if request.method == 'POST':
            subscription_type = request.form.get('type')
            cursor.execute("SELECT * FROM prices")
            prices = cursor.fetchall()

            if subscription_type == 'Annual':
                price = Decimal(prices[0]['price']) * Decimal(0.7) if profile['is_student_or_csc'] == 1 else prices[0]['price']  # Apply a 30% discount if applicable
                cursor.execute("UPDATE subscriptions SET type = %s, price = %s WHERE user_id = %s", (subscription_type, price, user_id))
            elif subscription_type == 'Monthly':
                price = Decimal(prices[1]['price']) * Decimal(0.7) if profile['is_student_or_csc'] == 1 else prices[1]['price']  # Apply a 30% discount if applicable
                cursor.execute("UPDATE subscriptions SET type = %s, price = %s WHERE user_id = %s", (subscription_type, price, user_id))

            if cursor.rowcount > 0:
                flash("Subscription updated successfully.", "success")
            else:
                flash("No changes were made to your subscription.", "info") 
            return redirect(url_for('subscription_page.manage_subscription'))  

    return render_template('manage_subscription.html', profile=profile, subscription=subscription, payment_history=payment_history, image_data = image_data_base64)

#Route for Manager to edit subscription
@subscription_page.route('/manage_user_subscription/<int:user_id>', methods=['GET', 'POST'])
def manage_user_subscription(user_id):
    if 'loggedin' not in session:
        return redirect(url_for('login_page'))

    cursor = getCursor()
    subscription = None  # Defaulting subscription to None

    if request.method == 'POST':
        if 'send_reminder' in request.form:
            # Send reminder logic
            cursor.execute("UPDATE member SET reminder_date = %s WHERE user_id = %s", (date.today(), user_id))
            flash('Reminder sent successfully!', 'success')
            return redirect(url_for('subscription_page.manage_user_subscription', user_id=user_id))
        else:
            # Handling POST request to update subscription details
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            subscription_type = request.form.get('type')
            status = request.form.get('status')

            cursor.execute("""UPDATE subscriptions
                            SET `start_date` = %s, `end_date` = %s, `type` = %s, `status` = %s
                            WHERE `user_id` = %s
                        """, (start_date, end_date, subscription_type, status, user_id))
            if cursor.rowcount > 0:
                flash("Subscription updated successfully.", "success")
            else:
                flash("No changes were made to user's subscription.", "info")

    # Fetch current subscription details
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
    subscription = cursor.fetchone()

    if not subscription:
        flash("This user does not have an active subscription.", "danger")
        return redirect(url_for('subscription_page.subscribe'))
    
    # Common code for fetching user profile and payment history
    cursor.execute("SELECT * FROM member WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()
    cursor.execute("SELECT * FROM payments WHERE user_id = %s ORDER BY payment_date DESC", (user_id,))
    payment_history = cursor.fetchall()

    cursor.execute("SELECT profile_image FROM member WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    image_data_base64 = ""
    if result and result['profile_image']:
        image_data_base64 = base64.b64encode(result['profile_image']).decode('utf-8')    

    # Display the subscription management page
    return render_template('manage_subscription.html', subscription=subscription, profile=profile, payment_history=payment_history, image_data = image_data_base64)

@subscription_page.route('/cancel_membership', methods=['GET', 'POST'])
def cancel_membership():
    if 'loggedin' in session and session['role'] == 'Member':
        cursor = getCursor()
        user_id = session.get('user_id')
        if not user_id:
            flash("User not found.", "danger")
            return redirect(url_for('subscription_page.manage_subscription'))

        # Update the subscription status to 'Inactive'
        try:
            cursor.execute("""
                UPDATE subscriptions
                SET status = 'Inactive'
                WHERE user_id = %s
            """, (user_id,))
            flash("Your membership has been successfully cancelled.", "success")
        except Exception as e:
            cursor.rollback()
            flash(f"An error occurred: {e}", "danger")

        return redirect(url_for('subscription_page.manage_subscription'))
    else:
        flash("You must be logged in to perform this action.", "danger")
        return redirect(url_for('app.login'))


# Member Subscription list
@subscription_page.route('/member_subscriptionlist')
def member_subscriptionlist():
    if 'loggedin' in session and session['role'] == 'Manager':
        cursor = getCursor()
        cursor.execute("""SELECT * FROM member m natural join subscriptions s
                        ORDER BY s.end_date""")
        subscriptions = cursor.fetchall()
        today = date.today()
        for s in subscriptions:
            if s['end_date'] <= today:
                s['check'] = '0'
            elif  (s['end_date'] - today).days <= 15:
                s['check'] = '1'
            else:
                s['check'] = '2'
        return render_template('member/member_subscriptionlist.html',  subscriptions=subscriptions)
    else:
        return redirect(url_for('account_page.dashboard'))
    

@subscription_page.route('/send_reminder', methods=['POST'])
def send_reminder():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        cursor = getCursor()
        cursor.execute("SELECT * FROM member WHERE user_id = %s ", (user_id,))
        user = cursor.fetchone()  
        if user:
            cursor.execute("UPDATE member SET reminder_date = %s  WHERE user_id = %s ", (date.today(), user_id))
            flash('Reminder sent successfully!', 'success')
        else:
            flash('User not found!', 'error')
        return redirect(url_for('subscription_page.member_subscriptionlist'))
    