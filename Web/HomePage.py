from flask import Blueprint, render_template, redirect, session, request, jsonify, url_for
import boto3
import re
from boto3.dynamodb.conditions import Attr

home_bp = Blueprint('home', __name__)
@home_bp.route('/home')
def home(items = None, message=None, query = None):
    if 'email' not in session:  # Redirect user to login if email is not in session
        return redirect('/')
    
    # Fetch user details from DynamoDB
    table = boto3.resource('dynamodb').Table('login')
    response = table.get_item(Key={'email': session['email']})
    user_name = response['Item']['user_name']
    dynamodb = boto3.resource('dynamodb')
    subscriptions_table = dynamodb.Table('Subscriptions')
    subscriptions_response = subscriptions_table.scan(
        FilterExpression=Attr('email').eq(session['email'])
    )
    subscriptions_items = subscriptions_response.get('Items', [])
    if query:
        query_items = items
        query_message = message
        return render_template('HomePage.html', subscriptions_items=subscriptions_items,user_name=user_name,query_items = query_items, query_message = query_message )
    return render_template('HomePage.html', subscriptions_items=subscriptions_items,user_name=user_name )

@home_bp.route('/query', methods=['POST', 'GET'])
def query():  
    if request.method == 'POST':
        # Process the form data and query the DynamoDB table
        title = request.form['title']
        year = request.form.get('release_year')
        artist = request.form['artist']
        
        # Check if at least one of the fields is entered
        if not title and not year and not artist:
            message = 'Please enter data in at least one of the fields.'
            return render_template('HomePage.html', message=message)
        
        # Query the DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        music_table = dynamodb.Table('music')
        
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
            item['artist_img'] = "https://trapforment.s3.ap-southeast-2.amazonaws.com/"+artist_img+".jpg"
    
        # Set the message to display under the query form
        message = ''
        if not items:
            message = 'No result is retrieved. Please query again.'
        
        # Render the template with the query results and message
        return home(items, message=message, query = True)

    # Render the query form if the request method is GET
    return home()


@home_bp.route('/subscribe', methods=['POST'])
def subscribe():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscriptions')
    title = request.form['title']
    release_year = request.form['release_year']
    artist = request.form['artist']
    img = request.form['artist_img']
    email = session['email']

    # Check if an item with the same "title" and "email" exists
    existing_item = table.scan(
        FilterExpression="title = :title_val AND email = :email_val",
        ExpressionAttributeValues={
            ":title_val": title,
            ":email_val": email
        }
    )

    # If the item doesn't exist, add it to the table
    if not existing_item['Items']:
        response = table.scan(Select='SPECIFIC_ATTRIBUTES', ProjectionExpression="id")
        items = response['Items']

        if not items:
            index = 1
        else:
            max_value = max([item["id"] for item in items])
            index = max_value + 1

        item = {
            'id': index,
            'title': title,
            'release_year': release_year,
            'artist': artist,
            'artist_img': img,
            'email': email
        }

        table.put_item(Item=item)
    return home()


@home_bp.route('/remove', methods=['POST'])
def remove():
    dynamodb = boto3.resource('dynamodb')
    table_name = "Subscriptions"
     # Get subscription item details from the form
    title = request.form['title']

    # Remove subscription item from DynamoDB table
    table = dynamodb.Table(table_name)
    response = table.scan(
        FilterExpression='title = :title and email = :email',
        ExpressionAttributeValues={
            ':title': title,
            ':email': session['email']
        }
    )
    # Check if the item is found in the table
    if response['Count'] == 1:
        item_id = response['Items'][0]['id']
        
        # Delete the item from the DynamoDB table using the "id" attribute as the key
        table.delete_item(Key={'id': item_id})
    return home()
@home_bp.route('/logout')
def logout():
    session.pop('email', None)  # Remove email from the session
    return redirect(url_for('login.login'))
