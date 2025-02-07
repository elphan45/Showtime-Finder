# Error messages in English and German
ERROR_MESSAGES = {
    'no_movie_name': {
        'en': 'Please enter a movie name',
        'de': 'Bitte geben Sie einen Filmnamen ein'
    },
    'scraping_error': {
        'en': 'Error while scraping theater: {}',
        'de': 'Fehler beim Scrapen des Kinos: {}'
    },
    'no_showtimes': {
        'en': 'No showtimes found for "{}"',
        'de': 'Keine Vorstellungen gefunden für "{}"'
    },
    'database_error': {
        'en': 'Database connection error: {}',
        'de': 'Datenbankverbindungsfehler: {}'
    }
}

# Theater URLs
THEATER_URLS = {
    'cinemaxx_si': 'https://www.cinemaxx.de/stuttgart-si-centrum',
    'cinemaxx_liederhalle': 'https://www.cinemaxx.de/stuttgart',
    'capitol': 'https://capitol-kornwestheim.de/',
    'traumpalast': 'https://leonberg.traumpalast.de/'
}
