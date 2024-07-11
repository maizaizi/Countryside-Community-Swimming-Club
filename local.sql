CREATE schema swimming_club;

USE swimming_club;

CREATE TABLE IF NOT EXISTS account (
    account_id int NOT NULL AUTO_INCREMENT,
    username varchar(100) NOT NULL UNIQUE,
    `password` varchar(255) NOT NULL,
    `role` Enum ('member', 'instructor','manager') NOT NULL,
    PRIMARY KEY (account_id)
);

CREATE TABLE IF NOT EXISTS member (
    member_id int NOT NULL AUTO_INCREMENT,
    account_id int NOT NULL,
    title varchar(100) NOT NULL,
    first_name varchar(100) NOT NULL,
    family_name varchar(100) NOT NULL,
    position varchar(100) NOT NULL,
    phone varchar(100) NOT NULL,
    email varchar(100) NOT NULL,
    `address` varchar(255)NOT NULL,
    dob date NOT NULL, 
    `image` varchar(255),
    health_info varchar(255),
    `status` Enum ('active', 'inactive') NOT NULL default 'active',
    PRIMARY KEY (member_id),
    FOREIGN KEY (account_id) REFERENCES account (account_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS instructor (
    instructor_id int NOT NULL AUTO_INCREMENT,
    account_id int NOT NULL,
    title varchar(100) NOT NULL,
    first_name varchar(100) NOT NULL,
    family_name varchar(100) NOT NULL,
    position varchar(100) NOT NULL,
    phone varchar(100) NOT NULL,
    email varchar(100) NOT NULL,
    `profile` text NOT NULL,
    `expert_area` varchar(225) NOT NULL,
    `image` varchar(255) NOT NULL, 
    `status` Enum ('active', 'inactive') NOT NULL default 'active',
    PRIMARY KEY (instructor_id),
    FOREIGN KEY (account_id) REFERENCES account (account_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS manager (
    manager_id int NOT NULL AUTO_INCREMENT,
    account_id int NOT NULL,
    title varchar(100) NOT NULL,
    first_name varchar(100) NOT NULL,
    family_name varchar(100) NOT NULL,
    position varchar(100) NOT NULL,
    phone varchar(100) NOT NULL,
    email varchar(100) NOT NULL, 
    `status` Enum ('active', 'inactive') NOT NULL default 'active',
    PRIMARY KEY (manager_id),
    FOREIGN KEY (account_id) REFERENCES account (account_id) ON UPDATE CASCADE ON DELETE CASCADE
);



-- Table for instructor availability
CREATE TABLE IF NOT EXISTS available_time (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instructor_id INT NOT NULL,
    `day` ENUM('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY') NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table class
CREATE TABLE IF NOT EXISTS class (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    `type` ENUM('Group Class','Individual Lesson') NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `image` varchar(255) NOT NULL,
    duration INT NOT NULL,
    price DECIMAL(5,2) NOT NULL,
    `capacity` INT NOT NULL,
    `status` Enum ('active', 'inactive') NOT NULL default 'active'
);

-- Table for pool
CREATE TABLE IF NOT EXISTS pool (
    pool_id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(100) NOT NULL
);
-- Table for lane
CREATE TABLE IF NOT EXISTS lane (
    lane_id INT AUTO_INCREMENT PRIMARY KEY,
    pool_id INT NOT NULL,
    `name` varchar(100) NOT NULL,
    FOREIGN KEY (pool_id) REFERENCES pool(pool_id) ON UPDATE CASCADE ON DELETE CASCADE
);


-- Table for Schedules
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
     `day` ENUM('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    pool_id INT,
    lane_id INT,
    class_id INT,
    instructor_id INT NOT NULL,
    `capacity` INT NOT NULL,
    `status` Enum ('active', 'inactive') NOT NULL default 'active',
    FOREIGN KEY (lane_id) REFERENCES lane(lane_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (pool_id) REFERENCES pool(pool_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (class_id) REFERENCES class(class_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON UPDATE CASCADE ON DELETE CASCADE
);



-- Table for Subscription
CREATE TABLE IF NOT EXISTS subscription (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `type`  VARCHAR(50) NOT NULL,
    price DECIMAL(6,2) NOT NULL
);


-- Table for Memberships
CREATE TABLE IF NOT EXISTS memberships (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    `type`  VARCHAR(50) NOT NULL,
    `start_date` DATE NOT NULL,
    `expiry_date` DATE NOT NULL,
    FOREIGN KEY (member_id) REFERENCES member(member_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table for Bookings
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    class_id INT NOT NULL,
    instructor_id INT NOT NULL,
    schedule_id INT NOT NULL,
    class_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    payment_status ENUM('pending', 'paid') NOT NULL,
    payment_amount DECIMAL(5,2),
    booking_status ENUM('confirmed','pending','cancelled','completed') DEFAULT 'pending' NOT NULL,
    FOREIGN KEY (member_id) REFERENCES member(member_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES class(class_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table for Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    `type` ENUM('subscription', 'lesson') NOT NULL,
    member_id INT,
    booking_id INT, 
    `date` DATE NOT NULL,
    amount INT NOT NULL,
    payment_status ENUM('pending', 'paid','cancelled') NOT NULL,
    FOREIGN KEY (member_id) REFERENCES member(member_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON UPDATE CASCADE ON DELETE CASCADE
);


-- Table for Attendance

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    attended BOOLEAN NOT NULL,
    UNIQUE (booking_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON UPDATE CASCADE ON DELETE CASCADE
);



-- Table for News
CREATE TABLE news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    publish_date DATE NOT NULL
);

-- Table for Reminders
CREATE TABLE reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    `date` DATE NOT NULL,
    `status` ENUM ('read','unread') DEFAULT 'unread',
    FOREIGN KEY(member_id) REFERENCES member(member_id) ON UPDATE CASCADE ON DELETE CASCADE  
);


INSERT INTO subscription (type,price) VALUES ('Annually',700);
INSERT INTO subscription (type,price) VALUES ('Monthly',60);

INSERT INTO account (username, `password`,`role`) VALUES ('jo','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','manager');
INSERT INTO account (username, `password`,`role`) VALUES ('joeysu','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','instructor');
INSERT INTO account (username, `password`,`role`) VALUES ('ashley','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','instructor');
INSERT INTO account (username, `password`,`role`) VALUES ('momo','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','instructor');
INSERT INTO account (username, `password`,`role`) VALUES ('marshal','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('jun','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('henry','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('ivy','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('eric','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('aaron','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','instructor');
INSERT INTO account (username, `password`,`role`) VALUES ('sara','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','instructor');
INSERT INTO account (username, `password`,`role`) VALUES ('helloworld','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','manager');
INSERT INTO account (username, `password`,`role`) VALUES ('lincoln','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('wigram','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('newzealand','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('chch','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('hilincoln','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('wendy','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('vivi','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('Rebecca','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('tim','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('ant','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('ironman','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('captain','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('anenger','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('hulk','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('Juliette','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('Weiss','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('Brian','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');
INSERT INTO account (username, `password`,`role`) VALUES ('David','4234c1a1c5aff1707df0891e781e248472a7783e89e6600d7125e806844c6e27','member');


INSERT INTO manager (account_id,title,first_name,family_name, position,phone,email) 
VALUES (1,'Mr','Jo','Su','Manager','02108898231','josu@gmail.com');

INSERT INTO manager (account_id,title,first_name,family_name, position,phone,email) 
VALUES (12,'Miss','Wendy','Zhao','Manager','0210297361','wendy@gmail.com');

INSERT INTO instructor (account_id,title,first_name,family_name, position,phone,email,profile,expert_area,image) 
VALUES (2,'Mr','Joey','Su','Swimmer','0210297363','sushiyi@gmail.com','good at swimming','Aqua Yoga,Aqua Zumba,Aqua Fit,Mums and Babies,Aqua Jog,One-on-one swimming','1.jpg');

INSERT INTO instructor (account_id,title,first_name,family_name, position,phone,email,profile,expert_area,image) 
VALUES (3,'Mr','Ashley','Wang','Instructor','0210297362','ashleywang@gmail.com','Aqua jog,Swimming','Aqua Yoga,Aqua Zumba,Aqua Fit,Mums and Babies,Aqua Jog,One-on-one swimming','2.jpg');

INSERT INTO instructor (account_id,title,first_name,family_name, position,phone,email,profile,expert_area,image) 
VALUES (4,'Mr','Momo','Su','Senior Instructor','0210297363','sumaomao@gmail.com','Aqua jog,Swimming,Aqua Zumba','Aqua Yoga,Aqua Zumba,Aqua Fit,Mums and Babies,Aqua Jog,One-on-one swimming','3.jpg');

INSERT INTO instructor (account_id,title,first_name,family_name, position,phone,email,profile,expert_area,image) 
VALUES (10,'Mx','Aaron','Armstrong','Instructor','0215653248','aaron@gmail.com','Aqua jog,Swimming','Aqua Yoga,Aqua Zumba,Aqua Fit,Mums and Babies,Aqua Jog,One-on-one swimming','8.jpg');

INSERT INTO instructor (account_id,title,first_name,family_name, position,phone,email,profile,expert_area,image) 
VALUES (11,'None','Sara','He','Senior Instructor','02135554983','sara@gmail.com','Aqua jog,Swimming,Aqua Zumba','Aqua Yoga,Aqua Zumba,Aqua Fit,Mums and Babies,Aqua Jog,One-on-one swimming','9.jpg');



INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (5,'Mr','Marshal','Marshal','Sales','0215653248','marshal@gmail.com','Lincoln','2000-12-01');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob,image) 
VALUES (6,'Miss','Jun','Su','Tutor','0215653248','junsun@gmail.com','Auckland','2001-01-01','4.jpg');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob,image) 
VALUES (7,'Mr','Henry','He','Manager','02135554983','henryhe@gmail.com','Hamilton','2002-01-01','5.jpg');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob,image) 
VALUES (8,'Miss','Ivy','Yang','Manager','02135554983','ivyyang@gmail.com','Lincoln','1989-01-01','6.jpg');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob,image) 
VALUES (9,'None','Eric','Zhou','Member','02135554988','ericzhou@gmail.com','Avonhead','2000-05-01','7.jpg');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (13,'Miss','Na','Wang','Sales','0213555499','nawang@gmail.com','Lincoln','1988-10-01');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (14,'Mr','Andy','Armstrong','Admin','02102232452','andy@gmail.com','Wigram','1987-10-01');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (15,'Miss','Jing','Ning','actor','0210839283','ningning@gmail.com','Halswell','1995-09-01');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (16,'Miss','Amanda','Kennett','Doctor','0272206586','amanda@gmail.com','Lincoln','2000-10-01');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (17,'Mr','Peter','Campbell','Builder','0275804944','peter@gmail.com','Lincoln','1990-10-01');

INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (18,'Mr','Stuart','Rogers','Singer','0212757767','roger@gmail.com','Rolleston','1993-10-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (19,'Mr','Josh','Chen','Farmer','0210710218','hoshr@gmail.com','Rolleston','1973-10-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (20,'Mr','Tim','Miller','Farmer','078671221','tim@gmail.com','Rolleston','1963-10-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (21,'Mrs','Jenny','McCracken','Farmer','0211265701','jenny@gmail.com','Rolleston','1963-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (22,'Mr','Brian','Henry','Farmer','0292007226','hensss@gmail.com','Rolleston','1964-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (23,'Mrs','Maz','Robertson','Farmer','0274496679','mazzzzz@gmail.com','Rolleston','1984-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (24,'Mrs','Sherry','Lee','Farmer','0274724408','lee@gmail.com','Rolleston','1985-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (25,'Mrs','Lingling','Lee','Farmer','0212757767','leelinlin@gmail.com','Rolleston','1987-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (26,'Mrs','Susan','Ding','Farmer','021393114','susan@gmail.com','Rolleston','1987-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (27,'Mrs','Juliette','Weiss','Farmer','02626737245','Juliette@gmail.com','Rolleston','1987-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (28,'Mrs','Sarah','Weiss','Farmer','02102421922','Sarah@gmail.com','Rolleston','1987-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (29,'Mrs','Feb','Sasa','Farmer','0211292079','sasasa@gmail.com','Rolleston','1987-08-01');
INSERT INTO member (account_id,title,first_name,family_name, position,phone,email,address,dob) 
VALUES (30,'Mrs','Wednesday','Tylor','Farmer','0212757767','tylor@gmail.com','Rolleston','1987-08-01');

-- add pool
INSERT INTO pool (name) VALUE ('Lane pool');
INSERT INTO pool (name) VALUE ('Deep pool');

-- add lane
INSERT INTO lane (pool_id,name) VALUES (1,1);
INSERT INTO lane (pool_id,name) VALUES (1,2);
INSERT INTO lane (pool_id,name) VALUES (1,3);
INSERT INTO lane (pool_id,name) VALUES (1,4);
INSERT INTO lane (pool_id,name) VALUES (1,5);
INSERT INTO lane (pool_id,name) VALUES (1,6);
INSERT INTO lane (pool_id,name) VALUES (1,7);
INSERT INTO lane (pool_id,name) VALUES (1,8);
INSERT INTO lane (pool_id,name) VALUES (1,9);
INSERT INTO lane (pool_id,name) VALUES (1,10);

-- add class
INSERT INTO class (name,type,description,image,duration,price,capacity) VALUES ('Aqua Yoga','Group Class','Aqua Yoga is a low-impact aquatic exercise, performing yoga poses in water. Aqua Yoga poses help you develop strength, static balance, and increases range of motion with little to no impact on joints, especially knees, hips, and ankles. No yoga experience is necessary.','aqua_yoga.jpg',60,0,15);
INSERT INTO class (name,type,description,image,duration,price,capacity) VALUES ('Aqua Zumba','Group Class','Dance the calories away with this safe, challenging, water-based workout.','aqua_zumba.jpg',60,0,15);
INSERT INTO class (name,type,description,image,duration,price,capacity) VALUES ('Aqua Fit','Group Class','A medium to high-intensity class, incorporating equipment to improve core stability and balance, while increasing muscular strength endurance and overall flexibility.','aqua_fit.jpg',60,0,15);
INSERT INTO class (name,type,description,image,duration,price,capacity) VALUES ('Mums and Babies','Group Class','Group class with caregiver and child in the water. Develop water confidence and safety skills for your child in a fun and interactive way.','mums_babies.jpg',60,0,15);
INSERT INTO class (name,type,description,image,duration,price,capacity) VALUES ('Aqua Jog','Group Class','Experience a unique and effective form of exercise that combines the benefits of water resistance with the motion of running. Aqua jogging, also known as water running, is a low-impact workout that provides a multitude of advantages for individuals of all fitness levels.','aqua_jog.jpg',60,0,15);
INSERT INTO class (name,type,description,image,duration,price,capacity) VALUES ('One-on-one swimming','Individual Lesson',"Privates are great for those who may have special requirements or those that don't respond well in group lessons. No matter what the reason is we can help you.",'swim.jpg',30,50,1);
INSERT INTO class (name,type,description,image,duration,price,capacity) VALUES ('Aqua Gentle','Group Class','Aqua Gentle is a gentle, low-intensity workout in the hydrotherapy pool aimed to gain strength and mobility while improving flexibility and coordination.','aqua_gentle.jpg',60,0,15);

-- add instructor available time
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (1,'MONDAY','6:00','10:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (1,'FRIDAY','16:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (1,'WEDNESDAY','16:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (1,'THURSDAY','6:00','12:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (1,'THURSDAY','13:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (1,'SUNDAY','6:00','20:00');

INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (2,'MONDAY','9:00','13:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (2,'WEDNESDAY','16:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (2,'THURSDAY','9:00','13:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (2,'FRIDAY','6:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (2,'SATURDAY','6:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (2,'SUNDAY','6:00','20:00');

INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (3,'MONDAY','6:00','10:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (3,'SATURDAY','6:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (3,'SUNDAY','6:00','10:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (3,'FRIDAY','10:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (3,'THURSDAY','8:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (3,'WEDNESDAY','6:00','10:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (3,'TUESDAY','12:00','20:00');

INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (4,'MONDAY','15:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (4,'SATURDAY','6:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (4,'WEDNESDAY','10:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (4,'TUESDAY','6:00','16:00');

INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (5,'MONDAY','8:00','12:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (5,'MONDAY','16:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (5,'FRIDAY','16:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (5,'SUNDAY','6:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (5,'WEDNESDAY','15:00','20:00');
INSERT INTO available_time (instructor_id,day,start_time,end_time) VALUES (5,'TUESDAY','6:00','20:00');

-- add schedules
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','7:00','8:00',2,1,3,15);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','8:00','8:30',9,1,6,1,1);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','12:00','13:00',2,2,2,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','10:00','11:00',2,7,5,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','17:00','18:00',2,4,5,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','6:00','7:00',2,5,5,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','11:00','12:00',2,1,4,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','11:00','12:00',2,3,4,15);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','9:00','9:30',8,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','16:00','16:30',5,1,6,5,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','7:00','7:30',2,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','11:00','12:00',2,2,3,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','9:00','10:00',2,5,5,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','17:00','18:00',2,3,4,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','18:30','19:30',2,7,4,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','9:00','10:00',2,3,4,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','14:00','15:00',2,7,3,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','17:00','18:00',2,2,3,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','11:00','12:00',2,4,4,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','8:00','9:00',2,2,3,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','17:00','18:00',2,1,4,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','18:30','19:30',2,5,5,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','9:00','10:00',2,4,3,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','17:00','18:00',2,3,1,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','19:00','20:00',2,7,1,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','7:00','8:00',2,7,2,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','9:00','10:00',2,5,2,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','14:00','15:00',2,3,2,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','8:00','9:00',2,1,2,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','10:00','11:00',2,3,4,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','17:00','18:00',2,2,3,15);

INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','7:00','8:00',2,1,2,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','8:30','9:30',2,2,1,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','12:00','13:00',2,3,5,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','15:00','16:00',2,4,2,15);
INSERT INTO schedules (day,start_time,end_time,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','17:00','18:00',2,5,2,15);

INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','8:00','8:30',6,1,6,5,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','9:30','10:00',1,1,6,1,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','9:30','10:00',3,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('MONDAY','9:30','10:00',4,1,6,2,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','8:00','8:30',1,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','8:00','8:30',2,1,6,5,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','13:00','13:30',2,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','15:00','15:30',5,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','13:00','13:30',3,1,6,5,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','13:00','13:30',3,1,6,5,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','19:00','19:30',7,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('TUESDAY','19:00','19:30',3,1,6,5,1);

INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','10:00','10:30',3,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','13:00','13:30',3,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','14:00','14:30',3,1,6,5,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','15:00','15:30',3,1,6,5,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('WEDNESDAY','16:00','16:30',4,1,6,1,1);

INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','7:00','7:30',4,1,6,1,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','8:00','8:30',4,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','13:00','13:30',4,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','13:00','13:30',1,1,6,1,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','14:00','14:30',4,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('THURSDAY','14:00','14:30',1,1,6,1,1);

INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','15:00','15:30',4,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','16:00','16:30',4,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','16:00','16:30',1,1,6,2,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','16:00','16:30',8,1,6,1,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','18:00','18:30',4,1,6,2,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('FRIDAY','18:00','18:30',1,1,6,1,1);


INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','12:00','12:30',4,1,6,2,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','12:00','12:30',1,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','12:00','12:30',7,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','14:00','14:30',8,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','14:00','14:30',4,1,6,2,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SATURDAY','14:00','14:30',1,1,6,3,1);

INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','8:00','8:30',4,1,6,4,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','8:00','8:30',1,1,6,3,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','10:00','10:30',7,1,6,1,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','10:00','10:30',8,1,6,2,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','14:00','14:30',4,1,6,2,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','14:00','14:30',7,1,6,1,1);
INSERT INTO schedules (day,start_time,end_time,lane_id,pool_id,class_id,instructor_id,capacity) VALUES ('SUNDAY','14:00','14:30',1,1,6,4,1);


-- add membership
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (1,'Annually','2023-01-16','2024-04-28');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (3,'Annually','2023-03-16','2024-03-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (2,'Annually','2023-01-16','2024-04-27');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (4,'Annually','2023-01-16','2024-04-29');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (6,'Monthly','2023-01-18','2024-06-18');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (7,'Monthly','2023-01-16','2024-04-29');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (8,'Monthly','2023-01-16','2024-04-30');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (9,'Monthly','2023-01-16','2024-03-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (10,'Monthly','2023-01-16','2024-04-19');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (11,'Annually','2023-01-16','2024-05-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (12,'Annually','2023-01-16','2024-05-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (13,'Annually','2023-01-16','2024-05-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (14,'Annually','2023-01-16','2024-05-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (15,'Annually','2023-01-16','2024-05-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (16,'Annually','2023-04-16','2024-04-16');
INSERT INTO memberships (member_id,type,start_date,expiry_date) VALUES (17,'Annually','2023-04-16','2024-04-16');

-- add bookings
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (2,7,2,26,'2024-04-19','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (2,6,3,61,'2024-04-26','14:00:00','14:30:00','paid',50.00,'confirmed');

INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,1,65,'2024-04-26','18:00:00','18:30:00','paid',50.00,'confirmed');

INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,3,2,28,'2024-04-19','14:00:00','15:00:00','paid',0.00,'confirmed');

INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (1,6,3,11,'2024-04-21','07:00:00','07:30:00','paid',50.00,'confirmed');

INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (1,1,3,1,'2024-04-15','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (2,1,3,1,'2024-04-15','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (3,1,3,1,'2024-04-15','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,1,3,1,'2024-04-15','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (6,1,3,1,'2024-04-15','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (7,1,3,1,'2024-04-15','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (8,1,3,1,'2024-04-15','07:00:00','08:00:00','paid',0.00,'confirmed');


INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (8,6,3,11,'2024-04-07','07:00:00','07:30:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (8,6,3,11,'2024-04-14','07:00:00','07:30:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,2,66,'2024-04-27','12:00:00','12:30:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,2,66,'2024-04-20','12:00:00','12:30:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,2,66,'2024-04-13','12:00:00','12:30:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,2,66,'2024-04-06','12:00:00','12:30:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,1,53,'2024-04-17','16:00:00','16:30:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,1,53,'2024-04-24','16:00:00','16:30:00','paid',50.00,'confirmed');



INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (1,1,3,1,'2024-04-29','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (2,1,3,1,'2024-04-29','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (3,1,3,1,'2024-04-29','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,1,3,1,'2024-04-29','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (6,1,3,1,'2024-04-29','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (7,1,3,1,'2024-04-29','07:00:00','08:00:00','paid',0.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (8,1,3,1,'2024-04-29','07:00:00','08:00:00','paid',0.00,'confirmed');

INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,3,39,'2024-04-22','09:30:00','10:00:00','paid',50.00,'confirmed');
INSERT INTO bookings (member_id,class_id,instructor_id,schedule_id,class_date,start_time,end_time,payment_status,payment_amount,booking_status) 
VALUES (4,6,3,39,'2024-04-29','09:30:00','10:00:00','pending',50.00,'pending');



INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',2,1,'2024-04-19',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',2,2,'2024-04-18',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,3,'2024-04-20',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,4,'2024-04-15',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',1,6,'2024-04-10',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',1,5,'2024-04-19',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',2,7,'2024-04-09',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',3,8,'2024-04-09',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,9,'2024-04-10',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',6,10,'2024-04-11',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',7,11,'2024-04-11',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',8,12,'2024-04-11',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',8,13,'2024-04-01',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',8,14,'2024-04-10',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,15,'2024-04-22',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,16,'2024-04-17',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,17,'2024-04-10',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,18,'2024-04-03',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,19,'2024-04-12',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,20,'2024-04-19',50,'paid');


INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',1,21,'2024-04-23',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',2,22,'2024-04-23',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',3,23,'2024-04-23',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,24,'2024-04-24',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',6,25,'2024-04-24',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',7,26,'2024-04-24',0,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',8,27,'2024-04-24',0,'paid');

INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,28,'2024-04-19',50,'paid');
INSERT INTO payments (type,member_id,booking_id,date,amount,payment_status) VALUES ('lesson',4,29,'2024-04-24',50,'pending');

-- add payments
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',1,'2023-01-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',1,'2024-01-28',180,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',2,'2024-02-28',120,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',4,'2023-01-28',120,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',4,'2023-03-28',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',4,'2024-03-28',60,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',3,'2023-03-28',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',11,'2023-05-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',10,'2023-01-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',10,'2024-01-16',60,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',10,'2024-02-16',60,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',10,'2024-03-16',60,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',9,'2024-01-16',120,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',8,'2024-03-01',120,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',7,'2024-01-16',60,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',7,'2024-02-16',120,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',6,'2023-01-18',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',6,'2024-01-18',300,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',12,'2023-01-16',240,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',12,'2023-05-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',13,'2023-01-16',240,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',13,'2023-05-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',14,'2023-01-16',240,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',14,'2023-05-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',15,'2023-01-16',240,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',15,'2023-05-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',16,'2023-04-16',700,'paid');
INSERT INTO payments (type,member_id,date,amount,payment_status) VALUES ('subscription',17,'2023-04-16',700,'paid');

-- add news
INSERT INTO news (title,content,publish_date) VALUES ('Christmas Closing Dates','Dear members, Contryside Swimming Club will close on 25th and 26th December during the Christmas, wish you all enjoy the Christmas holiday.','2023-12-01');
INSERT INTO news (title,content,publish_date) VALUES ('Notice of Deep Pool Maintenance','Dear members, to ensure the safety and quality of our pool facilities, regular maintenance is essential. 
We will run maintenance for Deep Pool on 24th Feb. The deep pool will be closed to all members. All aqua class will be canceled on that day. We kindly ask for your cooperation and understanding as we work to complete these necessary tasks efficiently.','2024-02-01');
