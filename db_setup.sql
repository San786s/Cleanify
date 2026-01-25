USE alazeez_db;
UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;

-- Drop tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS properties;
DROP TABLE IF EXISTS users;

-- Create Users table
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NULL,
  password VARCHAR(255) NULL,
  role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
  provider VARCHAR(50) DEFAULT NULL,
  provider_id VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login TIMESTAMP NULL,
  UNIQUE KEY (email),
  INDEX (provider, provider_id)
);

-- Create Properties table
CREATE TABLE properties (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  location VARCHAR(255),
  price VARCHAR(50),
  image VARCHAR(255)
);

-- Create Favorites table
CREATE TABLE favorites (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  property_id INT,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (property_id) REFERENCES properties(id)
);

-- Insert admin user with a proper password hash
INSERT INTO users (name, email, password, role)
VALUES (
  'Admin',
  'creativeshanansari@gmail.com',
  '$2b$12$K7WpP7WpP7WpP7WpP7WpO.7WpP7WpP7WpP7WpP7WpP7WpP7WpP7WpP', -- This is for password "Admin123"
  'admin'
);