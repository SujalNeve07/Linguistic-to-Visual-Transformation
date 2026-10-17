create database facetrace;
use facetrace;
CREATE TABLE criminals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    crime TEXT,
    image LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);