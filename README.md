# Stuttgart Movie Showtimes Finder

A Python-based web application that aggregates movie showtimes from various theaters in Stuttgart, with a special focus on Indian movies. The application scrapes data from multiple theater websites and presents it in an easy-to-use interface.

## Features

- Search for movies across multiple Stuttgart theaters
- Real-time scraping of showtimes from theater websites
- Clean and simple web interface using Streamlit
- Database storage of movie and showtime information
- Special focus on Indian movies

## Supported Theaters

- CinemaxX SI-Centrum Stuttgart
- CinemaxX Stuttgart Liederhalle
- Capitol Lichtspiele Kornwestheim
- Traumpalast Leonberg
- Lokah Films Events

## Prerequisites

- Python 3.11+
- PostgreSQL database

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd stuttgart-movie-finder
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following variables:
```
DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database]
```

## Usage

1. Start the application:
```bash
streamlit run movie_scraper.py
```

2. Open your web browser and navigate to the provided URL (typically http://localhost:3000)

3. Enter a movie name and click "Search Showtimes"

## Project Structure

- `movie_scraper.py`: Main application file containing the web interface and scraping logic
- `models.py`: Database models for storing theater, movie, and showtime information
- `requirements.txt`: List of Python dependencies

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
