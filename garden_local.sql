DROP DATABASE IF EXISTS garden;
CREATE DATABASE `garden`;
USE `garden`;


CREATE TABLE `images` (
  `image_id` INT NOT NULL AUTO_INCREMENT,
  `filename` VARCHAR(255) NOT NULL,
  `image_status` ENUM('Active', 'Inactive') NOT NULL,
  PRIMARY KEY (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `images` (`image_id`, `filename`, `image_status`) VALUES
(1, 'place1.jpg', 'active'),
(2, 'place2.jpg', 'active'),
(3, 'place3.jpg', 'active'),
(4, 'place4.jpg', 'active'),
(5, 'place5.jpg', 'active'),
(6, 'place6.jpg', 'active'),
(7, 'place7.jpg', 'active'),
(8, 'place8.jpg', 'active'),
(9, 'place9.jpg', 'active'),
(10, 'place10.jpg', 'active'),
(11, 'place11.jpg', 'active'),
(12, 'place12.jpg', 'active'),
(13, 'place13.jpg', 'active'),
(14, 'place14.jpg', 'active'),
(15, 'place15.jpg', 'active'),
(16, 'place16.jpg', 'active'),
(17, 'place17.jpg', 'active'),
(18, 'place18.jpg', 'active'),
(19, 'place19.jpg', 'active'),
(20, 'place20.jpg', 'active'),
(21, 'instructor1.jpg', 'active'),
(22, 'instructor2.jpg', 'active'),
(23, 'instructor3.jpg', 'active'),
(24, 'instructor4.jpg', 'active'),
(25, 'instructor5.jpg', 'active');


CREATE TABLE `user` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `user_name` VARCHAR(100) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` ENUM('Member', 'Instructor', 'Manager') NOT NULL,
  `status` ENUM('Active', 'Inactive'),
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_id_unique` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `user` (`user_name`, `password`, `role`, `status`) VALUES
('Alice', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Ryan', 'f30812d888da717ac73244516f242d7a55e8b1728d1aaeeefa9be4ced85d6a46', 'Member', 'Active'),
('Ethan', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Sophia', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Mason', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Olivia', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Liam', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Emma', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Noah', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Ava', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Logan', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Isabella', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Aiden', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Mia', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Lucas', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Charlotte', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Caden', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Amelia', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Grayson', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Harper', '60dba936c868fbbfc42538edadfdbca80fbc23346476df1af7986f911cb38e34', 'Member', 'Active'),
('Bob', 'ae015f80440381b71f4a312275a970357f69880296816890ecc72d4dc04dd053', 'Instructor', 'Active'),
('Bella', 'ae015f80440381b71f4a312275a970357f69880296816890ecc72d4dc04dd053', 'Instructor', 'Active'),
('Belly', 'ae015f80440381b71f4a312275a970357f69880296816890ecc72d4dc04dd053', 'Instructor', 'Active'),
('Bell', 'ae015f80440381b71f4a312275a970357f69880296816890ecc72d4dc04dd053', 'Instructor', 'Active'),
('Blair', 'ae015f80440381b71f4a312275a970357f69880296816890ecc72d4dc04dd053', 'Instructor', 'Active'),
('Charlie', 'a72265c080c1a920a6ba6b859d634fcb8fdf75baef2c9dbd87801e436154dda6', 'Manager', 'Active'),
('Justin', 'a72265c080c1a920a6ba6b859d634fcb8fdf75baef2c9dbd87801e436154dda6', 'Manager', 'Active'),
('Lisa', 'a72265c080c1a920a6ba6b859d634fcb8fdf75baef2c9dbd87801e436154dda6', 'Manager', 'Active');

CREATE TABLE `member` (
  `member_id` INT NOT NULL AUTO_INCREMENT,
  `user_id`  INT NOT NULL,
  `title` VARCHAR(100),
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `position` VARCHAR(100),
  `phone_number` VARCHAR(20),
  `email` VARCHAR(100),
  `address` VARCHAR(100),
  `date_of_birth` DATE,
  `profile_image` LONGBLOB,
  `gardening_experience` TEXT,
  `reminder_date` DATE, 
  `is_student_or_csc` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 for student/community card holders, 0 for others',
  PRIMARY KEY (`member_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `member` (`user_id`, `title`, `first_name`, `last_name`, `position`, `phone_number`, `email`, `address`, `date_of_birth`, `gardening_experience`, `is_student_or_csc`) VALUES
('1', 'Ms.', 'Alice', 'Wonderland', 'Gardener', '0218898384', 'alice@example.com', '123 Wonderland Lane', '1990-01-01', 'Alice brings over 10 years of experience in garden management with a focus on sustainable and organic practices. She has extensive knowledge in the cultivation of both ornamental and edible plants, having overseen the transformation of urban spaces into green oases.', 0),
('2', 'Mr.', 'Ryan', 'Gosling', 'Gardener', '0218898384', 'ryan@example.com', '124 Wonderland Lane', '1995-01-01', 'With 8 years of hands-on experience, Ryan specializes in the implementation of innovative gardening techniques, including hydroponics and vertical gardening. His passion for eco-friendly gardening has led to several community green initiatives.', 1),
('3', 'Mr.', 'Ethan', 'Greenleaf', 'Junior Gardener', '0218898396', 'ethan.greenleaf@example.com', '132 Verdant Way', '1992-10-10', 'Ethan brings a fresh perspective to urban gardening, focusing on rooftop and balcony gardens to bring greenery to the cityscape.', 0),
('4', 'Ms.', 'Sophia', 'Bloomfield', 'Botanical Consultant', '0218898397', 'sophia.bloomfield@example.com', '133 Petal Place', '1988-03-21', 'Sophia has a decade of experience consulting on botanical projects, emphasizing the use of native plants to foster sustainable ecosystems.', 1),
('5', 'Mr.', 'Mason', 'Willows', 'Arborist', '0218898398', 'mason.willows@example.com', '134 Treeline Avenue', '1985-07-18', 'With a strong background in arboriculture, Mason’s expertise lies in the care and maintenance of trees within both public parks and private estates.', 0),
('6', 'Ms.', 'Olivia', 'Meadows', 'Horticultural Therapist', '0218898399', 'olivia.meadows@example.com', '135 Serenity Gardens', '1991-12-30', 'Olivia combines her horticultural knowledge with therapeutic practices to promote wellness through gardening.', 1),
('7', 'Mr.', 'Liam', 'Terra', 'Soil Specialist', '0218898400', 'liam.terra@example.com', '136 Fertility Lane', '1990-05-05', 'Liam’s extensive research in soil health has revolutionized the way organic fertilizers are used to enhance plant growth.', 0),
('8', 'Ms.', 'Emma', 'Vine', 'Plant Breeder', '0218898401', 'emma.vine@example.com', '137 Grapevine Row', '1994-09-17', 'Emma has innovated in the field of plant breeding, developing new grape varieties that are both hardier and more flavorful.', 1),
('9', 'Mr.', 'Noah', 'Grove', 'Orchard Keeper', '0218898402', 'noah.grove@example.com', '138 Orchard Outlook', '1986-11-22', 'Noah manages a sprawling orchard, applying organic principles to produce an abundance of fruit while nurturing the local ecosystem.', 0),
('10', 'Ms.', 'Ava', 'Gardner', 'Garden Designer', '0218898403', 'ava.gardner@example.com', '139 Blossom Boulevard', '1987-04-09', 'Ava’s artistic vision in garden design has been featured in various lifestyle magazines, inspiring a trend towards naturalistic landscaping.', 1),
('11', 'Mr.', 'Logan', 'Field', 'Crop Rotation Expert', '0218898404', 'logan.field@example.com', '140 Crop Circle Court', '1989-01-14', 'Logan has perfected the art of crop rotation to maximize yield while minimizing environmental impact on farmland.', 0),
('12', 'Ms.', 'Isabella', 'Thorn', 'Floral Artist', '0218898405', 'isabella.thorn@example.com', '141 Thorny Thicket Path', '1993-06-06', 'Isabella’s floral arrangements are nothing short of art, combining colors and textures to create living sculptures.', 1),
('13', 'Mr.', 'Aiden', 'Brook', 'Water Conservationist', '0218898406', 'aiden.brook@example.com', '142 River Run Road', '1987-08-25', 'Aiden has implemented numerous water-saving techniques in gardens, making a significant impact on conservation efforts.', 0),
('14', 'Ms.', 'Mia', 'Blossom', 'Children’s Gardening Educator', '0218898407', 'mia.blossom@example.com', '143 Kiddie Garden Lane', '1988-02-29', 'Mia specializes in educational programs for children, instilling a love for gardening while teaching about the environment.', 1),
('15', 'Mr.', 'Lucas', 'Woods', 'Forestry Manager', '0218898408', 'lucas.woods@example.com', '144 Woodland Way', '1983-03-15', 'Lucas oversees forest management projects, applying sustainable practices to support wildlife habitats and timber production.', 0),
('16', 'Ms.', 'Charlotte', 'Hill', 'Landscape Architect', '0218898409', 'charlotte.hill@example.com', '145 Rolling Meadows', '1989-08-08', 'Charlotte Hill has been reshaping urban environments as a landscape architect for over a decade, integrating innovative green spaces that promote social interaction and environmental responsibility.', 1),
('17', 'Mr.', 'Caden', 'Pond', 'Aquatic Horticulturist', '0218898410', 'caden.pond@example.com', '146 Water Lily Way', '1990-09-09', 'Caden Pond’s extensive knowledge of aquatic plants has led to the creation of stunning water features and sustainable pond ecosystems in various botanical gardens.', 0),
('18', 'Ms.', 'Amelia', 'Breeze', 'Environmental Scientist', '0218898411', 'amelia.breeze@example.com', '147 Windwhisper Road', '1988-10-15', 'Amelia Breeze, with her profound expertise as an environmental scientist, has spearheaded initiatives focused on climate-resilient gardening practices, integrating cutting-edge research with traditional knowledge to foster gardens that thrive in changing climates.', 1),
('19', 'Mr.', 'Grayson', 'Stone', 'Rock Garden Specialist', '0218898412', 'grayson.stone@example.com', '148 Stony Path', '1992-11-20', 'Grayson Stone is renowned for his innovative designs in rock gardening, creating spaces that celebrate the rugged beauty of alpine and desert landscapes, while emphasizing water conservation and sustainable gardening methods.', 0),
('20', 'Ms.', 'Harper', 'Meadow', 'Wildflower Expert', '0218898413', 'harper.meadow@example.com', '149 Prairie Vista', '1991-03-22', 'Harper Meadow has dedicated her career to the conservation of wildflower habitats, advocating for the preservation of native species through public education and the development of wildflower-focused gardens that serve as biodiversity hotspots.', 1);

CREATE TABLE `manager` (
  `manager_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `title` VARCHAR(100),
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `position` VARCHAR(100),
  `phone_number` VARCHAR(20),
  `email` VARCHAR(100),
  `profile_image` LONGBLOB,
  PRIMARY KEY (`manager_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `manager` (`user_id`, `title`, `first_name`, `last_name`, `position`, `phone_number`, `email`) VALUES
('26', 'Mr.', 'Charlie', 'Bucket', 'Garden Manager', '02187654321', 'charlie@example.com'),
('27', 'Mr.', 'Justin', 'Zhao', 'Garden Manager', '02193590701', 'justin@example.com'),
('28', 'Mr.', 'Lisa', 'Jeans', 'Garden Manager', '02184561470', 'lisa@example.com');


CREATE TABLE `instructor` (
  `instructor_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `title` VARCHAR(100),
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `position` VARCHAR(100),
  `phone_number` VARCHAR(20),
  `email` VARCHAR(100),
  `address` VARCHAR(100),
  `instructor_profile` TEXT,
  `profile_image` LONGBLOB,
  `image_id` INT DEFAULT NULL,
  PRIMARY KEY (`instructor_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


INSERT INTO `instructor` (`user_id`, `title`, `first_name`, `last_name`, `position`, `phone_number`, `email`, `address`, `instructor_profile`, `image_id`) VALUES
('21', 'Mr.', 'Bob', 'Green', 'Senior Gardening Instructor', '0214559876', 'bob.green@example.com', '123 Leafy Lane', 'Specializing in sustainable gardening and landscape design.','21'),
('22', 'Ms.', 'Bella', 'Thorn', 'Gardening Instructor', '0214559877', 'bella.thorn@example.com', '124 Blossom Ave', 'Expert in floral design and botanical arts.','22'),
('23', 'Ms.', 'Belly', 'Grassley', 'Junior Gardening Instructor', '0214559878', 'belly.grassley@example.com', '125 Greenfield Blvd', 'Focused on organic vegetable production and urban farming.','23'),
('24', 'Ms.', 'Bell', 'Roots', 'Gardening Instructor', '0214559879', 'bell.roots@example.com', '126 Orchard Rd', 'Enthusiastic about permaculture and soil health.','24'),
('25', 'Dr.', 'Blair', 'Bush', 'Head Gardening Instructor', '0214559880', 'blair.bush@example.com', '127 Prairie Path', 'PhD in horticulture, passionate about plant genetics and breeding.','25');



CREATE TABLE `locations` (
  `location_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255),
  `address` VARCHAR(255),
  `capacity` INT,
  `image_id` INT DEFAULT NULL,
  `status` ENUM('Active', 'Inactive'),
  PRIMARY KEY (`location_id`),
  FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `locations` (`name`, `address`, `capacity`, `status`) VALUES
('Greenhouse', '101 Garden Road', 50, 'Active'),
('Outdoor Garden', '102 Flower Lane', 100, 'Active'),
('Community Garden Center', '103 Green Thumb St', 75, 'Active'),
('Rooftop Oasis', '201 High Rise Ave', 40, 'Active'),
('Urban Farm Plot', '304 Cultivate Ct', 60, 'Active');

CREATE TABLE `subscriptions` (
  `subscription_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT,
  `type` ENUM('Annual', 'Monthly'),
  `start_date` DATE,
  `end_date` DATE,
  `status` ENUM('Active', 'Inactive'),
  `price` DECIMAL(10,2),
  PRIMARY KEY (`subscription_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `subscriptions` (`user_id`, `type`, `start_date`, `end_date`, `status`,`price`) VALUES
(1, 'Annual', '2023-03-15', '2024-03-30', 'Inactive',50),
(2, 'Annual', '2023-06-15', '2024-06-15', 'Active',35),
(3, 'Annual', '2023-03-15', '2024-04-02', 'Inactive',50),
(4, 'Annual', '2023-03-15', '2024-05-14', 'Active',35),
(5, 'Annual', '2023-03-15', '2024-03-14', 'Inactive',50),
(6, 'Annual', '2023-03-15', '2024-08-14', 'Active',35),
(7, 'Annual', '2023-03-15', '2024-11-14', 'Active',50),
(8, 'Annual', '2023-08-15', '2024-08-14', 'Active',35),
(9, 'Annual', '2023-05-15', '2024-10-14', 'Active',50),
(10, 'Annual', '2023-08-25', '2024-08-24', 'Active',35),
(11, 'Annual', '2023-03-15', '2024-06-14', 'Active',50),
(12, 'Annual', '2023-03-15', '2024-06-14', 'Active',35),
(13, 'Annual', '2023-03-15', '2024-06-14', 'Active',50),
(14, 'Annual', '2023-03-15', '2024-06-14', 'Active',35),
(15, 'Monthly', '2024-03-15', '2024-06-14', 'Active',50),
(16, 'Monthly', '2023-02-15', '2024-06-14', 'Active',3.5),
(17, 'Monthly', '2023-11-05', '2024-06-04', 'Active',5),
(18, 'Monthly', '2023-01-15', '2024-06-14', 'Active',3.5),
(19, 'Monthly', '2023-12-15', '2024-06-08', 'Active',5),
(20, 'Monthly', '2023-09-15', '2024-06-09', 'Active',3.5);

SET GLOBAL event_scheduler = ON;
CREATE EVENT IF NOT EXISTS update_subscription_status
ON SCHEDULE EVERY 1 DAY
STARTS CONCAT(CURDATE(), ' 00:00:00') + INTERVAL 1 DAY
DO
  UPDATE subscriptions
  SET status = 'Inactive'
  WHERE end_date <= CURRENT_DATE AND status != 'Inactive';

CREATE TABLE `news` (
  `news_id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255),
  `content` TEXT,
  `date_published` DATE,
  `author_id` INT,
  `news_image` LONGBLOB,
  PRIMARY KEY (`news_id`),
  FOREIGN KEY (`author_id`) REFERENCES `user`(`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `news` (`title`, `content`, `date_published`, `author_id`) VALUES
('Eco-Friendly Pest Control', 'Discover natural and eco-friendly methods to protect your garden from pests at our upcoming workshop. Learn about beneficial insects, natural repellents, and more. Perfect for gardeners of all levels.', '2024-04-15', 26),
('Water-Saving Gardening Techniques', 'As water conservation becomes increasingly important, join us to explore water-saving gardening techniques that do not compromise on your garden’s beauty or productivity. This workshop will cover topics such as drip irrigation, soil moisture management, and choosing drought-resistant plant varieties.', '2024-05-10', 26);

CREATE TABLE `workshops` (
  `workshop_id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255),
  `type` VARCHAR(50),
  `details` TEXT,
  `location_id` INT,
  `instructor_id` INT,
  `price` DECIMAL(10,2),
  `capacity` INT,
  `slots` INT,
  `date` DATE,
  `start_time` TIME,
  `end_time` TIME,
  `image_id` INT DEFAULT NULL,
  `workshop_image` LONGBLOB,
  PRIMARY KEY (`workshop_id`),
  FOREIGN KEY (`location_id`) REFERENCES `locations`(`location_id`) ON DELETE CASCADE ,
  FOREIGN KEY (`instructor_id`) REFERENCES `instructor`(`instructor_id`) ON DELETE CASCADE ,
  FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DELIMITER //
CREATE TRIGGER UpdateSlots BEFORE UPDATE ON workshops
FOR EACH ROW
BEGIN
    IF OLD.capacity <> NEW.capacity THEN
        -- Adjust slots only if there is a change in capacity
        SET NEW.slots = NEW.capacity - (OLD.capacity - OLD.slots);
    END IF;
END; //
DELIMITER ;

INSERT INTO `workshops` (`title`, `type`, `details`, `location_id`, `instructor_id`,  `price`, `capacity`, `slots`, `date`, `start_time`, `end_time`, `image_id`) VALUES
('Urban Container Gardening', 'Beginner', 'Discover the joys of urban gardening by learning how to grow vegetables, herbs, and flowers in containers.', 1, 3, 75.00, 15, 14, '2024-05-15', '10:00', '11:00', 1),
('Sustainable Gardening Practices', 'Intermediate', 'Explore sustainable gardening practices that enrich the soil, conserve water, and support biodiversity.', 2, 4, 65.00, 10, 9, '2024-04-27', '14:00', '16:00', 2),
('Herbal Gardening and Uses', 'Advanced', 'Grow your own herbal garden and learn about the various uses of herbs in cooking, medicine, and wellness.', 1, 2, 80.00, 12, 11, '2024-04-28', '10:00', '13:00', 3),
('Organic Pest Control', 'Intermediate', 'Learn natural methods to manage pests in your garden without the use of harmful chemicals.', 2, 1, 55.00, 20, 19,'2024-04-25', '15:00', '17:00', 4),
('Permaculture Principles', 'Intermediate', 'An introduction to the principles of permaculture design and how they can be applied to create sustainable and productive gardens.', 1, 5, 90.00, 8, 7, '2024-04-29', '10:00', '12:00', 5),
('Composting for Urban Gardens', 'Beginner', 'Learn the basics of composting and how it can transform your urban gardening experience by improving soil health.', 2, 1, 60.00, 20, 19,'2024-05-30', '10:00', '12:00', 6),
('Water-Smart Gardening', 'Beginner', 'Discover water-saving techniques for your garden, including drip irrigation and the use of native plants.', 1, 2, 50.00, 18, 17, '2024-06-15', '10:00', '11:00', 7),
('Introduction to Hydroponics', 'Intermediate', 'Dive into hydroponic gardening and learn how to grow plants without soil, using nutrient-rich water solutions.', 3, 3, 85.00, 15, 14, '2024-07-05', '14:00', '17:00', 8),
('Beekeeping Basics', 'Beginner', 'Explore the fundamentals of beekeeping and learn how bees can benefit your garden and the environment.', 2, 4, 75.00, 12, 11, '2024-08-10', '10:00', '12:00', 9),
('Native Plants for Landscaping', 'Advanced', 'Learn about the benefits of using native plants in landscaping to support local ecosystems and reduce maintenance.', 1, 5, 70.00, 10, 9, '2024-09-05', '15:00', '17:00', 10),
('Vegetable Gardening in Small Spaces', 'Beginner', 'Maximize your small space with vertical gardening and other techniques to grow a bounty of vegetables.', 3, 1, 65.00, 15, 14, '2024-10-10', '10:00', '12:00', 11),
('Gardening for Wildlife', 'Intermediate', 'Create a garden that attracts birds, bees, and butterflies while providing habitats and food sources.', 2, 2, 60.00, 20, 19, '2024-11-15', '13:00', '15:00', 12),
('Winter Gardening Strategies', 'Intermediate', 'Learn strategies for extending your gardening season into the colder months, including cold frames and greenhouse basics.', 1, 3, 55.00, 12, 11, '2024-12-05', '10:00', '11:00', 13),
('Edible Flowers and How to Grow Them', 'Beginner', 'Discover the beauty and taste of edible flowers. Learn how to grow, harvest, and use them in your kitchen.', 3, 4, 50.00, 18, 17, '2025-01-20', '14:00', '16:00', 14),
('Soil Health and Fertility Management', 'Advanced', 'Deep dive into soil health, understanding its structure, nutrients, and how to manage soil fertility for productive gardens.', 2, 5, 90.00, 10, 9, '2025-02-10', '10:00', '13:00', 15),
('Garden Design with Native Species', 'Intermediate', 'Learn how to design a beautiful and sustainable garden using native plant species to enhance biodiversity.', 3, 1, 80.00, 15, 14, '2025-03-15', '10:00', '12:00', 16),
('Seed Saving and Exchange', 'Beginner', 'Discover the importance of saving seeds and how to properly collect, store, and exchange them with others.', 1, 2, 45.00, 20, 19, '2025-04-12', '10:00', '12:00', 17),
('Plant Propagation Techniques', 'Intermediate', 'Master various plant propagation techniques including cuttings, division, and grafting to expand your garden.', 2, 3, 70.00, 12, 11, '2025-05-20', '14:00', '17:00', 18),
('Urban Farming Fundamentals', 'Beginner', 'An introduction to urban farming, covering basics from soil preparation to crop rotation and community gardening.', 3, 4, 65.00, 18, 17, '2025-06-18', '09:00', '11:00', 19),
('Healing Gardens: Design & Benefits', 'Advanced', 'Explore the concept of healing gardens, learn how to design them, and understand their therapeutic benefits.', 1, 5, 95.00, 10, 9, '2025-07-23', '15:00', '18:00', 20);

CREATE TABLE `lessons` (
  `lesson_id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(50),
  `details` TEXT,
  `instructor_id` INT,
  `member_id` INT,
  `date` DATE,
  `start_time` TIME,
  `end_time` TIME,
  `name` VARCHAR(255),
  `location_id` INT,
  `price` DECIMAL(10,2),
  `status` ENUM('Reserved', 'Completed', 'Available'),
  `lesson_image` LONGBLOB,
  `image_id` INT DEFAULT NULL,
  PRIMARY KEY (`lesson_id`),
  FOREIGN KEY (`instructor_id`) REFERENCES `instructor`(`instructor_id`) ON DELETE CASCADE,
  FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`) ON DELETE CASCADE,
  FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (`location_id`) REFERENCES `locations`(`location_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `lessons` (`type`, `details`, `instructor_id`, `member_id`, `date`, `start_time`, `end_time`, `name`, `location_id`, `price`, `status`, `image_id`) VALUES
('Beginner', 'This lesson offers a comprehensive guide to starting your seeds, covering the basics of soil preparation, light requirements, and initial care.', 1, 1, '2024-04-27', '10:00', '11:00', 'Seed Starting Success: A Beginner Guide', 2, 100.00, 'Reserved', 1),
('Urban Gardening', 'Learn how to transform your urban space into a green oasis with techniques on container gardening, vertical installations, and space-efficient plant choices.', 2, NULL, '2024-04-25', '10:00', '11:00', 'Urban Gardening: Maximizing Small Spaces', 2, 100.00, 'Available', 2),
('Organic Practices', 'Dive into the world of organic gardening with this essential guide on using non-synthetic fertilizers, pest control, and cultivating soil biodiversity.', 3, NULL, '2024-04-27', '10:00', '11:00', 'Organic Gardening Essentials: From Soil to Supper', 2, 100.00, 'Available', 3),
('Advanced Techniques', 'Enhance the health and productivity of your plants with expert pruning techniques for different plant species, from flowering shrubs to fruit trees.', 4, NULL, '2024-04-28', '10:00', '11:00', 'Pruning Perfection: Techniques for Healthy Plants', 2, 100.00, 'Available', 4),
('Food Gardening', 'Explore the joy of growing your own food with tips on planting, nurturing, and harvesting vegetables and herbs right from your backyard or balcony.', 5, NULL, '2024-04-29', '10:00', '11:00', 'Edible Gardens: Growing Your Own Vegetables and Herbs', 2, 100.00, 'Available', 5),
('Water Conservation', 'Learn sustainable watering practices that save water and promote healthier plants in your garden.', 1, NULL, '2024-04-30', '10:00', '11:00', 'Sustainable Watering Techniques', 3, 100.00, 'Available', 6),
('Pest Management', 'Discover natural and effective strategies for managing pests in your garden without resorting to harsh chemicals.', 2, NULL, '2024-05-01', '10:00', '11:00', 'Pest-Free Gardening: Organic Solutions', 1, 100.00, 'Available', 7),
('Composting Basics', 'This lesson covers everything you need to know to start composting, from choosing a bin to what you can and can\'t compost.', 3, NULL, '2024-05-02', '10:00', '11:00', 'Composting 101: Turning Waste into Gold', 4, 100.00, 'Available', 8),
('Landscape Design', 'Learn how to design your own garden landscape, incorporating elements of design theory to create aesthetically pleasing and functional spaces.', 4, NULL, '2024-05-03', '10:00', '11:00', 'Designing Your Dream Garden', 5, 100.00, 'Available', 9),
('Herb Gardening', 'From basil to thyme, learn how to grow a variety of herbs in any space, and how to harvest and use them.', 5, NULL, '2024-05-04', '10:00', '11:00', 'Herbal Delights: Growing and Using Culinary Herbs', 1, 100.00, 'Available', 10),
('Soil Health', 'Understand the critical importance of soil health for plant growth, including how to test and improve your garden soil.', 1, NULL, '2024-05-05', '10:00', '11:00', 'Soil Science: The Foundation of Gardening', 2, 100.00, 'Available', 11),
('Container Gardening', 'Maximize your space and grow plants anywhere by mastering the art of container gardening.', 2, NULL, '2024-05-06', '10:00', '11:00', 'Gardening Without Ground: Container Cultivation', 3, 100.00, 'Available', 12),
('Vertical Gardening', 'Learn innovative ways to grow plants vertically to enhance your space, whether indoors or outdoors.', 3, NULL, '2024-05-07', '10:00', '11:00', 'Upwards & Onwards: Vertical Gardening Basics', 4, 100.00, 'Available', 13),
('Fruit Tree Care', 'Dive into the essentials of fruit tree care, from planting to pruning and pest control, to ensure bountiful harvests.', 4, NULL, '2024-05-08', '10:00', '11:00', 'Fruitful Endeavors: Caring for Your Fruit Trees', 5, 100.00, 'Available', 14),
('Perennial Plants', 'Explore the world of perennials, learning how to select, plant, and care for these plants that will return year after year.', 5, NULL, '2024-05-09', '10:00', '11:00', 'Perennials: Plant Once, Enjoy for Years', 1, 100.00, 'Available', 15),
('Garden Tool Maintenance', 'Keep your garden tools in top condition with practical tips for cleaning, sharpening, and storing them.', 1, NULL, '2024-05-10', '10:00', '11:00', 'Tool Time: Maintaining Your Garden Tools', 2, 100.00, 'Available', 16),
('Mulching Techniques', 'Learn why mulch is your garden’s best friend and how to properly apply it to conserve moisture, control weeds, and improve soil health.', 2, NULL, '2024-05-11', '10:00', '11:00', 'Mulch Ado About Gardening: The Benefits of Mulching', 3, 100.00, 'Available', 17),
('Seasonal Planting', 'Understand how to plan your garden’s planting schedule to take full advantage of the growing season for both annuals and perennials.', 3, NULL, '2024-05-12', '10:00', '11:00', 'Seasonal Strategies: Year-Round Gardening', 4, 100.00, 'Available', 18),
('Biodiversity in the Garden', 'Learn how to create a garden that supports a wide range of plants and animals, promoting a healthy, balanced ecosystem.', 4, NULL, '2024-05-13', '10:00', '11:00', 'Wildlife Welcome: Encouraging Biodiversity', 5, 100.00, 'Available', 19),
('Garden Planning', 'Plan your garden from the ground up, focusing on layout, plant selection, and succession planting for a continuous harvest.', 5, NULL, '2024-05-14', '10:00', '11:00', 'Blueprints for Blooms: Planning Your Garden Layout', 1, 100.00, 'Available', 20);

CREATE TABLE `prices` (
  `price_id` INT NOT NULL AUTO_INCREMENT,
  `price_type` VARCHAR(255),
  `price` DECIMAL(10,2),
  PRIMARY KEY (`price_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `prices` (`price_type`, `price`)
VALUES
  ('annual_subscription', 50),
  ('monthly_subscription', 5);

  
CREATE TABLE `bookings` (
  `booking_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT,
  `workshop_id` INT,
  `lesson_id` INT,
  `booking_date` DATE,
  `status` ENUM('Reserved', 'Completed', 'Cancelled', 'Waitlist'),
  PRIMARY KEY (`booking_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE ,
  FOREIGN KEY (`workshop_id`) REFERENCES `workshops`(`workshop_id`) ON DELETE CASCADE ,
  FOREIGN KEY (`lesson_id`) REFERENCES `lessons`(`lesson_id`) ON DELETE CASCADE 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `bookings` (`user_id`, `workshop_id`, `lesson_id`, `booking_date`, `status`) VALUES
(1, 1, NULL, '2023-03-21', 'Reserved'),
(2, 2, NULL, '2024-01-15', 'Reserved'),
(3, 3, NULL, '2024-01-16', 'Reserved'),
(4, 4, NULL, '2024-01-17', 'Reserved'),
(5, 5, NULL, '2024-01-18', 'Reserved'),
(6, 6, NULL, '2024-01-19', 'Reserved'),
(7, 7, NULL, '2024-01-20', 'Reserved'),
(8, 8, NULL, '2024-01-21', 'Reserved'),
(9, 9, NULL, '2024-01-22', 'Reserved'),
(10, 10, NULL, '2024-01-23', 'Reserved'),
(11, NULL, 1, '2024-02-15', 'Reserved'),
(12, NULL, 2, '2024-02-16', 'Reserved'),
(13, NULL, 3, '2024-02-17', 'Reserved'),
(14, NULL, 4, '2024-02-18', 'Reserved'),
(15, NULL, 5, '2024-02-19', 'Reserved'),
(16, NULL, 6, '2024-02-20', 'Reserved'),
(17, NULL, 7, '2024-02-21', 'Reserved'),
(18, NULL, 8, '2024-02-22', 'Reserved'),
(19, NULL, 9, '2024-02-23', 'Reserved'),
(20, NULL, 10, '2023-03-22', 'Reserved');

CREATE TABLE `payments` (
  `payment_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT,
  `workshop_id` INT,
  `lesson_id` INT,
  `amount` DECIMAL(10,2),
  `payment_type` ENUM('Membership Fee', 'Donation', 'Workshop Fee', 'One-on-One Lesson Fee'),
  `payment_date` DATE,
  `status` ENUM('Completed', 'Pending'),
  PRIMARY KEY (`payment_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`workshop_id`) REFERENCES `workshops`(`workshop_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (`lesson_id`) REFERENCES `lessons`(`lesson_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `payments` (`user_id`, `workshop_id`, `lesson_id`, `amount`, `payment_type`, `payment_date`, `status`) VALUES
(1, NULL, 1, 100.00, 'One-on-One Lesson Fee', '2024-03-22', 'Completed'),
(2, NULL, 2, 100.00, 'One-on-One Lesson Fee', '2024-03-24', 'Completed'),
(3, NULL, 3, 100.00, 'One-on-One Lesson Fee', '2024-03-26', 'Completed'),
(4, NULL, 4, 100.00, 'One-on-One Lesson Fee', '2024-03-28', 'Completed'),
(5, NULL, 5, 100.00, 'One-on-One Lesson Fee', '2024-03-30', 'Completed'),
(6, NULL, 6, 100.00, 'One-on-One Lesson Fee', '2024-04-01', 'Completed'),
(7, NULL, 7, 100.00, 'One-on-One Lesson Fee', '2024-04-03', 'Completed'),
(8, NULL, 8, 100.00, 'One-on-One Lesson Fee', '2024-04-05', 'Completed'),
(9, NULL, 9, 100.00, 'One-on-One Lesson Fee', '2024-04-07', 'Completed'),
(10, NULL, 10, 100.00, 'One-on-One Lesson Fee', '2024-04-09', 'Completed'),
(11, 1, NULL, 50.00, 'Workshop Fee', '2023-04-04', 'Completed'),
(12, 2, NULL, 50.00, 'Workshop Fee', '2024-04-05', 'Completed'),
(13, 3, NULL, 50.00, 'Workshop Fee', '2024-04-06', 'Completed'),
(14, 4, NULL, 50.00, 'Workshop Fee', '2024-04-07', 'Completed'),
(15, 5, NULL, 50.00, 'Workshop Fee', '2024-04-08', 'Completed'),
(16, 6, NULL, 50.00, 'Workshop Fee', '2024-04-09', 'Completed'),
(17, 7, NULL, 50.00, 'Workshop Fee', '2024-04-10', 'Completed'),
(18, 8, NULL, 50.00, 'Workshop Fee', '2024-04-11', 'Completed'),
(19, 9, NULL, 50.00, 'Workshop Fee', '2024-04-12', 'Completed'),
(20, 10, NULL, 50.00, 'Workshop Fee', '2024-04-13', 'Completed'),
(1, NULL, NULL, 50.00, 'Membership Fee', '2024-03-15', 'Completed'),
(2, NULL, NULL, 35.00, 'Membership Fee', '2024-03-15', 'Completed'),
(3, NULL, NULL, 50.00, 'Membership Fee', '2024-03-15', 'Completed'),
(4, NULL, NULL, 35.00, 'Membership Fee', '2024-03-15', 'Completed'),
(5, NULL, NULL, 50.00, 'Membership Fee', '2024-03-15', 'Completed'),
(6, NULL, NULL, 35.00, 'Membership Fee', '2024-03-15', 'Completed'),
(7, NULL, NULL, 50.00, 'Membership Fee', '2024-03-15', 'Completed'),
(8, NULL, NULL, 35.00, 'Membership Fee', '2024-08-15', 'Completed'),
(9, NULL, NULL, 50.00, 'Membership Fee', '2024-05-15', 'Completed'),
(10, NULL, NULL, 35.00, 'Membership Fee', '2024-08-25', 'Completed'),
(11, NULL, NULL, 50.00, 'Membership Fee', '2024-03-15', 'Completed'),
(12, NULL, NULL, 35.00, 'Membership Fee', '2024-03-15', 'Completed'),
(13, NULL, NULL, 50.00, 'Membership Fee', '2024-03-15', 'Completed'),
(14, NULL, NULL, 35.00, 'Membership Fee', '2024-03-15', 'Completed'),
(15, NULL, NULL, 5.00, 'Membership Fee', '2024-03-15', 'Completed'),
(16, NULL, NULL, 3.50, 'Membership Fee', '2024-02-15', 'Completed'),
(17, NULL, NULL, 5.00, 'Membership Fee', '2024-11-05', 'Completed'),
(18, NULL, NULL, 3.50, 'Membership Fee', '2024-01-05', 'Completed'),
(19, NULL, NULL, 5.00, 'Membership Fee', '2024-12-15', 'Completed'),
(20, NULL, NULL, 3.50, 'Membership Fee', '2024-09-15', 'Completed')
;
