from flask import Blueprint
from db import getCursor
from app import *
import base64
from datetime import date

news_page = Blueprint('news_page', __name__,
                        template_folder='templates',
                        static_folder='static')


@news_page.route('/delete_news/<int:news_id>', methods=['GET', 'POST'])
def delete_news(news_id):
    if 'loggedin' in session:
        cursor = getCursor()
        cursor.execute("DELETE FROM news WHERE news_id = %s", (news_id,))
        flash("News deleted successfully.")
        return redirect(url_for('news_page.manage_news_list'))
    
@news_page.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    if 'loggedin' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            cursor = getCursor()
            cursor.execute("""
                UPDATE news
                SET title = %s, content = %s
                WHERE news_id = %s
            """, (title, content, news_id))

            flash('News updated successfully!')
            return redirect(url_for('news_page.manage_news_list',news_id=news_id))
        else:
            cursor = getCursor()
            cursor.execute("SELECT * FROM news WHERE news_id = %s", (news_id,))
            news_item = cursor.fetchone()

            image_data_base64 = ""
            cursor.execute("SELECT news_image FROM news WHERE news_id = %s", (news_id,))
            result = cursor.fetchone()
            if result and result['news_image']:
                image_data_base64 = base64.b64encode(result['news_image']).decode('utf-8')
            return render_template('edit_news.html', news=news_item, image_data=image_data_base64)
    else:
        flash('Please login to view this page.')
        return redirect(url_for('account_page.login'))
    

@news_page.route('/manage_news/<int:news_id>', methods=['GET'])
def manage_news(news_id):
    if 'loggedin' in session:
        cursor = getCursor()
        cursor.execute("SELECT * FROM news WHERE news_id=%s",(news_id,))
        news_items = cursor.fetchone()
        cursor.execute("SELECT news_image FROM news WHERE news_id = %s", (news_id,))
        result = cursor.fetchone()
        image_data_base64 = ""
        if result and result['news_image']:
            image_data_base64 = base64.b64encode(result['news_image']).decode('utf-8')

        print(image_data_base64)        
        return render_template('news.html', news=news_items, image_data=image_data_base64)
    else:
        flash('Please login to view this page.')
        return redirect(url_for('login'))

@news_page.route('/manage_news_list', methods=['GET', 'POST'])
def manage_news_list():
    if 'loggedin' in session:
        cursor = getCursor()
        cursor.execute("""SELECT n.*, m.first_name, m.last_name
                        FROM news n
                        JOIN manager m ON n.author_id = m.user_id;""")
        news_list = cursor.fetchall()
       
        return render_template('manage_news_list.html', news_list=news_list)
    else:
        flash('Please login to view this page.')
        return redirect(url_for('login'))
    
@news_page.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'loggedin' in session and session['role'] == 'Manager':
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            date_pulished = date.today()
            cursor = getCursor()
            cursor.execute(
                "INSERT INTO news (title, content, date_published, author_id) VALUES (%s, %s, %s, %s)",
                (title, content, date_pulished, session['user_id']))
            flash("News added successfully!")
            return redirect(url_for('news_page.manage_news_list'))
        else:
            return render_template('add_news.html')
    else:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))


@news_page.route('/upload_image/<int:news_id>', methods=['POST'])
def upload_image(news_id):
    if 'loggedin' in session:
        file = request.files['newsImage']
        if file:
            image_data = file.read()
            cursor = getCursor()
            print(image_data)
            cursor.execute('UPDATE news SET news_image = %s WHERE news_id = %s', (image_data, news_id))
            cursor.close()
            flash('News image updated successfully!', 'success')
        else:
            flash('No image selected for uploading.', 'error')
    else:
        flash('You do not have permission to perform this action.', 'error')
    return redirect(url_for('news_page.edit_news', news_id=news_id))

# Delete image for a news item
@news_page.route('/delete_image/<int:news_id>', methods=['POST'])
def delete_image(news_id):
    if 'loggedin' in session:
        cursor = getCursor()
        cursor.execute('UPDATE news SET news_image = NULL WHERE news_id = %s', (news_id,))
        cursor.close()
        flash('News image removed successfully!', 'success')
    else:
        flash('You do not have permission to perform this action.', 'error')
    return redirect(url_for('news_page.edit_news', news_id=news_id))

