from flask import Flask, redirect, render_template, request, make_response, session, abort, jsonify, url_for
import secrets
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import timedelta
import os
from dotenv import load_dotenv
import firebase_query as qr
load_dotenv()



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'


# Firebase Admin SDK setup
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

########################################D
""" Authentication and Authorization """

# Decorator for routes that require authentication
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if 'user' not in session:
            return redirect(url_for('login'))
        
        else:
            return f(*args, **kwargs)
        
    return decorated_function


@app.route('/auth', methods=['POST'])
def authorize():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer'):
        return "Unauthorized", 401

    token = token[7:]  # Strip off 'Bearer ' to get the actual token

    try:
        decoded_token = auth.verify_id_token(token) # Validate token here
        session['user'] = decoded_token # Add user to session
        return redirect(url_for('dashboard'))
    
    except:
        return "Unauthorized", 401


#####################
""" Public Routes """

@app.route('/')
def home():
    books = qr.get_all_docs(db,"Book")
    print(books)
    if books:
        return render_template('home.html',books=books)
    else:
        return "error home page", 404

@app.route('/book/<book_id>')
def book_page(book_id):
    book_data = qr.get_document(db, 'Book', book_id)
    if book_data:
        return render_template('book.html', book=book_data, bookId = book_id)
    else:
        return "Error loading Book", 404


# @app.route('/book/<book_id>/quiz')
# def quiz(book_id):
#     book_ref = qr.get_document(db, 'Book', book_id)
#     if book_ref:
#         return render_template('quiz.html', book=book_ref)
#     else:
#         return "Error loading Quiz", 404

@app.route('/book/<book_id>/quiz', methods=['GET', 'POST'])
def quiz(book_id):
    book = qr.get_document(db, 'Book', book_id)
    if not book:
        return "Error loading Book", 404

    if request.method == 'POST':
        correct_answers = {
            'q1': 'Paris',
            'q2': '4',
            'q3': 'Mars'
        }
        user_answers = request.form.to_dict()
        score = sum(1 for q, a in correct_answers.items() if user_answers.get(q) == a)
        return render_template('quiz.html', book=book, score=score, bookkId = book_id)

    return render_template('quiz.html', book=book, bookId = book_id)



@app.route('/mylist')
def mylist():
    book_list = qr.get_all_docs(db, 'Book')
    if book_list:
        return render_template('mylist.html', books = book_list)
    else:
        return "Error MyList", 404

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('signup.html')


@app.route('/reset-password')
def reset_password():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('forgot_password.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from session
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)  # Optionally clear the session cookie
    return response


##############################################
""" Private Routes (Require authorization) """

@app.route('/dashboard')
@auth_required
def dashboard():

    return render_template('dashboard.html')

# data = {
#     "Author": "Ioan Slavici",
#     "Genre": "Drama",
#     "Image": "\\rand1",
#     "Name": "Mara"
# }
# qr.insert_document(db,'Book',data)
# books = qr.get_all_docs(db,'Book')
# print(books[0])
# mara = qr.get_documents_with_status(db,'Book','Name','==','Mara')
# # qr.delete_document(db,"Book",mara[0][1])
# # print(mara)
# id = mara[0][1]
# qr.update_existing_document(db,'Book',id,"Name","Mara")
# print(id)
# print(mara)

if __name__ == '__main__':
    app.run(debug=True)