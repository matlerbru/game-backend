INSERT INTO users (username, hashed_password)
VALUES ("user1", "$2b$12$ztHWdHhD.R0NrcwOmHxsnOK2FMS4NRlI9fX5WtIAfqw1Msrj7E.pa"), -- password: password1
    ("user2", "$2b$12$KK1bVU72T1yMus2bJxUD.uaZ6M4ltAYYW/iBPLmRIYsHfle6Gr92C"), -- password: password2
    ("user3", "$2b$12$jK8/3P172XykdLZoUbOcZuaf9vWowg/fz7UpQ5nf.zyQxRwLn4LYC"), -- password: password3
    ("user4", "$2b$12$85/M9rGmX1Jhvtf8cQ8ENeBMTInaFWcPwk10RakpA6XCds6w88A1m"), -- password: password4
    ("user5", "$2b$12$Dtgy3TetbeDXvXgM5IYfgO8Tj1A4UyyZ0U1sI81/O3cA4ALS.YYk6"); -- password: password5

SELECT * FROM users;

INSERT variables (user_id, name, val)
VALUES (1, "key1", "value1"),
    (1, "key2", "value2"),
    (1, "key3", "value3");

SELECT * FROM variables;