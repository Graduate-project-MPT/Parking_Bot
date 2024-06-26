USE db;

create table wp_user(
    ID bigint not null auto_increment primary key,
    user_login varchar(255) not null unique,
    user_pass varchar(255) not null,
    user_nicename varchar(255) not null,
    user_email varchar(255) not null,
    user_url varchar(255) not null,
    user_registered bigint not null,
    user_status int not null,
    user_display_name varchar(255) not null
);
INSERT INTO wp_user (user_login, user_pass, user_nicename, user_email, user_url, user_registered, user_status, user_display_name)
VALUES
  ('user1', '$2a$04$eGyRRh99ZVxqdR7s8S9hs.H6xMFRqrKIMOfII1sOfCkfbpeLGYCpC', 'User One', 'user1@email.com', 'http://user1.com', NOW(), 1, 'User One'),
  ('user2', '$2a$04$eGyRRh99ZVxqdR7s8S9hs.H6xMFRqrKIMOfII1sOfCkfbpeLGYCpC', 'User Two', 'user2@email.com', 'http://user2.com', NOW(), 1, 'User Two'),
  ('user3', '$2a$04$eGyRRh99ZVxqdR7s8S9hs.H6xMFRqrKIMOfII1sOfCkfbpeLGYCpC', 'User Three', 'user3@email.com', 'http://user3.com', NOW(), 1, 'User Three');


CREATE TABLE wp_place(
	ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	place_is_valid BIT NOT NULL DEFAULT(1),
	place_code VARCHAR(4) NOT NULL UNIQUE,
	
	CONSTRAINT CH_code_place CHECK(place_code REGEXP '[A-Z][0-9][0-9][0-9]')
);
INSERT into wp_place (place_code)
SELECT CONCAT(
		CHAR(let_code._code USING utf8mb4),
        num.num
)
FROM
	(
		SELECT Concat(a.num, b.num, c.num) AS num FROM
			(SELECT 0 AS num UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS a,
			(SELECT 0 AS num UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS b,
			(SELECT 0 AS num UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS c
		Where (a.num * 100 + b.num * 10 + c.num) < 25
        ORDER BY num
	) AS num,
	(
		SELECT (a.digit * 10 + b.digit) AS _code FROM
			(SELECT 6 AS digit UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS a,
			(SELECT 0 AS digit UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS b
		WHERE (a.digit * 10 + b.digit) <= 90 && (a.digit * 10 + b.digit) >= 65
        ORDER BY _code
	) let_code
ORDER BY let_code._code, num.num;

create table wp_usermeta(
    ID bigint not null auto_increment primary key,
    user_id bigint not null,
    user_meta_key varchar(100) null,
    user_meta_value longtext null,
    foreign key (user_id) references wp_user (ID)
);

create table wp_message(
    ID bigint not null auto_increment primary key,
    message_date bigint null default(now()),
	message_user_telegram_id bigint not null,
	message_bot_telegram_id bigint not null,
    message_telegram_id bigint not null,
    message_text text null,

    user_id bigint null,
    message_answer_id bigint null,
    foreign key (message_answer_id) references wp_message(ID),
    foreign key (user_id) references wp_user (ID)
);

create table wp_document(
    ID bigint not null auto_increment primary key,
    message_id bigint not null,
    document_file_id varchar(100),
    document_file_unique_id varchar(100),
    document_file_size bigint,
    document_file_url  text,
    document_file_mime text,

    foreign key (message_id) references wp_message(ID)
);

create table wp_documentmeta(
    ID bigint not null auto_increment primary key,
    message_id bigint not null,
    document_meta_key varchar(100) null,
    document_meta_value longtext null,
    foreign key (message_id) references wp_message(ID)
);

CREATE TABLE wp_reserve(
	ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,

	reserve_begin BIGINT NOT NULL DEFAULT(NOW()),
	reserve_end BIGINT NOT NULL,

	reserve_is_started BIT NOT NULL DEFAULT 0,
	reserve_is_deleted BIT NOT NULL DEFAULT 0,

	place_id BIGINT NULL,
	user_id BIGINT NULL,

	FOREIGN KEY(place_id) REFERENCES wp_place(ID),
	FOREIGN KEY(user_id) REFERENCES wp_user(ID),
	
	CONSTRAINT CH_timestamp_reserve CHECK(reserve_begin < reserve_end)
);


-- Trigger tables

-- CREATE TABLE wp_auth_history(
-- 	ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
-- 	ahistory_user_telegram_id BIGINT NOT NULL,
-- 	ahistory_user_login TEXT NOT NULL,
-- 	ahistory_user_auth_datetime BIGINT NOT NULL DEFAULT(NOW())
-- );

-- CREATE TABLE wp_reserve_history(
-- 	ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
-- 	rhistory_id_reserve BIGINT NOT NULL,
-- 	rhistory_user_login TEXT NOT NULL,
-- 	rhistory_begin_reserve BIGINT NOT NULL,
-- 	rhistory_end_reserve BIGINT NOT NULL,
-- 	rhistory_place_code VARCHAR(4) NULL,
-- 	rhistory_is_deleted_reserve BIT NOT NULL DEFAULT(0)
-- );

-- Triggers
-- DELIMITER //
-- CREATE TRIGGER reserve_insert
-- AFTER INSERT ON wp_reserve
-- FOR EACH ROW
-- BEGIN
-- 	INSERT INTO wp_reserve_history(rhistory_id_reserve,
-- 		rhistory_begin_reserve, rhistory_end_reserve, rhistory_user_login)
-- 		(select r.ID, r.reserve_begin, r.reserve_end, u.user_login
-- 			from wp_reserve r
-- 			inner join wp_user u on r.user_id = u.ID
-- 			WHERE r.ID = NEW.ID
-- 		);
-- END//

-- CREATE TRIGGER reserve_update
-- BEFORE UPDATE ON wp_reserve
-- FOR EACH ROW
-- BEGIN
-- 	-- IF(NEW.reserve_is_started = 1) THEN
-- 		IF EXISTS (
-- 			SELECT * from wp_reserve
-- 				WHERE (
-- 					(NEW.reserve_begin BETWEEN reserve_begin AND reserve_end) OR
-- 					(NEW.reserve_end BETWEEN reserve_begin AND reserve_end)
-- 				) AND (NEW.place_id IS NOT NULL) AND (NEW.place_id = place_id) AND (reserve_is_deleted = 0)
-- 		) THEN
-- 			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Пересечение диапазонов дат недопустимо';
-- 		END IF;
	-- 	UPDATE wp_reserve_history SET 
	-- 		rhistory_place_code = 
	-- 			(SELECT place_code FROM wp_place WHERE ID = NEW.place_id)
	-- 		WHERE rhistory_id_reserve = NEW.ID;
	-- ELSE
	-- 	UPDATE wp_reserve_history SET rhistory_is_deleted_reserve = NEW.reserve_is_deleted
	-- 		WHERE rhistory_id_reserve = NEW.ID;
	-- END IF;
-- END//

CREATE TRIGGER reserve_check
BEFORE UPDATE ON wp_reserve
FOR EACH ROW
BEGIN
	-- Обновление is_deleted is_started в истории
	IF(NEW.place_id IS NULL) THEN
		RETURN
	END IF
	IF NOT EXISTS (
		SELECT * from wp_reserve
			WHERE (
				(NEW.reserve_begin BETWEEN reserve_begin AND reserve_end) OR
				(NEW.reserve_end BETWEEN reserve_begin AND reserve_end)
			) AND (NEW.place_id = place_id) AND (reserve_is_deleted = 0)
	) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Пересечение диапазонов дат недопустимо';
    END IF;
END//
-- DELIMITER //