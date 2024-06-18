
# Football Data Flask Application

This Python Flask application retrieves football competition data, such as standings, upcoming matches, and completed scores, from the football-data.org API. Users can select different competitions and seasons to view relevant information.
All data cached by FLask-cache and stored in local MongoDB for best performance

## Features

- **List Competitions:** Select between various popular football leagues.
- **View Standings:** Shows current standings for the selected competition.
- **Upcoming Matches:** Displays the schedule of upcoming matches.
- **Completed Matches:** Provides scores of completed matches (delayed scores).
- **Season Selection:** Choose the desired season/year for viewing data.

## Prerequisites

1. **Python 3.7+** (make sure Python is installed)
2. **Football-Data API Key:** Obtain an API key by registering at [football-data.org](https://www.football-data.org/client/register).

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone <your-repository-url>
   ```

2. Navigate to the project's directory:
   ```bash
   cd <your-project-folder>
   ```

3. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Install mongoDB and create a Database

## Usage

1. Run mongoDB at port 27017

2. Run the Flask application:
   ```bash
   python main.py
   ```

3. Open the browser to http://localhost:8000.

4. Select the desired competition and season, and explore standings, upcoming matches, and scores.

## Files and Structure

- **`main.py`:** Main application file containing the Flask routes and logic.
- **`api.py`:** Api interface.
- **`templates/index.html`:** HTML template used for rendering the main page.
- **`requirements.txt`:** Python dependencies required to run the project.

## Dependencies

- **Flask:** Python web framework
- **Requests:** For handling API requests
- **MongoDB** For long-term caching

## Contributing

Feel free to open issues or submit pull requests if you'd like to add features, fix bugs, or improve the documentation.

## License

[MIT License](LICENSE)
