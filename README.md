# Professional Travel Itinerary Generator

A Flask application that uses Google's Gemini API to generate professional travel itineraries with fee calculations by category. The app allows users to download their itineraries as PDFs and keeps a history of generated itineraries.

- [*Demo Video*](https://youtu.be/8zmszxsehj4)
- [*Temporarily Hosted Demo Website*](https://travelplanner-dwsp.onrender.com/)
- [*PDF*](https://github.com/Louis-Li-dev/TravelPlanner/blob/main/solution_challenge_PDF.pdf)


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
## Demo

| Homepage | Result Page |
|----------|-------------|
| ![Homepage](https://github.com/user-attachments/assets/59bfed26-facd-4a18-81cf-c39cea96bfed) | ![Result Page](https://github.com/user-attachments/assets/7eaac88c-860a-4339-a91c-8bf746baab41) |
## Design
| Diagram Type          | Image |
|-----------------------|-------|
| **Architecture Diagram** | ![Architecture Diagram](https://github.com/user-attachments/assets/2c00d2bf-9eb8-4276-acf0-e9fb2596c5a9) |
| **Flow Diagram**         | ![Flow Diagram](https://github.com/user-attachments/assets/16d37362-1e64-42ad-ba1f-11b1c7fcc6f2) |
| **Wireframe**            | ![Wireframe](https://github.com/user-attachments/assets/5a989329-5da8-427d-8ffe-cf4db07efcc9) |



## Requirements

- Python 3.7+
- Flask
- Google API key for Gemini
- ReportLab (for PDF generation)
- SQLite (for database)
- PyTZ (for time zone calculations)

## Citation
Please kindly cite this repo in your modified, distributed, or released project using this.
