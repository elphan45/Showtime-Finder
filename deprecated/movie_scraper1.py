import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import trafilatura

class TheaterScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_cinemaxx(self, movie_name):
        """Scrape showtimes from CinemaxX theaters"""
        showtimes = []
        try:
            # CinemaxX SI-Centrum Stuttgart and Liederhalle
            cinemaxx_urls = [
                'https://www.cinemaxx.de/stuttgart-si-centrum',
                'https://www.cinemaxx.de/stuttgart'
            ]

            for url in cinemaxx_urls:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    shows = soup.find_all('div', class_='movie-title')
                    for show in shows:
                        if movie_name.lower() in show.text.lower():
                            times = show.find_next('div', class_='showtime')
                            if times:
                                showtimes.append({
                                    'theater': 'CinemaxX ' + url.split('/')[-1],
                                    'times': times.text.strip()
                                })
        except Exception as e:
            st.error(f"Error scraping CinemaxX: {str(e)}")
        return showtimes

    def scrape_capitol(self, movie_name):
        """Scrape showtimes from Capitol Lichtspiele Kornwestheim"""
        showtimes = []
        try:
            url = 'https://capitol-kornwestheim.de/'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                # Using trafilatura for better content extraction
                text = trafilatura.extract(response.text)
                if text and movie_name.lower() in text.lower():
                    # Basic extraction - will need refinement based on actual website structure
                    showtimes.append({
                        'theater': 'Capitol Lichtspiele Kornwestheim',
                        'times': 'Please check website for exact times'
                    })
        except Exception as e:
            st.error(f"Error scraping Capitol: {str(e)}")
        return showtimes

    def scrape_traumpalast(self, movie_name):
        """Scrape showtimes from Traumpalast Leonberg"""
        showtimes = []
        try:
            urls = [
                'https://leonberg.traumpalast.de/index.php/PID/5796.html',
                'https://leonberg.traumpalast.de/index.php/PID/5842.html'
            ]
            for url in urls:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    # Using trafilatura for better content extraction
                    text = trafilatura.extract(response.text)
                    if text and movie_name.lower() in text.lower():
                        showtimes.append({
                            'theater': 'Traumpalast Leonberg',
                            'times': 'Please check website for exact times'
                        })
        except Exception as e:
            st.error(f"Error scraping Traumpalast: {str(e)}")
        return showtimes

    def scrape_lokahfilms(self, movie_name):
        """Scrape information from Lokah Films"""
        showtimes = []
        try:
            url = 'https://www.lokahfilms.com/events/'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                text = trafilatura.extract(response.text)
                if text and movie_name.lower() in text.lower():
                    showtimes.append({
                        'theater': 'Lokah Films Events',
                        'info': 'Found matching event - please check website for details'
                    })
        except Exception as e:
            st.error(f"Error scraping Lokah Films: {str(e)}")
        return showtimes

def main():
    st.title("Stuttgart Movie Showtimes Finder")
    st.write("Search for movie showtimes in Stuttgart theaters (specialized in Indian movies)")

    movie_name = st.text_input("Enter movie name:", "")

    if st.button("Search Showtimes"):
        if movie_name:
            scraper = TheaterScraper()

            with st.spinner('Searching for showtimes...'):
                # Collect results from all theaters
                all_showtimes = []
                all_showtimes.extend(scraper.scrape_cinemaxx(movie_name))
                all_showtimes.extend(scraper.scrape_capitol(movie_name))
                all_showtimes.extend(scraper.scrape_traumpalast(movie_name))
                all_showtimes.extend(scraper.scrape_lokahfilms(movie_name))

                if all_showtimes:
                    st.success("Found showtimes!")
                    for showtime in all_showtimes:
                        st.subheader(showtime['theater'])
                        if 'times' in showtime:
                            st.write(f"Showtimes: {showtime['times']}")
                        if 'info' in showtime:
                            st.write(showtime['info'])
                else:
                    st.warning(f"No showtimes found for '{movie_name}'. Try another movie name or check back later.")

                st.markdown("---")
                st.markdown("Note: For the most accurate and up-to-date information, please visit the theater websites directly:")
                st.markdown("- [CinemaxX](https://www.cinemaxx.de/)")
                st.markdown("- [Capitol Lichtspiele Kornwestheim](https://capitol-kornwestheim.de/)")
                st.markdown("- [Traumpalast Leonberg](https://leonberg.traumpalast.de/)")
                st.markdown("- [Lokah Films](https://www.lokahfilms.com/events/)")

if __name__ == "__main__":
    main()