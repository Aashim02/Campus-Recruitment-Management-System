CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100),
    password VARCHAR(100)
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    salary VARCHAR(50),
    location VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_email VARCHAR(100),
    job_id INT,
    reply VARCHAR(100)
);

CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity TEXT
);
