/*
  Warnings:

  - You are about to drop the column `jobTitle` on the `User` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE `Post` ADD COLUMN `tag` VARCHAR(191) NOT NULL DEFAULT 'tag1';

-- AlterTable
ALTER TABLE `User` DROP COLUMN `jobTitle`;
