from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file, flash
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, re
from datetime import datetime
import pytz
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
import tempfile
import uuid

# Load environment
load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")  # Using the environment variable from Vercel
if not api_key:
    raise EnvironmentError("Please set the GOOGLE_API_KEY environment variable.")

# Initialize GenAI client
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash"
google_search_tool = Tool(google_search=GoogleSearch())

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    itineraries = db.relationship('Itinerary', backref='user', lazy=True, cascade="all, delete-orphan")

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    home_country = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    budget = db.Column(db.String(50), nullable=False)
    interests = db.Column(db.Text)
    itinerary_data = db.Column(db.Text, nullable=False)
    party_size = db.Column(db.Integer, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Time zone dictionary for major countries
TIMEZONE_MAP = {
    "United States": "America/New_York",
    "United Kingdom": "Europe/London",
    "Canada": "America/Toronto",
    "Australia": "Australia/Sydney",
    "Japan": "Asia/Tokyo",
    "China": "Asia/Shanghai",
    "India": "Asia/Kolkata",
    "Germany": "Europe/Berlin",
    "France": "Europe/Paris",
    "Brazil": "America/Sao_Paulo",
    "South Africa": "Africa/Johannesburg",
    "Mexico": "America/Mexico_City",
    "Spain": "Europe/Madrid",
    "Italy": "Europe/Rome",
    "Russia": "Europe/Moscow",
    "South Korea": "Asia/Seoul",
    "Singapore": "Asia/Singapore",
    "Netherlands": "Europe/Amsterdam",
    "Sweden": "Europe/Stockholm",
    "Switzerland": "Europe/Zurich",
    "Taiwan": "Asia/Taipei"  # Adding Taiwan
}

COUNTRIES = sorted(list(TIMEZONE_MAP.keys()) + [
    "Argentina", "Austria", "Belgium", "Chile", "Colombia", 
    "Denmark", "Egypt", "Finland", "Greece", "Hong Kong", 
    "Indonesia", "Ireland", "Israel", "Malaysia", "New Zealand", 
    "Norway", "Philippines", "Poland", "Portugal", "Saudi Arabia", 
    "Thailand", "Turkey", "UAE", "Vietnam", "Taiwan"  # Adding Taiwan
])



def get_time_difference(home_country, destination_country):
    """Calculate time difference between home and destination"""
    try:
        home_tz = pytz.timezone(TIMEZONE_MAP.get(home_country, "UTC"))
        dest_tz = pytz.timezone(TIMEZONE_MAP.get(destination_country, "UTC"))
        
        now = datetime.now()
        home_time = pytz.utc.localize(now).astimezone(home_tz)
        dest_time = pytz.utc.localize(now).astimezone(dest_tz)
        
        diff_hours = (dest_time.utcoffset() - home_time.utcoffset()).total_seconds() / 3600
        
        if diff_hours == 0:
            return "Same time zone"
        elif diff_hours > 0:
            return f"{int(diff_hours)} hours ahead"
        else:
            return f"{abs(int(diff_hours))} hours behind"
    except:
        return "Time zone information not available"

def generate_itinerary(home_country, destination, duration, budget, interests, party_size):
    """Generate a travel itinerary using Google's Gemini API"""
    
    # Create a prompt for the AI
    prompt = f"""
    Create a detailed travel itinerary for a trip from {home_country} to {destination} for {duration} days with a budget of {budget}.
    The traveler is interested in: {interests}.
    The party is of {party_size} people.
    Format the response as a JSON object with the following structure:
    {{
        "flight_info": {{
            "estimated_flight_duration": "X hours",
            "recommended_airlines": ["Airline 1", "Airline 2"],
            "flight_link": ["Link to Airline 1", "Link to Airline 2"],
            "estimated_flight_cost": 0
        }},
        "daily_plans": [
            {{
                "day": 1,
                "date": "Day of the week",
                "activities": [
                    {{
                        "time": "Morning",
                        "description": "Activity description",
                        "location": "Location name",
                        "category": "Activity/Food/Transportation/Accommodation",
                        "estimated_cost": 0
                    }},
                    // More activities for the day
                ]
            }},
            // More days
        ],
        "budget_breakdown": {{
            "Flights": 0,
            "Accommodation": 0,
            "Food": 0,
            "Transportation": 0,
            "Activities": 0,
            "Miscellaneous": 0,
            "Total": 0
        }},
        "travel_tips": [
            "Tip 1",
            "Tip 2"
        ],
        "visa_requirements": "Brief description of visa requirements",
        "local_customs": "Brief description of important local customs"
    }}
    
    Ensure the budget breakdown is realistic and the total matches the sum of all categories.
    Make sure all costs are within the total budget of {budget}.
    Only respond with the JSON object, no additional text.
    The currency is USD
    """
    print("PROMPT")
    try:
        # Initialize the Gemini model with Google Search tool
        client = genai.Client(api_key=api_key)
        MODEL_ID = "gemini-2.0-flash"
        google_search_tool = Tool(google_search=GoogleSearch())

        
        # Generate content with search capability
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt],
            config=GenerateContentConfig(tools=[google_search_tool], response_modalities=["TEXT"])
        )
        
        # Extract and parse the JSON response
        response_text = response.text
        
        # Clean up the response if it contains markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
                   # Parse the JSON
        itinerary_data = json.loads(response_text)

        # Combine airlines and flight links into a list of tuples
        flight_info = itinerary_data.get("flight_info", {})
        recommended_airlines = flight_info.get("recommended_airlines", [])
        flight_links = flight_info.get("flight_link", [])

        # Combine airlines with their corresponding links
        airlines_with_links = list(zip(recommended_airlines, flight_links))

        # Add the combined list to the itinerary_data
        itinerary_data["flight_info"]["airlines_with_links"] = airlines_with_links
 
        
        
        return itinerary_data
    
    except Exception as e:
        print(f"Error generating itinerary: {e}")
        raise Exception(f"Failed to generate itinerary: {str(e)}")

def create_pdf(itinerary_data, home_country, destination, duration, budget, interests, time_difference, party_size):
    """Create a PDF file from the itinerary data with proper text wrapping"""
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()
    
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles with text wrapping
    title_style = styles['Heading1']
    heading2_style = styles['Heading2']
    heading3_style = styles['Heading3']
    
    # Enhanced text wrapping style
    wrapped_style = ParagraphStyle(
        'WrappedStyle',
        parent=styles['Normal'],
        spaceBefore=6,
        spaceAfter=6,
        wordWrap='CJK',  # Improved word wrapping
        allowWidows=0,
        allowOrphans=0
    )
    
    # Create the content
    content = []
    
    # Title and logo (placeholder)
    content.append(Paragraph(f"Travel Itinerary: {home_country} to {destination}", title_style))
    content.append(Spacer(1, 0.25*inch))
    
    # Trip details
    content.append(Paragraph("Trip Details", heading2_style))
    
    trip_details = [
        ["Duration", f"{duration} days"],
        ["Budget", budget],
        ["Time Difference", time_difference],
        ["Interests", interests],
        ["Party Size", party_size]
    ]
    
    trip_table = Table(trip_details, colWidths=[1.5*inch, 5*inch])
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(trip_table)
    content.append(Spacer(1, 0.25*inch))
    
    # Flight information
    if "flight_info" in itinerary_data:
        content.append(Paragraph("Flight Information", heading2_style))
        
        flight_details = [
            ["Estimated Duration", itinerary_data["flight_info"].get("estimated_flight_duration", "N/A")],
            ["Recommended\nAirlines", ", ".join(itinerary_data["flight_info"].get("recommended_airlines", ["N/A"]))],
            ["Estimated Cost", f"${itinerary_data['flight_info'].get('estimated_flight_cost', 'N/A')}"]
        ]
        
        flight_table = Table(flight_details, colWidths=[1.5*inch, 5*inch])
        flight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        content.append(flight_table)
        content.append(Spacer(1, 0.25*inch))
    
    # Visa and customs information
    content.append(Paragraph("Travel Requirements", heading2_style))
    
    # Ensure text wrapping for visa requirements
    visa_info = Paragraph(f"<b>Visa Requirements:</b> {itinerary_data.get('visa_requirements', 'Information not available')}", wrapped_style)
    content.append(visa_info)
    content.append(Spacer(1, 0.1*inch))
    
    # Ensure text wrapping for local customs
    customs_info = Paragraph(f"<b>Local Customs:</b> {itinerary_data.get('local_customs', 'Information not available')}", wrapped_style)
    content.append(customs_info)
    content.append(Spacer(1, 0.25*inch))
    
    # Daily plans
    content.append(Paragraph("Daily Itinerary", heading2_style))
    content.append(Spacer(1, 0.1*inch))
    
    for day in itinerary_data['daily_plans']:
        content.append(Paragraph(f"Day {day['day']} - {day.get('date', '')}", heading3_style))
        
        # Create a table for activities
        data = [["Time", "Activity", "Location", "Category", "Cost"]]
        
        for activity in day['activities']:
            # Ensure text wrapping for description
            description = Paragraph(activity['description'], wrapped_style)
            location = Paragraph(activity.get('location', 'N/A'), wrapped_style)
            data.append([
                activity['time'],
                description,
                location,
                activity['category'],
                f"${activity['estimated_cost']}"
            ])
        
        # Create the table with appropriate column widths
        table = Table(data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1*inch, 0.8*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Allow text wrapping in the description column
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.2*inch))
    
    # Budget breakdown
    content.append(Paragraph("Budget Breakdown", heading2_style))
    content.append(Spacer(1, 0.1*inch))
    
    budget_data = [["Category", "Amount"]]
    for category, amount in itinerary_data['budget_breakdown'].items():
        budget_data.append([category, f"${amount}"])
    
    budget_table = Table(budget_data, colWidths=[3*inch, 1.5*inch])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Highlight the total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    content.append(budget_table)
    content.append(Spacer(1, 0.2*inch))
    
    # Travel tips
    content.append(Paragraph("Travel Tips", heading2_style))
    content.append(Spacer(1, 0.1*inch))
    
    for tip in itinerary_data['travel_tips']:
        # Ensure text wrapping for tips
        content.append(Paragraph(f"• {tip}", wrapped_style))
    
    # Build the PDF
    doc.build(content)
    
    return pdf_path

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', countries=COUNTRIES)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
            
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
            
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        # Check credentials
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
            
        # Set session
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', countries=COUNTRIES)

@app.route('/generate', methods=['POST'])
def generate():
    # Check if user is logged in
    user_id = session.get('user_id')
    
    # Get form data
    home_country = request.form.get('home_country')
    destination = request.form.get('destination')
    duration = request.form.get('duration')
    budget = request.form.get('budget')
    interests = request.form.get('interests')
    style = request.form.get('style')  # For PDF style
    currency = request.form.get('currency')  # For selected currency
    party_size = int(request.form.get('party_size', 1))  # Default to 1 if not provided
    total_budget = float(budget)

    # Calculate time difference
    time_difference = get_time_difference(home_country, destination)
    
    # Generate itinerary using AI
    try:
        itinerary_data = generate_itinerary(
            home_country, 
            destination, 
            duration, 
            budget,
            interests,
            party_size
        )
        
        # Save to database if user is logged in
        if user_id:
            new_itinerary = Itinerary(
                user_id=user_id,
                home_country=home_country,
                destination=destination,
                duration=duration,
                budget=budget,
                interests=interests,
                itinerary_data=json.dumps(itinerary_data),
                party_size=party_size
            )
            db.session.add(new_itinerary)
            db.session.commit()
            itinerary_id = new_itinerary.id
        else:
            # For non-logged in users, create a temporary ID
            itinerary_id = str(uuid.uuid4())
            # Store in session for temporary access
            session['temp_itinerary'] = {
                'id': itinerary_id,
                'home_country': home_country,
                'destination': destination,
                'duration': duration,
                'style': style,
                'currency': currency,
                'total_budget': total_budget,
                'budget': budget,
                'interests': interests,
                'party_size': party_size,
                'itinerary_data': json.dumps(itinerary_data),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return render_template('result.html', 
                              itinerary=itinerary_data, 
                              home_country=home_country,
                              destination=destination,
                              duration=duration,
                              budget=budget,
                              interests=interests,
                              time_difference=time_difference,
                              itinerary_id=itinerary_id,
                              party_size=party_size)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/history')
@login_required
def history():
    user_id = session.get('user_id')
    itineraries = Itinerary.query.filter_by(user_id=user_id).order_by(Itinerary.created_at.desc()).all()
    return render_template('history.html', history=itineraries)

@app.route('/delete/<int:itinerary_id>', methods=['POST'])
@login_required
def delete_itinerary(itinerary_id):
    user_id = session.get('user_id')
    itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user_id).first_or_404()
    
    db.session.delete(itinerary)
    db.session.commit()
    
    flash('Itinerary deleted successfully', 'success')
    return redirect(url_for('history'))

@app.route('/download/<itinerary_id>')
def download_pdf(itinerary_id):
    # Check if user is logged in
    user_id = session.get('user_id')
    
    # Get itinerary data
    if user_id:
        # For logged in users, get from database
        itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user_id).first()
        if not itinerary:
            flash('Itinerary not found', 'danger')
            return redirect(url_for('history'))
            
        itinerary_data = json.loads(itinerary.itinerary_data)
        home_country = itinerary.home_country
        party_size = itinerary.party_size
        destination = itinerary.destination
        duration = itinerary.duration
        budget = itinerary.budget
        interests = itinerary.interests
    else:
        # For non-logged in users, get from session
        temp_itinerary = session.get('temp_itinerary')
        if not temp_itinerary or temp_itinerary['id'] != itinerary_id:
            flash('Itinerary not found', 'danger')
            return redirect(url_for('index'))
            
        itinerary_data = json.loads(temp_itinerary['itinerary_data'])
        home_country = temp_itinerary['home_country']
        party_size = temp_itinerary['party_size']
        destination = temp_itinerary['destination']
        duration = temp_itinerary['duration']
        budget = temp_itinerary['budget']
        interests = temp_itinerary['interests']
    
    # Calculate time difference
    time_difference = get_time_difference(home_country, destination)
    
    # Generate PDF
    pdf_path = create_pdf(
        itinerary_data, 
        home_country, 
        destination, 
        duration, 
        budget, 
        interests,
        time_difference,
        party_size
    )
    
    # Send file to user
    return send_file(pdf_path, as_attachment=True, download_name=f"itinerary_{destination}_{datetime.now().strftime('%Y%m%d')}.pdf")

if __name__ == '__main__':
    app.run(debug=True)
