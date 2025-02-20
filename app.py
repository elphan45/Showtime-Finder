# app.py
from flask import Flask, render_template, request
import src.movie_scraper as movie_scraper

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        movie = request.form.get('movie')
        if movie:
            # Call the smart search function from movie_scraper
            results = movie_scraper.scrape_movie_info(movie)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    # keep the web interface always active
    app.run(debug=True, host='0.0.0.0')
