from flask import Blueprint
reports_page = Blueprint('reports_page', __name__,
                        template_folder='templates',
                        static_folder='static')

