CREATE DATABASE blg317e;

USE blg317e;

CREATE TABLE movies (
    movieId INT PRIMARY KEY NOT NULL,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    userId INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE reviews (
    reviewId INT PRIMARY KEY AUTO_INCREMENT,
    review_text VARCHAR(255) NOT NULL,
    movieId INT NOT NULL,
    userId INT NOT NULL,
    FOREIGN KEY (movieId) REFERENCES movies(movieId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (userId) REFERENCES users(userId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE watchlists (
    watchlistId INT PRIMARY KEY AUTO_INCREMENT,
    userId INT NOT NULL,
    movieId INT NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (movieId) REFERENCES movies(movieId)
		ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE ratings (
    ratingId INT PRIMARY KEY AUTO_INCREMENT,
    rating INT NOT NULL, 
    movieId INT NOT NULL,
    userId INT NOT NULL,

    FOREIGN KEY (movieId) REFERENCES movies(movieId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (userId) REFERENCES users(userId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE links (
    imdbId INT,
    tmdbId INT,
    movieId INT,
    FOREIGN KEY (movieId) REFERENCES movies(movieId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE friendship (
	userId INT NOT NULL,
    friendId INT NOT NULL
);

