from flask import Blueprint, render_template, redirect, session, request, jsonify
import boto3
import re

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

@home_bp.route('/query', methods=['POST', 'GET'])
def query():
    user_name = None
    
    if 'email' in session:
        # Fetch user details from DynamoDB
        table = boto3.resource('dynamodb').Table('login')
        response = table.get_item(Key={'email': session['email']})
        user_name = response['Item']['user_name']
    
    if request.method == 'POST':
        # Process the form data and query the DynamoDB table
        title = request.form['title']
        year = request.form.get('release_year')
        artist = request.form['artist']
        
        # Check if at least one of the fields is entered
        if not title and not year and not artist:
            message = 'Please enter data in at least one of the fields.'
            return render_template('HomePage.html', message=message, user_name=user_name)
        
        # Query the DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        music_table = dynamodb.Table('Music')
        
        # Create a list of FilterExpressions and ExpressionAttributeValues
        filters = []
        values = {}
        
        # Add a filter expression for the title
        if title:
            filters.append("contains(title, :title)")
            values[':title'] = title
        
        # Add a filter expression for the year
        if year:
            filters.append("contains(release_year, :release_year)")
            values[':release_year'] = year

        
        # Add a filter expression for the artist
        if artist:
            filters.append("contains(artist, :artist)")
            values[':artist'] = artist
        
        # Combine all filter expressions into a single expression
        if title and year and artist:
            filter_expression = "contains(title, :title) AND contains(release_year, :release_year) AND contains(artist, :artist)"
        else:
            filter_expression = " OR ".join(filters)
        
        response = music_table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=values
        )

        # Modify the response to include artist_img
        items = response['Items']
        for item in items:
            artist_name = item['artist']
            artist_img = ''.join(x.capitalize() for x in re.split(r'[\W_]+', artist_name) if x)
            item['artist_img'] = "https://trapforment4.s3.amazonaws.com/"+artist_img+".jpg"
    
        # Set the message to display under the query form
        message = ''
        if not items:
            message = 'No result is retrieved. Please query again.'
        
        # Render the template with the query results and message
        return render_template('HomePage.html', results=items, message=message, user_name=user_name)

    # Render the query form if the request method is GET
    return render_template('HomePage.html', user_name=user_name)


@home_bp.route('/subscribe', methods=['POST'])
def subscribe():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscriptions')
    title = request.form['title']
    release_year = request.form['release_year']
    artist = request.form['artist']
    img = request.form['artist_img']
    email = session['email']
    
    response = table.scan()
    items = response['Items']
    index = len(items) + 1
    
    item = {
        'Index': index,
        'title': title,
        'release_year': release_year,
        'artist': artist,
        'artist_img': img,
        'email': email
    }
    
    table.put_item(Item=item)
    
    # Fetch user details from DynamoDB
    table = boto3.resource('dynamodb').Table('login')
    response = table.get_item(Key={'email': session['email']})
    user_name = response['Item']['user_name']
    
    return display_subscriptions(email=email, user_name=user_name)


@home_bp.route('/subscriptions', methods=['GET'])
def display_subscriptions(email=None, user_name=None):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscriptions')
    response = table.scan()
    items = response['Items']
    if 'email' in session:
        # Fetch user details from DynamoDB
        table = boto3.resource('dynamodb').Table('login')
        response = table.get_item(Key={'email': session['email']})
        user_name = response['Item']['user_name']
        return render_template('HomePage.html', subscriptions=items, email=session['email'], user_name=user_name)
    else:
        return render_template('HomePage.html', subscriptions=items)


@home_bp.route('/logout')
def logout():
    session.pop('email', None)  # Remove email from the session
    return redirect('/')
