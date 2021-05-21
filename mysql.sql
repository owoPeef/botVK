CREATE DATABASE `bot`;
CREATE TABLE `bot`.`users` (
`user_id` INT NOT NULL,
`reg_date` DATETIME NOT NULL,
PRIMARY KEY (`user_id`))
COLLATE='utf8mb4_0900_ai_ci';