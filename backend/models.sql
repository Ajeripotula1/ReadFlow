-- Users Table

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
);

-- Books Table (to store books from API)
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    external_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    description TEXT,
    image_url TEXT
);

-- UserBooks Table (user's reading list)
CREATE TABLE IF NOT EXISTS user_books (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    UNIQUE(user_id, book_id)

);
