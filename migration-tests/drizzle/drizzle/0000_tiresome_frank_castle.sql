CREATE TABLE `book` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` text,
	`author_id` int,
	CONSTRAINT `book_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `user` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` text,
	CONSTRAINT `user_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
ALTER TABLE `book` ADD CONSTRAINT `book_author_id_user_id_fk` FOREIGN KEY (`author_id`) REFERENCES `user`(`id`) ON DELETE no action ON UPDATE no action;