from flask import Flask, render_template, redirect, request, session
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import bcrypt

app = Flask(__name__)

app.secret_key = 'Evh|4@%P{c/1<u%<LMMzUCg_5bk+V*'

# MongoDB connection URI
uri = "mongodb+srv://kumarmanket135:KHZTBgh89JK0oaxI@cluster0.ncrvh3r.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Connect to the 'flask_app' database and 'users' collection
db = client.delhidate
users_collection_male = db.male_user
users_collection_female = db.female_user

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/backtologin')
def login():
    return redirect('/')

@app.route('/signuppage')
def signup_page():
  return render_template('signup.html')

@app.route('/login', methods=['POST'])
def home():
    # Retrieve form data
    username = request.form['username']
    password = request.form['password'].encode('utf-8')  # Encode password to bytes

    # Attempt to find the user in the female collection
    user = users_collection_female.find_one({'username': username})
    if user and bcrypt.checkpw(password, user['password']):
        session['username'] = username
        session['gender'] = 'female'
        session['insta_link'] = user.get('insta_link', '')  # Store Instagram link in session
        return render_template('interest.html', user_name=session['username'])
    else:
        # If not found in the female collection, try the male collection
        user = users_collection_male.find_one({'username': username})
        if user and bcrypt.checkpw(password, user['password']):
            session['username'] = username
            session['gender'] = 'male'
            session['insta_link'] = user.get('insta_link', '')  # Store Instagram link in session
            return render_template('interest.html', user_name=session['username'])

    return "User doesn't exist"



import random

@app.route('/interest', methods=['POST'])
def interest():
    if 'username' in session:
        username = session['username']
        gender = session['gender']  # Assuming gender is stored in the session

        # Retrieve form data
        street_food = request.form.get('street-food')  # Ensure these match your form's `name` attributes
        weekend_activity = request.form.get('weekend-activity')
        music_genre = request.form.get('music-genre')
        hangout_place = request.form.get('hangout-place')

        interests = {
            "street_food": street_food,
            "weekend_activity": weekend_activity,
            "music_genre": music_genre,
            "hangout_place": hangout_place
        }

        # Determine the user's collection and the opposite gender collection
        current_users_collection = users_collection_male if gender == 'male' else users_collection_female
        opposite_gender_collection = users_collection_female if gender == 'male' else users_collection_male

        # Update the current user's interests
        current_users_collection.update_one({'username': username}, {'$set': {'interests': interests}})

        # Find matches in the opposite gender collection
        query = {
            "interests.street_food": street_food,
            "interests.weekend_activity": weekend_activity,
            "interests.music_genre": music_genre,
            "interests.hangout_place": hangout_place
        }
        potential_matches = list(opposite_gender_collection.find(query))

      
        if potential_matches:
           
            selected_match = random.choice(potential_matches)
            match_insta_link = selected_match.get('insta_link', '')

        
            current_users_collection.update_one(
                {'username': username},
                {'$set': {'match': selected_match['username']}}
            )

            # Redirect or inform the user that a match has been found
            return render_template('index.html', match_username=selected_match['username'],match_insta_link=match_insta_link)
        else:
            return "No matches found."

    else:
        return redirect('/login')



@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        insta_link = request.form.get('instagram_link')
        salt = bcrypt.gensalt()

        # Hash the password using the salt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Initialize collection variable
        users_collection = None
        existing_user = None 

        # Check gender and assign corresponding collection
        if gender == "male":
            users_collection = users_collection_male
            existing_user = users_collection.find_one({'username': username})
        elif gender == "female":
            users_collection = users_collection_female
            existing_user = users_collection.find_one({'username': username})

        # If user exists in the respective collection, return error message
        if existing_user:
            return "Username already exists. Please choose another username."

        user_data = {
            'username': username,
            'password': hashed_password,
            'gender': gender,
            'dob': dob,
            'insta_link': insta_link
        }

        try:
            # Insert the document into the designated collection
            if users_collection is not None:  # Check if users_collection is not None
                users_collection.insert_one(user_data)
                return redirect('/')
            else:
                return "Invalid gender specified."
        except DuplicateKeyError:
            return "An error occurred during signup."

@app.route('/index')
def main():
  return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)


