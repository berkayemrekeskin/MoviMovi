# 150240721
# Berkay Emre Keskin
# BLG317E

from flask import Blueprint, render_template, request, session ,jsonify, url_for
from PIL import Image
from app.db import create_connection
import requests
import os

movies_bp = Blueprint('movies_bp', __name__)

# ----------------------------- API KEY AND REQUEST LINK -----------------------------

API_KEY = os.environ.get('TMDB_API_KEY')
REQUEST_LINK = 'https://api.themoviedb.org/3/movie/{tmbd_id}?api_key={API_KEY}&append_to_response=images'

# ----------------------------- HELPER FUNCTIONS -----------------------------

def download_movie_poster(movie_id, save_dir='posters'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    url = REQUEST_LINK.format(tmbd_id=movie_id, API_KEY=API_KEY)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    poster_path = data['poster_path']
    poster_url = f'https://image.tmdb.org/t/p/original{poster_path}'
    poster_data = requests.get(poster_url)
    poster_data.raise_for_status()
    poster_file_path = os.path.join(save_dir, f'{movie_id}.jpg')
    with open(poster_file_path, 'wb') as f:
        f.write(poster_data.content)
    print(f'Downloaded poster for movie ID {movie_id} to {poster_file_path}')

def download_posters():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT tmdbId FROM links")
        tmdb_ids = cursor.fetchall()
        for tmdb_id in tmdb_ids:
            download_movie_poster(tmdb_id[0])
        cursor.close()
    else:
        print("Error connecting to the database")
        
def resize_images(input_folder, output_folder, max_width=500, max_height=500, quality=85):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            with Image.open(image_path) as img:
                img.thumbnail((max_width, max_height))
                img.save(output_path, optimize=True, quality=quality)
                print(f"Resized and saved: {output_path}")


def return_error(message, status_code = 400):
    return jsonify({'error': message}), status_code

def return_success(message, status_code = 200):
    return jsonify({'success': message}), status_code

def get_movie_poster(tmdb_id):
    poster_path = os.path.join('app', 'static', 'posters', f'{tmdb_id}.jpg')
    if os.path.exists(poster_path):
        print(f'Poster for movie ID {tmdb_id} found')
        return url_for('static', filename=f'posters/{tmdb_id}.jpg')
    else:
        print(f'Poster for movie ID {tmdb_id} not found')
    return None

# ----------------------------- ROUTES -----------------------------
@movies_bp.route('/')
def get_movies():
    
    
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as total FROM movies")
        total_movies = cursor.fetchone()['total']

        page = request.args.get('page', 1, type=int)

        movies_per_page = 12
        offset = (page - 1) * movies_per_page
        
        cursor.execute('''
            SELECT *
            FROM movies
            INNER JOIN links ON movies.movieId = links.movieId
            LIMIT %s OFFSET %s
        ''', (movies_per_page, offset))
        movies = cursor.fetchall()
        
        cursor.execute('''
            SELECT ratings.movieId, AVG(ratings.rating) as rating
            FROM ratings, movies
            WHERE ratings.movieId = movies.movieId
            GROUP BY ratings.movieId
        ''')
        ratings = cursor.fetchall()

        
        for movie in movies:
            movie['poster_url'] = get_movie_poster(movie['tmdbId'])
            for rating in ratings:
                if movie['movieId'] == rating['movieId']:
                    movie['rating'] = round(rating['rating'], 1)


        total_pages = (total_movies + movies_per_page - 1) // movies_per_page

        return render_template('movies/movies.html', movies=movies, page=page, total_pages=total_pages, user_id = session['user_id'], page_type='all')
    
    else:
        return return_error("Error connecting to the database", 500)
    
@movies_bp.route('/<int:movie_id>')
def get_movie(movie_id):
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM movies WHERE movieId = %s", (movie_id,))
        movie = cursor.fetchone()
        cursor.execute("SELECT * FROM ratings WHERE movieId = %s", (movie_id,))
        ratings = cursor.fetchall()
        cursor.execute("SELECT * FROM links WHERE movieId = %s", (movie_id,))
        link = cursor.fetchone()
        cursor.execute("SELECT * FROM reviews WHERE movieId = %s", (movie_id,))
        reviews = cursor.fetchall()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.execute("SELECT * FROM watchlists WHERE movieId = %s AND userId = %s", (movie_id,session['user_id']))
        if cursor.fetchone():
            movie['in_watchlist'] = True
        else:
            movie['in_watchlist'] = False
        cursor.execute("SELECT * FROM ratings WHERE movieId = %s AND userId = %s", (movie_id,session['user_id']))
        if cursor.fetchone():
            movie['rated'] = True
        else:
            movie['rated'] = False
            
        cursor.close()
        
        movie['review_text'] = []
        for review in reviews:
            movie['review_text'].append(review['review_text'])
        movie['poster_url'] = get_movie_poster(link['tmdbId'])
        movie['imdbId'] = link['imdbId']
        movie['tmdbId'] = link['tmdbId']
        movie['movieId'] = movie_id
        
        total_rating = 0
        for rating in ratings:
            total_rating += rating['rating']
        if len(ratings) != 0:
            movie['rating'] = int(total_rating / len(ratings)) + 1
        else:
            movie['rating'] = 0
            
        return render_template('movies/movie.html', movie=movie, ratings=ratings, link=link, reviews=reviews, users=users, user_id = session['user_id'], user_name=session['username'])
    
@movies_bp.route('/add_to_watchlist/<int:movie_id>', methods=['POST'])
def add_to_watchlist(movie_id):
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    user_id = session.get('user_id')
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM watchlists WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        if cursor.fetchone():
            return return_error("Movie already in watchlist", 400)
        
        cursor.execute("INSERT INTO watchlists (userId, movieId) VALUES (%s, %s)", (user_id, movie_id))
        connection.commit()
        cursor.close()
        return return_success("Movie added to watchlist", 200)
    else:
        return return_error("Error connecting to the database", 500)

@movies_bp.route('/remove_from_watchlist/<int:movie_id>', methods=['POST'])
def remove_from_watchlist(movie_id):
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    user_id = session.get('user_id')
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM watchlists WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        if not cursor.fetchone():
            return return_error("Movie not in watchlist", 400)
        cursor.execute("DELETE FROM watchlists WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        connection.commit()
        cursor.close()
        return return_success("Movie removed from watchlist", 200)
    else:
        return return_error("Error connecting to the database", 500)
    

@movies_bp.route('/add_review/<int:movie_id>', methods=['POST'])
def add_review(movie_id):
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    user_id = session.get('user_id')
    review_text = request.form.get('review')
    rating = request.form.get('rating')
    
    print(rating)
    print(review_text)
    
    if not rating or not rating.isdigit():
        return return_error("Rating is required", 400)
    rating = int(rating)
    if not review_text:
        return return_error("Review is required", 400)
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM reviews WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        if cursor.fetchone():
            return return_error("You have already reviewed this movie", 400)
        
        cursor.execute("SELECT * FROM ratings WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        if cursor.fetchone():
            return return_error("You have already rated this movie", 400)
        
        cursor.execute("INSERT INTO reviews (userId, movieId, review_text) VALUES (%s, %s, %s)", (user_id, movie_id, review_text))
        cursor.execute("""
            INSERT INTO ratings (userId, movieId, rating)
            SELECT %s, %s, %s
            WHERE %s BETWEEN 0 AND 5
        """, (user_id, movie_id, rating, rating))
        if cursor.rowcount == 0:
            return return_error("Rating must be between 0 and 5", 400)
        connection.commit()
        cursor.close()
        return return_success("Review added successfully", 200)
    else:
        return return_error("Error connecting to the database", 500)
    
@movies_bp.route('/delete_review/<int:movie_id>', methods=['POST'])
def delete_review(movie_id):
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    user_id = session.get('user_id')
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM reviews WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        if not cursor.fetchone():
            return return_error("You have not reviewed this movie", 400)
        
        cursor.execute("DELETE FROM reviews WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        cursor.execute("DELETE FROM ratings WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        connection.commit()
        cursor.close()
        return return_success("Review deleted successfully", 200)
    else:
        return return_error("Error connecting to the database", 500)
    
@movies_bp.route('/check_in_watchlist/<int:movie_id>', methods=['GET'])
def check_in_watchlist(movie_id):
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    user_id = session.get('user_id')
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM watchlists WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        if cursor.fetchone():
            return "True", 200
        else:
            return "False", 200 
        
@movies_bp.route('/search', methods=['GET'])
def search():
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)

    query = request.args.get('query', '').strip()
    search_type = request.args.get('type', '').strip()

    if not query or not search_type:
        return return_error("Missing search parameters", 400)

    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)

        if len(query) < 3:
            return return_error("Query must be at least 3 characters long", 400)
            
        page = request.args.get('page', 1, type=int)
        movies_per_page = 12
        offset = (page - 1) * movies_per_page
            
        if search_type == 'title':
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM movies
                WHERE title LIKE %s
            """, (f"{query}%",))
            total_movies = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT movies.*, links.*
                FROM movies
                LEFT JOIN links ON movies.movieId = links.movieId
                WHERE movies.title LIKE %s
                LIMIT %s OFFSET %s
            """, (f"{query}%", movies_per_page, offset))
            result = cursor.fetchall()
            
            total_pages = (total_movies + movies_per_page - 1) // movies_per_page

            for movie in result:
                movie['poster_url'] = get_movie_poster(movie['tmdbId'])

            cursor.close()
            return render_template('movies/movies.html', movies=result, page=page, total_pages=total_pages, user_id=session['user_id'], page_type='search')

        elif search_type == 'genre':
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM movies
                WHERE genres LIKE %s
            """, (f"%{query}%",))
            total_movies = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT movies.*, links.*
                FROM movies
                LEFT JOIN links ON movies.movieId = links.movieId
                WHERE genres LIKE %s
                LIMIT %s OFFSET %s
            """, (f"%{query}%", movies_per_page, offset))
            result = cursor.fetchall()
    
            total_pages = (total_movies + movies_per_page - 1) // movies_per_page

            for movie in result:
                movie['poster_url'] = get_movie_poster(movie['tmdbId'])

            cursor.close()
            return render_template('movies/movies.html', movies=result, page=page, total_pages=total_pages, user_id=session['user_id'], page_type='search')

        else:
            return return_error("Invalid search type", 400)

    else:
        return return_error("Database connection failed", 500)


@movies_bp.route('/update_review/<int:movie_id>', methods=['POST']) 
def update_review(movie_id):
    if not session.get('logged_in'):
        return return_error("Unauthorized", 401)
    
    user_id = session.get('user_id')
    review_text = request.form.get('review')
    rating = request.form.get('rating')
    
    if not rating or not rating.isdigit():
        return return_error("Rating is required", 400)
    rating = int(rating)
    if not review_text:
        return return_error("Review is required", 400)
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM reviews WHERE userId = %s AND movieId = %s", (user_id, movie_id))
        if not cursor.fetchone():
            return return_error("You have not reviewed this movie", 400)
        
        cursor.execute("UPDATE reviews SET review_text = %s WHERE userId = %s AND movieId = %s", (review_text, user_id, movie_id))
        cursor.execute("UPDATE ratings SET rating = %s WHERE userId = %s AND movieId = %s", (rating, user_id, movie_id))
        connection.commit()
        cursor.close()
        return return_success("Review updated successfully", 200)
    else:
        return return_error("Error connecting to the database", 500)
    
