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



########################################
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
    if not token or not token.startswith('Bearer '):
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
    return render_template('home.html')

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

@app.route('/notes', methods=['GET'])
def notes():
    user = qr.get_documents_with_status(db, 'User', 'Name', '==', 'Bezel')
    user_id = user[0][1]
    notes = qr.get_all_docs(db, f'User/{user_id}/Note')
    return render_template('notes.html', notes=notes)


# CRUD Routes for Notes
@app.route('/notes/add', methods=['POST'])
def add_note():
    data = request.json
    user = qr.get_documents_with_status(db, 'User', 'Name', '==', 'Bezel')
    user_id = user[0][1]
    note_ref = f'User/{user_id}/Note'

    new_note = {
        "Book_Name": data.get('Book_Name'),
        "Notes": [
            {
                "Page_nr": int(data.get('Page_nr')),
                "Text": data.get('Text')
            }
        ]
    }
    result = qr.get_documents_with_status(db,"User/VsIylI7O9Ew7v9rofgM8/Note","Book_Name","==",new_note["Book_Name"])
    # print(result[0][1])
    if(result == []):
        qr.insert_document(db, note_ref, new_note)
    else:
        qr.insert_into_array(db, note_ref, result[0][1], "Notes", new_note["Notes"][0])
    return jsonify({"success": True, "message": "Notă adăugată cu succes"}), 201


@app.route('/notes/update/<note_id>', methods=['PUT'])
def update_note(note_id):
    # Parse JSON request body
    data = request.json

    # Get the old and new note data
    old_note = {
        "Page_nr": int(data.get('old_Page_nr')),
        "Text": data.get('old_Text')
    }
    print(old_note)
    new_note = {
        "Page_nr": int(data.get('new_Page_nr')),
        "Text": data.get('new_Text')
    }
    print(new_note)
    # Fetch the user
    user = qr.get_documents_with_status(db, 'User', 'Name', '==', 'Bezel')
    user_id = user[0][1]

    # Define the note reference
    collection_name = f'User/{user_id}/Note'
    document_id = note_id

    # Delete the old note
    qr.delete_array_element(db, collection_name, document_id, "Notes", old_note)

    # Add the new note
    qr.insert_into_array(db, collection_name, document_id, "Notes", new_note)

    return jsonify({"success": True, "message": "Notă actualizată cu succes"})


@app.route('/notes/delete/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    # Fetch user data for 'Bezel'
    user = qr.get_documents_with_status(db, 'User', 'Name', '==', 'Bezel')
    user_id = user[0][1]
    collection_name = f'User/{user_id}/Note'
    document_id = note_id

    # Preluăm datele trimise de la frontend
    data = request.json
    print(data)
    page_nr = data.get('Page_nr')
    text = data.get('Text')

    # Validare date primite
    if not page_nr or not text:
        return jsonify({"success": False, "message": "Date invalide trimise"}), 400

    # Construcția datelor pentru ștergere
    note_to_remove = {
        "Page_nr": int(page_nr),  # Convertim la int pentru potrivirea exactă
        "Text": text
    }

    # Șterge nota specifică din array-ul Notes
    try:
        qr.delete_array_element(db, collection_name, document_id, "Notes", note_to_remove)
    except Exception as e:
        return jsonify({"success": False, "message": f"Eroare la ștergerea notei: {str(e)}"}), 500

    result = qr.get_document(db, collection_name, document_id)

    if(result["Notes"] == []):
        qr.delete_document(db, collection_name, document_id)

    return jsonify({"success": True, "message": "Notă ștearsă cu succes"})


@app.route('/notes/view/<note_id>', methods=['GET'])
def view_note(note_id):
    user = qr.get_documents_with_status(db, 'User', 'Name', '==', 'Bezel')
    user_id = user[0][1]
    note_ref = f'User/{user_id}/Note'

    note = qr.get_document(db, note_ref, note_id)
    return jsonify(note)



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
# mara = qr.get_documents_with_status(db,'Book','Name','==','MaRa')
# qr.delete_document(db,"Book",mara[0][1])
# print(mara)
# id = mara[0][1]
# qr.update_existing_document(db,'Book',id,"Name","Mara")
# print(id)
# print(mara)

if __name__ == '__main__':
    app.run(debug=True)