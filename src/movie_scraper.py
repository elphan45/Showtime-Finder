# Language: Python
# filepath: /home/student4/repositories/Private_Repo/Showtime-Finder/movie_scraper.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import trafilatura
import time

# Base URLs for theaters
base_urls = {
    'cinemaxx': [
        'https://www.cinemaxx.de/stuttgart-si-centrum',
        'https://www.cinemaxx.de/stuttgart'
    ],
    'capitol': 'https://capitol-kornwestheim.de',
    'traumpalast': [
        'https://leonberg.traumpalast.de/index.php/PID/5796',
        'https://leonberg.traumpalast.de/index.php/PID/5842'
    ],
    'lokahfilms': 'https://www.lokahfilms.com/events'
}

# Pagination parameters for each theater
pagination_params = {
    'cinemaxx': '?page={}',
    'capitol': '/programm?page={}',
    'traumpalast': '.html?page={}',
    'lokahfilms': '?page={}'
}


class TheaterScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Set base URLs and pagination parameters
        self.base_urls = base_urls
        self.pagination_params = pagination_params

    def paginated_scrape(self, url, page_param, movie_name, max_pages=5):
        all_results = []
        page = 1
        while page <= max_pages:
            full_url = f"{url}{page_param.format(page)}"
            response = requests.get(full_url, headers=self.headers)
            if response.status_code != 200:
                break
            soup = BeautifulSoup(response.text, 'html.parser')
            movies = soup.find_all('div', class_='movie-title')
            if not movies:
                break
            for movie in movies:
                if movie_name.lower() in movie.text.lower():
                    all_results.append({
                        'theater': url,
                        'times': 'Check website for times',
                        'link': full_url
                    })
            next_page = soup.find('a', class_='next')
            if not next_page:
                break
            page += 1
            time.sleep(1)  # Be nice to servers
        return all_results

    def scrape_all_theaters(self, movie_name):
        all_showtimes = []
        # Scrape CinemaxX
        for url in self.base_urls['cinemaxx']:
            results = self.paginated_scrape(url, self.pagination_params['cinemaxx'], movie_name)
            all_showtimes.extend(results)
        # Scrape Capitol
        results = self.paginated_scrape(self.base_urls['capitol'],
                                        self.pagination_params['capitol'],
                                        movie_name)
        all_showtimes.extend(results)
        # Scrape Traumpalast
        for url in self.base_urls['traumpalast']:
            results = self.paginated_scrape(url,
                                        self.pagination_params['traumpalast'],
                                        movie_name)
            all_showtimes.extend(results)
        # Scrape Lokah Films
        results = self.paginated_scrape(self.base_urls['lokahfilms'],
                                        self.pagination_params['lokahfilms'],
                                        movie_name)
        all_showtimes.extend(results)
        return all_showtimes


def main():
    st.title("Stuttgart Movie Showtimes Finder")
    st.write("Search for movie showtimes in Stuttgart theaters (specialized in Indian movies)")

    movie_name = st.text_input("Enter movie name:", "")

    if st.button("Search Showtimes"):
        if movie_name:
            scraper = TheaterScraper()
            with st.spinner('Searching for showtimes...'):
                all_showtimes = scraper.scrape_all_theaters(movie_name)

                if all_showtimes:
                    st.success("Found showtimes!")
                    for show in all_showtimes:
                        st.subheader(show['theater'])
                        st.write(f"Showtimes: {show.get('times', 'Check website for times')}")
                        st.markdown(f"[More Info]({show['link']})")
                else:
                    st.warning(f"No showtimes found for '{movie_name}'. Try another movie name or check back later.")


if __name__ == "__main__":
    main()