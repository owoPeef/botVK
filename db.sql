/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Дамп структуры базы данных bot
CREATE DATABASE IF NOT EXISTS `bot` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `bot`;

-- Дамп структуры для таблица bot.chats
CREATE TABLE IF NOT EXISTS `chats` (
  `chat_id` int NOT NULL DEFAULT '0',
  `user_id` int NOT NULL,
  `messages` int NOT NULL,
  `symbols` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci AVG_ROW_LENGTH=1000 ROW_FORMAT=COMPACT;

-- Дамп данных таблицы bot.chats: ~1 rows (приблизительно)
DELETE FROM `chats`;
/*!40000 ALTER TABLE `chats` DISABLE KEYS */;
/*!40000 ALTER TABLE `chats` ENABLE KEYS */;

-- Дамп структуры для таблица bot.marriages
CREATE TABLE IF NOT EXISTS `marriages` (
  `marriage_id` int NOT NULL AUTO_INCREMENT,
  `marriage_date` datetime NOT NULL,
  `first_uid` int NOT NULL,
  `second_uid` int NOT NULL,
  `chat_id` int NOT NULL,
  PRIMARY KEY (`marriage_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы bot.marriages: ~0 rows (приблизительно)
DELETE FROM `marriages`;
/*!40000 ALTER TABLE `marriages` DISABLE KEYS */;
/*!40000 ALTER TABLE `marriages` ENABLE KEYS */;

-- Дамп структуры для таблица bot.requests
CREATE TABLE IF NOT EXISTS `requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) NOT NULL,
  `to_id` int NOT NULL,
  `from_id` int NOT NULL,
  PRIMARY KEY (`request_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы bot.requests: ~0 rows (приблизительно)
DELETE FROM `requests`;
/*!40000 ALTER TABLE `requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `requests` ENABLE KEYS */;

-- Дамп структуры для таблица bot.users
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int NOT NULL,
  `reg_date` datetime NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=COMPACT;

-- Дамп данных таблицы bot.users: ~2 rows (приблизительно)
DELETE FROM `users`;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
