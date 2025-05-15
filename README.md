# Professional Travel Itinerary Generator

A Flask application that uses Google's Gemini API to generate professional travel itineraries with fee calculations by category. The app allows users to download their itineraries as PDFs and keeps a history of generated itineraries.

## Features

- Generate travel itineraries using Google's Gemini API with Google Search capabilities
- Calculate fees by category (flights, accommodation, food, transportation, activities)
- Professional airline-like itinerary format
- Time zone difference calculations between home country and destination
- Flight information and recommendations
- Visa requirements and local customs information
- Download itineraries as PDF with proper text wrapping
- Store user history in SQLite database

## Installation

1. Clone this repository
2. Install the required packages:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
3. Create a file named `.env` under the root directory and put your Goolge AI Studio API key in it as described in `.env.example`. 

## Usage

1. Run the Flask application:
   \`\`\`
   python app.py
   \`\`\`
2. Open your browser and navigate to `http://127.0.0.1:5000/`
3. Fill out the form with your travel preferences, including your home country
4. View your generated itinerary with time zone information and flight details
5. Download the itinerary as a PDF
6. Access your history of generated itineraries


## Requirements

- Python 3.7+
- Flask
- Google API key for Gemini
- ReportLab (for PDF generation)
- SQLite (for database)
- PyTZ (for time zone calculations)
