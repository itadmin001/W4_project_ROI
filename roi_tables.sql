CREATE TABLE Users (
  user_id INT AUTO_INCREMENT,
  fname VARCHAR,
  lname VARCHAR,
  email VARCHAR,
  phone VARCHAR,
  pwd VARCHAR,
  pic_url VARCHAR,
  PRIMARY KEY (user_id)
);

CREATE TABLE Property (
  prop_id INT AUTO_INCREMENT=1,
  user_id INT,
  address VARCHAR,
  purch_price DECIMAL,
  est_rent DECIMAL,
  PRIMARY KEY (prop_id),
  FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Expense (
  exp_id INT AUTO_INCREMENT,
  prop_id INT,
  name VARCHAR,
  amount DECIMAL,
  PRIMARY KEY (exp_id),
  FOREIGN KEY (prop_id) REFERENCES Property(prop_id)
);

CREATE TABLE Income (
  inc_id INT AUTO_INCREMENT,
  prop_id INT,
  name VARCHAR,
  amount DECIMAL,
  PRIMARY KEY (inc_id),
  FOREIGN KEY (prop_id) REFERENCES Property(prop_id)
);

