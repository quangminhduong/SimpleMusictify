from flask import Blueprint, request, render_template, redirect, session
import boto3

login_bp = Blueprint('login', __name__)
table = boto3.resource('dynamodb').Table('login')

def validate_credentials(email, password):
    response = table.get_item(Key={'email': email})
    return response.get('Item') if 'Item' in response else None

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = validate_credentials(email, password)
        if user:
            session['email'] = email  # Store email in the session
            return redirect('/home')
        else:
            error_msg = "Email or password is invalid. Please try again."
            return render_template('Login.html', error=error_msg)
    else:
        return render_template('Login.html')