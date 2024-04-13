CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT,
    username VARCHAR(30) UNIQUE,
    hashed_password VARCHAR(255),
    level INT DEFAULT 0,
    priviledge INT DEFAULT 0,
    PRIMARY KEY (id)
);    

CREATE TABLE IF NOT EXISTS variables (
    id INT AUTO_INCREMENT,
    user_id INT,
    name VARCHAR(30),
    val VARCHAR(255),
    PRIMARY KEY (id),
    UNIQUE KEY cmb (user_id, name)
);
