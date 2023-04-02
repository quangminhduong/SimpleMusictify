from flask import Blueprint, render_template, redirect, session
import boto3

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
def home():
    if 'email' not in session:  # Redirect user to login if email is not in session
        return redirect('/')

    # Fetch user details from DynamoDB
    table = boto3.resource('dynamodb').Table('login')
    response = table.get_item(Key={'email': session['email']})
    user_name = response['Item']['user_name']

    return render_template('HomePage.html', user_name=user_name)


@home_bp.route('/logout')
def logout():
    session.pop('email', None)  # Remove email from the session
    return redirect('/')
