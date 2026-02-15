-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: careertrack
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `application`
--

DROP TABLE IF EXISTS `application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application` (
  `AppID` int NOT NULL,
  `MemberID` int NOT NULL,
  `JobID` int NOT NULL,
  `ApplyDate` date NOT NULL,
  `Status` varchar(20) NOT NULL DEFAULT 'Applied',
  PRIMARY KEY (`AppID`),
  KEY `MemberID` (`MemberID`),
  KEY `JobID` (`JobID`),
  CONSTRAINT `application_ibfk_1` FOREIGN KEY (`MemberID`) REFERENCES `member` (`MemberID`) ON DELETE CASCADE,
  CONSTRAINT `application_ibfk_2` FOREIGN KEY (`JobID`) REFERENCES `jobposting` (`JobID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
INSERT INTO `application` VALUES (501,1001,401,'2025-11-05','Shortlisted'),(502,1002,401,'2025-11-06','Rejected'),(503,1005,401,'2025-11-05','Shortlisted'),(504,1001,402,'2025-11-10','Applied'),(505,1003,403,'2026-01-10','Applied'),(506,1011,404,'2025-11-15','Shortlisted'),(507,1009,405,'2025-11-05','Selected'),(508,1015,407,'2025-11-18','Shortlisted'),(509,1006,406,'2026-01-05','Applied'),(510,1004,409,'2026-01-10','Rejected'),(511,1018,413,'2025-11-15','Shortlisted'),(512,1020,411,'2025-11-10','Shortlisted'),(513,1005,412,'2025-11-12','Applied'),(514,1001,414,'2025-08-10','Rejected'),(515,1016,407,'2025-11-20','Applied'),(516,1017,408,'2025-11-15','Selected'),(517,1013,411,'2025-11-10','Applied'),(518,1002,405,'2025-11-06','Shortlisted'),(519,1012,410,'2026-01-15','Applied'),(520,1008,403,'2026-01-12','Shortlisted'),(521,1019,409,'2026-01-10','Rejected'),(522,1001,404,'2025-11-12','Applied'),(523,1011,418,'2025-11-27','Shortlisted'),(524,1014,417,'2026-01-17','Selected'),(525,1007,406,'2026-01-06','Applied');
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `company`
--

DROP TABLE IF EXISTS `company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company` (
  `CompanyID` int NOT NULL,
  `CompanyName` varchar(100) NOT NULL,
  `Website` varchar(255) NOT NULL,
  `Industry` varchar(50) NOT NULL,
  `Location` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`CompanyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company`
--

LOCK TABLES `company` WRITE;
/*!40000 ALTER TABLE `company` DISABLE KEYS */;
INSERT INTO `company` VALUES (1,'Google','https://careers.google.com','Technology','Bangalore'),(2,'Microsoft','https://careers.microsoft.com','Technology','Hyderabad'),(3,'Tata Consultancy Services','https://www.tcs.com','IT Services','Mumbai'),(4,'Larsen & Toubro','https://www.larsentoubro.com','Construction','Chennai'),(5,'Goldman Sachs','https://www.goldmansachs.com','Finance','Bangalore'),(6,'Amazon','https://www.amazon.jobs','E-commerce','Hyderabad'),(7,'Maruti Suzuki','https://www.marutisuzuki.com','Automotive','Gurgaon'),(8,'Flipkart','https://www.flipkartcareers.com','E-commerce','Bangalore'),(9,'Reliance Industries','https://www.ril.com','Conglomerate','Mumbai'),(10,'Adobe','https://www.adobe.com/careers','Software','Noida'),(11,'Texas Instruments','https://careers.ti.com','Electronics','Bangalore'),(12,'Oracle','https://www.oracle.com/careers','Technology','Pune'),(13,'McKinsey & Company','https://www.mckinsey.com','Consulting','Mumbai');
/*!40000 ALTER TABLE `company` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `DeptID` int NOT NULL,
  `DeptName` varchar(100) NOT NULL,
  `HODName` varchar(100) NOT NULL,
  PRIMARY KEY (`DeptID`),
  UNIQUE KEY `DeptName` (`DeptName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (101,'Computer Science & Engineering','Dr. Anirban Dasgupta'),(102,'Electrical Engineering','Dr. Nithin V. George'),(103,'Mechanical Engineering','Dr. Vinod Narayanan'),(104,'Civil Engineering','Dr. Gaurav Srivastava'),(105,'Chemical Engineering','Dr. Sameer Dalvi'),(106,'Materials Science & Engineering','Dr. Abhay Kumar'),(107,'Physics','Dr. S. K. Gupta'),(108,'Mathematics','Dr. Indranath Sengupta'),(109,'Cognitive Science','Dr. Pratik Mutha'),(110,'Humanities & Social Sciences','Dr. Ambika Aiyadurai'),(111,'Earth Sciences','Dr. V. N. Prabhakar');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviewround`
--

DROP TABLE IF EXISTS `interviewround`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interviewround` (
  `RoundID` int NOT NULL,
  `JobID` int NOT NULL,
  `RoundType` varchar(50) NOT NULL,
  `RoundNumber` int NOT NULL,
  PRIMARY KEY (`RoundID`),
  KEY `JobID` (`JobID`),
  CONSTRAINT `interviewround_ibfk_1` FOREIGN KEY (`JobID`) REFERENCES `jobposting` (`JobID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviewround`
--

LOCK TABLES `interviewround` WRITE;
/*!40000 ALTER TABLE `interviewround` DISABLE KEYS */;
INSERT INTO `interviewround` VALUES (601,401,'Coding Assessment',1),(602,401,'Technical Interview',2),(603,401,'HR Discussion',3),(604,404,'Aptitude Test',1),(605,404,'Managerial Round',2),(606,405,'Online Coding',1),(607,405,'System Design',2),(608,407,'Data Science Challenge',1),(609,413,'Case Study Round',1),(610,413,'Partner Interview',2),(611,411,'Technical Circuit Design',1),(612,411,'HR Interview',2),(613,408,'Product Task',1),(614,403,'TCS NQT',1),(615,417,'Civil Core Test',1);
/*!40000 ALTER TABLE `interviewround` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviewschedule`
--

DROP TABLE IF EXISTS `interviewschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interviewschedule` (
  `ScheduleID` int NOT NULL,
  `AppID` int NOT NULL,
  `RoundID` int NOT NULL,
  `RecruiterID` int DEFAULT NULL,
  `InterviewDate` datetime NOT NULL,
  `MeetingLink` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ScheduleID`),
  KEY `AppID` (`AppID`),
  KEY `RoundID` (`RoundID`),
  KEY `RecruiterID` (`RecruiterID`),
  CONSTRAINT `interviewschedule_ibfk_1` FOREIGN KEY (`AppID`) REFERENCES `application` (`AppID`) ON DELETE CASCADE,
  CONSTRAINT `interviewschedule_ibfk_2` FOREIGN KEY (`RoundID`) REFERENCES `interviewround` (`RoundID`) ON DELETE CASCADE,
  CONSTRAINT `interviewschedule_ibfk_3` FOREIGN KEY (`RecruiterID`) REFERENCES `recruiter` (`RecruiterID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviewschedule`
--

LOCK TABLES `interviewschedule` WRITE;
/*!40000 ALTER TABLE `interviewschedule` DISABLE KEYS */;
INSERT INTO `interviewschedule` VALUES (701,501,602,201,'2025-12-05 10:00:00','meet.google.com/abc-defg'),(702,503,602,201,'2025-12-05 11:00:00','meet.google.com/hij-klmn'),(703,506,605,204,'2025-12-06 14:00:00','zoom.us/j/123456'),(704,507,607,205,'2025-12-02 09:00:00','hackerrank.com/test/123'),(705,518,607,205,'2025-12-02 11:00:00','hackerrank.com/test/456'),(706,511,609,213,'2025-12-03 10:00:00','mckinsey.zoom.us/case1'),(707,508,608,206,'2025-12-04 15:00:00','flipkart.meet/ds-round'),(708,512,611,211,'2025-11-25 10:00:00','ti.webex.com/tech1'),(709,516,613,207,'2025-11-29 11:00:00','adobe.meet/prod1'),(710,501,603,201,'2025-12-07 09:00:00','meet.google.com/fin-hr'),(711,523,605,204,'2025-12-10 16:00:00','zoom.us/j/999888'),(712,520,614,203,'2026-01-22 10:00:00','tcs.ion.com/nqt1'),(713,524,615,208,'2026-01-18 09:00:00','lnt.exam/civil'),(714,511,610,213,'2025-12-04 14:00:00','mckinsey.zoom.us/part2'),(715,503,603,201,'2025-12-07 10:00:00','meet.google.com/fin-hr2');
/*!40000 ALTER TABLE `interviewschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobposting`
--

DROP TABLE IF EXISTS `jobposting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jobposting` (
  `JobID` int NOT NULL,
  `CompanyID` int NOT NULL,
  `DriveID` int NOT NULL,
  `RoleTitle` varchar(100) NOT NULL,
  `Description` text,
  `Package_LPA` decimal(10,2) NOT NULL,
  `PostDate` date NOT NULL,
  `Deadline` date NOT NULL,
  PRIMARY KEY (`JobID`),
  KEY `CompanyID` (`CompanyID`),
  KEY `DriveID` (`DriveID`),
  CONSTRAINT `jobposting_ibfk_1` FOREIGN KEY (`CompanyID`) REFERENCES `company` (`CompanyID`) ON DELETE CASCADE,
  CONSTRAINT `jobposting_ibfk_2` FOREIGN KEY (`DriveID`) REFERENCES `placementdrive` (`DriveID`) ON DELETE CASCADE,
  CONSTRAINT `jobposting_chk_1` CHECK ((`Package_LPA` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobposting`
--

LOCK TABLES `jobposting` WRITE;
/*!40000 ALTER TABLE `jobposting` DISABLE KEYS */;
INSERT INTO `jobposting` VALUES (401,1,301,'Software Engineer','Core development role in Search Team',32.00,'2025-11-01','2025-11-20'),(402,2,301,'SDE-1','Backend development for Azure',28.00,'2025-11-05','2025-11-25'),(403,3,302,'System Engineer','Maintenance and development',7.50,'2026-01-05','2026-01-20'),(404,5,301,'Financial Analyst','Global Markets Division',22.00,'2025-11-10','2025-11-30'),(405,6,301,'SDE-1','AWS Cloud Services Team',30.00,'2025-11-01','2025-11-20'),(406,4,302,'Graduate Engineer Trainee','Metro Rail Projects',6.50,'2026-01-02','2026-01-15'),(407,8,301,'Data Scientist','Machine Learning and AI Logistics',26.00,'2025-11-15','2025-12-01'),(408,10,301,'Product Intern','Adobe Experience Cloud',12.00,'2025-11-12','2025-11-28'),(409,7,302,'Mechanical Engineer','R&D Chassis Design',8.00,'2026-01-08','2026-01-25'),(410,9,302,'Management Trainee','Operations Supply Chain',9.00,'2026-01-12','2026-01-30'),(411,11,301,'Analog Design Engineer','Chip design and testing',18.00,'2025-11-05','2025-11-22'),(412,12,301,'Cloud Consultant','Oracle Cloud Infrastructure',15.00,'2025-11-08','2025-11-25'),(413,13,301,'Junior Associate','Strategy Consulting',24.00,'2025-11-10','2025-11-30'),(414,1,303,'SDE Intern','Summer 2026 Internship',6.00,'2025-08-05','2025-08-20'),(415,6,303,'Operations Intern','Warehouse Management',3.60,'2025-08-10','2025-08-25'),(416,2,303,'Research Intern','AI & Deep Learning',7.20,'2025-08-12','2025-08-28'),(417,4,308,'Site Engineer','Highway Projects',6.00,'2026-01-16','2026-01-19'),(418,5,309,'Quant Strategist','Algorithmic Trading',25.00,'2025-11-26','2025-11-29'),(419,3,301,'Digital Innovator','Innovation Lab',10.00,'2025-11-05','2025-11-20'),(420,8,303,'Supply Chain Intern','Summer Program',4.00,'2025-08-15','2025-08-25');
/*!40000 ALTER TABLE `jobposting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member`
--

DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member` (
  `MemberID` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Image` varchar(255) NOT NULL,
  `Age` int NOT NULL,
  `Email` varchar(100) NOT NULL,
  `ContactNumber` varchar(15) NOT NULL,
  `CGPA` decimal(4,2) DEFAULT NULL,
  `DeptID` int DEFAULT NULL,
  PRIMARY KEY (`MemberID`),
  UNIQUE KEY `Email` (`Email`),
  KEY `DeptID` (`DeptID`),
  CONSTRAINT `member_ibfk_1` FOREIGN KEY (`DeptID`) REFERENCES `department` (`DeptID`) ON DELETE SET NULL,
  CONSTRAINT `member_chk_1` CHECK ((`Age` >= 18)),
  CONSTRAINT `member_chk_2` CHECK ((`CGPA` <= 10.0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member`
--

LOCK TABLES `member` WRITE;
/*!40000 ALTER TABLE `member` DISABLE KEYS */;
INSERT INTO `member` VALUES (1001,'Aarav Sharma','https://randomuser.me/api/portraits/men/1.jpg',21,'aarav.sharma@inst.ac.in','9988776655',8.50,101),(1002,'Vivaan Gupta','https://randomuser.me/api/portraits/men/2.jpg',22,'vivaan.g@inst.ac.in','9988776654',9.20,101),(1003,'Aditya Iyer','https://randomuser.me/api/portraits/men/3.jpg',21,'aditya.iyer@inst.ac.in','9988776653',7.80,102),(1004,'Vihaan Reddy','https://randomuser.me/api/portraits/men/4.jpg',22,'vihaan.r@inst.ac.in','9988776652',8.90,103),(1005,'Arjun Malhotra','https://randomuser.me/api/portraits/men/5.jpg',21,'arjun.m@inst.ac.in','9988776651',9.50,101),(1006,'Sai Kumar','https://randomuser.me/api/portraits/men/6.jpg',23,'sai.k@inst.ac.in','9988776650',6.90,104),(1007,'Reyansh Joshi','https://randomuser.me/api/portraits/men/7.jpg',22,'reyansh.j@inst.ac.in','9988776649',8.10,105),(1008,'Krishna Das','https://randomuser.me/api/portraits/men/8.jpg',21,'krishna.d@inst.ac.in','9988776648',7.50,102),(1009,'Ishaan Nair','https://randomuser.me/api/portraits/men/9.jpg',22,'ishaan.n@inst.ac.in','9988776647',9.00,101),(1010,'Shaurya Singh','https://randomuser.me/api/portraits/men/10.jpg',21,'shaurya.s@inst.ac.in','9988776646',8.30,103),(1011,'Diya Patel','https://randomuser.me/api/portraits/women/1.jpg',21,'diya.p@inst.ac.in','9988776645',9.10,101),(1012,'Ananya Rao','https://randomuser.me/api/portraits/women/2.jpg',22,'ananya.r@inst.ac.in','9988776644',8.70,105),(1013,'Aadhya Shah','https://randomuser.me/api/portraits/women/3.jpg',21,'aadhya.s@inst.ac.in','9988776643',7.90,102),(1014,'Kiara Choudhury','https://randomuser.me/api/portraits/women/4.jpg',22,'kiara.c@inst.ac.in','9988776642',8.40,104),(1015,'Myra Kapoor','https://randomuser.me/api/portraits/women/5.jpg',21,'myra.k@inst.ac.in','9988776641',9.30,101),(1016,'Zara Khan','https://randomuser.me/api/portraits/women/6.jpg',23,'zara.k@inst.ac.in','9988776640',8.20,106),(1017,'Nikhil Verma','https://randomuser.me/api/portraits/men/11.jpg',22,'nikhil.v@inst.ac.in','9988776639',7.40,107),(1018,'Riya Sen','https://randomuser.me/api/portraits/women/7.jpg',21,'riya.s@inst.ac.in','9988776638',9.60,101),(1019,'Kabir Bedi','https://randomuser.me/api/portraits/men/12.jpg',24,'kabir.b@inst.ac.in','9988776637',6.80,103),(1020,'Meera Reddy','https://randomuser.me/api/portraits/women/8.jpg',22,'meera.r@inst.ac.in','9988776636',8.80,102);
/*!40000 ALTER TABLE `member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `placementdrive`
--

DROP TABLE IF EXISTS `placementdrive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `placementdrive` (
  `DriveID` int NOT NULL,
  `DriveName` varchar(100) NOT NULL,
  `Year` int NOT NULL,
  `StartDate` date NOT NULL,
  `EndDate` date NOT NULL,
  PRIMARY KEY (`DriveID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `placementdrive`
--

LOCK TABLES `placementdrive` WRITE;
/*!40000 ALTER TABLE `placementdrive` DISABLE KEYS */;
INSERT INTO `placementdrive` VALUES (301,'Phase 1 Placements 2025-26',2025,'2025-12-01','2025-12-15'),(302,'Phase 2 Placements 2026',2026,'2026-01-10','2026-02-28'),(303,'Summer Internship Drive 2025',2025,'2025-08-01','2025-08-30'),(304,'Winter Internship Drive 2025',2025,'2025-10-15','2025-10-31'),(305,'Startup Fair 2025',2025,'2025-11-20','2025-11-22'),(306,'Research Project Recruitment',2025,'2025-09-01','2025-09-10'),(307,'Alumni Hiring Drive',2026,'2026-03-01','2026-03-10'),(308,'Core Engineering Fair',2026,'2026-01-15','2026-01-20'),(309,'Data Science Expo Recruitment',2025,'2025-11-25','2025-11-30'),(310,'Off-Campus Support Drive',2026,'2026-04-01','2026-05-30');
/*!40000 ALTER TABLE `placementdrive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `placementoffer`
--

DROP TABLE IF EXISTS `placementoffer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `placementoffer` (
  `OfferID` int NOT NULL,
  `AppID` int NOT NULL,
  `OfferDate` date NOT NULL,
  `FinalPackage` decimal(10,2) NOT NULL,
  `AcceptanceStatus` varchar(20) NOT NULL DEFAULT 'Pending',
  PRIMARY KEY (`OfferID`),
  KEY `AppID` (`AppID`),
  CONSTRAINT `placementoffer_ibfk_1` FOREIGN KEY (`AppID`) REFERENCES `application` (`AppID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `placementoffer`
--

LOCK TABLES `placementoffer` WRITE;
/*!40000 ALTER TABLE `placementoffer` DISABLE KEYS */;
INSERT INTO `placementoffer` VALUES (801,507,'2025-12-10',30.00,'Accepted'),(802,506,'2025-12-12',22.00,'Pending'),(803,501,'2025-12-10',32.00,'Accepted'),(804,516,'2025-12-05',12.00,'Rejected'),(805,524,'2026-01-20',6.50,'Accepted'),(806,511,'2025-12-06',24.00,'Accepted'),(807,518,'2025-12-11',30.00,'Pending'),(808,503,'2025-12-10',32.00,'Rejected'),(809,512,'2025-11-28',18.00,'Accepted'),(810,523,'2025-12-15',25.00,'Pending');
/*!40000 ALTER TABLE `placementoffer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recruiter`
--

DROP TABLE IF EXISTS `recruiter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recruiter` (
  `RecruiterID` int NOT NULL,
  `CompanyID` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Phone` varchar(15) NOT NULL,
  PRIMARY KEY (`RecruiterID`),
  UNIQUE KEY `Email` (`Email`),
  KEY `CompanyID` (`CompanyID`),
  CONSTRAINT `recruiter_ibfk_1` FOREIGN KEY (`CompanyID`) REFERENCES `company` (`CompanyID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recruiter`
--

LOCK TABLES `recruiter` WRITE;
/*!40000 ALTER TABLE `recruiter` DISABLE KEYS */;
INSERT INTO `recruiter` VALUES (201,1,'Sarah Jenkins','sarah.j@google.com','9876543210'),(202,2,'Rahul Verma','rahul.v@microsoft.com','9876543211'),(203,3,'Priya Sharma','priya.s@tcs.com','9876543212'),(204,5,'Amit Patel','amit.p@gs.com','9876543213'),(205,6,'Emily Davis','emily.d@amazon.com','9876543214'),(206,8,'Vikram Singh','vikram.s@flipkart.com','9876543215'),(207,10,'Neha Gupta','neha.g@adobe.com','9876543216'),(208,4,'Rohan Mehta','rohan.m@lntecc.com','9876543217'),(209,7,'Suresh Kumar','suresh.k@maruti.co.in','9876543218'),(210,9,'Anjali Nair','anjali.n@ril.com','9876543219'),(211,11,'David Wilson','david.w@ti.com','9876543220'),(212,12,'Kavita Roy','kavita.r@oracle.com','9876543221'),(213,13,'James Anderson','j.anderson@mckinsey.com','9876543222');
/*!40000 ALTER TABLE `recruiter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `skill`
--

DROP TABLE IF EXISTS `skill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `skill` (
  `SkillID` int NOT NULL,
  `SkillName` varchar(50) NOT NULL,
  `Category` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`SkillID`),
  UNIQUE KEY `SkillName` (`SkillName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `skill`
--

LOCK TABLES `skill` WRITE;
/*!40000 ALTER TABLE `skill` DISABLE KEYS */;
INSERT INTO `skill` VALUES (1,'Python','Technical'),(2,'Java','Technical'),(3,'SQL','Technical'),(4,'Machine Learning','Technical'),(5,'Communication','Soft Skill'),(6,'AutoCAD','Technical'),(7,'MATLAB','Technical'),(8,'ReactJS','Technical'),(9,'C++','Technical'),(10,'Project Management','Soft Skill'),(11,'Leadership','Soft Skill'),(12,'Data Structures','Technical'),(13,'AWS / Cloud','Technical'),(14,'Figma / UIUX','Design'),(15,'Public Speaking','Soft Skill');
/*!40000 ALTER TABLE `skill` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `studentskill`
--

DROP TABLE IF EXISTS `studentskill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `studentskill` (
  `ID` int NOT NULL,
  `MemberID` int NOT NULL,
  `SkillID` int NOT NULL,
  `ProficiencyLevel` varchar(20) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `MemberID` (`MemberID`),
  KEY `SkillID` (`SkillID`),
  CONSTRAINT `studentskill_ibfk_1` FOREIGN KEY (`MemberID`) REFERENCES `member` (`MemberID`) ON DELETE CASCADE,
  CONSTRAINT `studentskill_ibfk_2` FOREIGN KEY (`SkillID`) REFERENCES `skill` (`SkillID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `studentskill`
--

LOCK TABLES `studentskill` WRITE;
/*!40000 ALTER TABLE `studentskill` DISABLE KEYS */;
INSERT INTO `studentskill` VALUES (1,1001,1,'Expert'),(2,1001,3,'Intermediate'),(3,1001,12,'Expert'),(4,1002,2,'Expert'),(5,1002,13,'Intermediate'),(6,1003,7,'Advanced'),(7,1005,4,'Expert'),(8,1005,1,'Expert'),(9,1006,6,'Intermediate'),(10,1011,8,'Expert'),(11,1011,3,'Advanced'),(12,1015,1,'Intermediate'),(13,1009,3,'Expert'),(14,1009,13,'Advanced'),(15,1018,5,'Expert'),(16,1018,11,'Expert'),(17,1016,4,'Intermediate'),(18,1020,9,'Advanced'),(19,1020,7,'Expert'),(20,1017,8,'Intermediate'),(21,1012,10,'Intermediate'),(22,1008,15,'Advanced'),(23,1004,6,'Expert'),(24,1004,10,'Advanced'),(25,1019,5,'Intermediate');
/*!40000 ALTER TABLE `studentskill` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-14 16:50:24
