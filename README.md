# MoviMovi

MoviMovi is a movie recommendation and review website where users can search for movies or genres, add movies to their watchlist, provide reviews and ratings, and connect with friends to see their watchlists and reviews. This project was developed using Flask for the backend and HTML, CSS, and JavaScript for the frontend.

## Features

### User Authentication
- **Register**: Users can create an account with a username, email, and password.
- **Login**: Secure login functionality with session management.
- **Logout**: Ends the user session securely.
- **Session Management**: Tracks logged-in users and updates session variables.

### Movie Management
- **Search Movies**: Search movies by title or genre.
- **Add to Watchlist**: Save movies to a personal watchlist.
- **Remove from Watchlist**: Remove movies from the watchlist.
- **Add Reviews and Ratings**: Share opinions and rate movies on a scale of 0 to 5.
- **Edit and Delete Reviews**: Update or delete existing reviews and ratings.
- **View All Movies**: Paginated display of all available movies with posters and average ratings.

### User and Friend Management
- **User Profiles**: View watchlists and reviews of users.
- **Add Friends**: Connect with other users to share recommendations.
- **Remove Friends**: Manage connections by removing friends.
- **Common Friends**: View mutual connections with other users.

## Database Design

The database consists of 7 tables:
1. **users**: Stores user information (ID, username, email, password, created_at).
2. **movies**: Contains movie details (ID, title, genres).
3. **ratings**: Stores user ratings for movies.
4. **reviews**: Stores user reviews for movies.
5. **watchlists**: Manages users' saved movies.
6. **links**: Stores movie-related external links.
7. **friendship**: Tracks friendships between users.

### Relationships
- `ratings`, `reviews`, and `watchlists` tables use foreign keys to connect `users` and `movies`.
- The `friendship` table tracks relationships between users independently.

## Implementation Details

### Backend
- **Framework**: Flask
- **Blueprints**:
  - `auth`: Manages user authentication.
  - `movies_bp`: Handles movie-related functionalities.
  - `user`: Supports user profile and friendship operations.

### Frontend
- **Technologies**: HTML, CSS, JavaScript
- **Integration**: Communicates with the Flask backend to fetch and render data dynamically.
