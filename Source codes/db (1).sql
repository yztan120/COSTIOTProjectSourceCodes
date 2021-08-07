DROP DATABASE costDevices;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
--GRANT ALL PRIVILEGES ON *.* TO 'yusuf'@'%';
--GRANT ALL PRIVILEGES ON *.* TO 'yusuf'@'localhost';
CREATE USER 'costyusuf'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON * . * TO 'costyusuf'@'localhost';
FLUSH PRIVILEGES;
-- -----------------------------------------------------
-- Schema costDevices
-- -----------------------------------------------------
CREATE DATABASE IF NOT EXISTS `costDevices` ;
USE `costDevices` ;





-- -----------------------------------------------------
-- Table `costDevices`.`patioShade`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `costDevices`.`patioShade` (
  `num` INT NOT NULL AUTO_INCREMENT,
  `appliance` VARCHAR(50) NOT NULL,
  `status` VARCHAR(50) NOT NULL,
  `shadeCovered` INT NOT NULL,
  `editedby` VARCHAR(50) NOT NULL,
  `timestamp` VARCHAR(25) NOT NULL,
  PRIMARY KEY (`num`))
ENGINE = InnoDB;

-- INSERT INTO `costDevices`.`patioShade` (`appliance`, `status`, `shadeCovered`) VALUES ('patioShade', 'ON', '75');


-- -----------------------------------------------------
-- Table `costDevices`.`samsungTv`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `costDevices`.`samsungTv` (
  `num` INT NOT NULL AUTO_INCREMENT,
  `appliance` VARCHAR(50) NOT NULL,
  `status` VARCHAR(50) NOT NULL,
  `tvChannel` INT NOT NULL,
  `editedby` VARCHAR(50) NOT NULL,
  `timestamp` VARCHAR(25) NOT NULL,
  PRIMARY KEY (`num`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `costDevices`.`tempSensor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `costDevices`.`tempSensor` (
  `temperature` VARCHAR(50) NOT NULL)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `costDevices`.`users`
-- -----------------------------------------------------

CREATE TABLE users(
`id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
PRIMARY KEY (`id`));
ENGINE = InnoDB;

-- -----------------------------------------------------


create table temperaturesensor(id int not null auto_increment, Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, temperature varchar(255), category varchar(255), status varchar(255), primary key (id));
create table iotsensor(id int not null auto_increment, Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, state varchar(255), primary key (id));

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;