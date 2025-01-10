# 150240721
# Berkay Emre Keskin
# BLG317E

from flask import Blueprint, render_template, jsonify, session
from app.db import create_connection
from app.movies import get_movie_poster

user = Blueprint('user', __name__)

# ----------------------------- HELPER FUNCTIONS -----------------------------

def return_error(message, status_code = 400):
    return jsonify({'error': message}), status_code

def return_success(message, status_code = 200):
    return jsonify({'success': message}), status_code

def get_all_friends(user_id):
    connection = create_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM friendship WHERE userId = %s', (user_id,))
    friendships = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return friendships

def get_common_friends(user_id, friend_id):
    connection = create_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
        SELECT DISTINCT f1.friendId 
        FROM friendship f1
        INNER JOIN friendship f2 ON f1.friendId = f2.friendId
        WHERE f1.userId = %s AND f2.userId = %s
    ''', (user_id, friend_id))
    common_friends = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return [friend['friendId'] for friend in common_friends]

def get_friendship(user_id, friend_id):
    connection = create_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM friendship WHERE userId = %s AND friendId = %s', (user_id, friend_id))
    friendship = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if friendship is None:
        return None
    
    return friendship

# ----------------------------- ROUTES -----------------------------

@user.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    if session.get('logged_in') is None:
        return return_error('Unauthorized', 401)

    connection = create_connection()
    if connection is None:
        return return_error('Database connection error', 500)

    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE userId = %s', (id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        connection.close()
        return return_error('User not found', 404)

    movies_per_page = 6

    cursor.execute("SELECT * FROM watchlists WHERE userId = %s LIMIT %s", (id, movies_per_page))
    watchlists = cursor.fetchall()
    
    watchlists_movies = []
    for watchlist in watchlists:
        cursor.execute('''
            SELECT * FROM movies, links
            WHERE movies.movieId = links.movieId
            AND movies.movieId = %s
        ''', (watchlist['movieId'],))
        movie = cursor.fetchone()
        if movie is None:
            continue
        movie['poster_url'] = get_movie_poster(movie['tmdbId'])
        watchlists_movies.append(movie)
        
    cursor.execute('''
        SELECT * FROM reviews, ratings, movies, links
        WHERE movies.movieId = links.movieId
        AND reviews.movieId = ratings.movieId
        AND reviews.userId = ratings.userId 
        AND movies.movieId = reviews.movieId
        AND reviews.userId = %s LIMIT %s'''
    , (id, movies_per_page)) 
    reviews_and_ratings = cursor.fetchall()   

    for movie in reviews_and_ratings:
        movie['poster_url'] = get_movie_poster(movie['tmdbId'])

    user['watchlists'] = watchlists_movies
    user['reviews'] = reviews_and_ratings
    user['current_user'] = session['username']

    user_id = session.get('user_id')
    cursor.execute('SELECT * FROM friendship WHERE userId = %s AND friendId = %s', (user_id, id))
    friendship = cursor.fetchone()
    user['is_friend'] = friendship is not None
    
    friends = get_all_friends(user_id)
    user['friends'] = []
    for friend in friends:
        cursor.execute('SELECT * FROM users WHERE userId = %s', (friend['friendId'],))
        user['friends'].append(cursor.fetchone())
        
    common_friends = get_common_friends(user_id, id)
    user['common_friends'] = []
    for friend_id in common_friends:
        cursor.execute('SELECT * FROM users WHERE userId = %s', (friend_id,))
        friend = cursor.fetchone()
        user['common_friends'].append(friend)

    cursor.close()
    connection.close()
    return render_template('user/user.html', user=user)

@user.route('/users/<int:id>/add_friend', methods=['POST'])
def add_friend(id):
    if session.get('logged_in') is None:
        return return_error('Unauthorized', 401)

    """Adds a friend to the user with the given ID."""
    connection = create_connection()
    if connection is None:
        return return_error('Database connection error', 500)
    
    friendship = get_friendship(session['user_id'], id)
    if friendship is not None:
        return return_error('Friend already exists', 409)
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute('INSERT INTO friendship (userId, friendId) VALUES (%s, %s)', (session['user_id'], id))
    cursor.execute('INSERT INTO friendship (userId, friendId) VALUES (%s, %s)', (id, session['user_id']))   
    connection.commit()
    cursor.close()
    connection.close()
        
    return return_success('Friend added', 201)

@user.route('/users/<int:id>/remove_friend', methods=['POST'])
def remove_friend(id):
    if session.get('logged_in') is None:
        return return_error('Unauthorized', 401)

    """Removes a friend from the user with the given ID."""
    connection = create_connection()
    if connection is None:
        return return_error('Database connection error', 500)
    
    friendship = get_friendship(session['user_id'], id)
    if friendship is None:
        return return_error('Friend not found', 404)
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute('DELETE FROM friendship WHERE userId = %s AND friendId = %s', (session['user_id'], id))
    cursor.execute('DELETE FROM friendship WHERE userId = %s AND friendId = %s', (id, session['user_id']))
    connection.commit()
    cursor.close()
    connection.close()
    
    return return_success('Friend removed')
