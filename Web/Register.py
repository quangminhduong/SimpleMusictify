from flask import Blueprint, render_template, request, redirect, url_for

import boto3

register_bp = Blueprint('register', __name__)

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    message = None
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['user_name']
        password = request.form['password']

        # Check if the email already exists in the DynamoDB table
        response = table.get_item(Key={'email': email})
        if 'Item' in response:
            error = 'Email already exists!'
        else:
            # Add the new user to the DynamoDB table
            table.put_item(Item={'email': email, 'user_name': username, 'password': password})
            message = 'User created, return to login!'

    return render_template('Register.html', error=error, message=message)

