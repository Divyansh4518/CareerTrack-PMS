# CareerTrack - Placement Management System 🎓💼

[cite_start]A robust, database-driven software solution designed to automate and manage the college placement process efficiently[cite: 502]. Developed as part of the CS432 Databases course at IIT Gandhinagar.

## 📌 Project Overview
[cite_start]Many institutions handle placement activities manually, leading to data duplication, delayed communication, and inconsistent records [cite: 503-508]. [cite_start]CareerTrack provides a centralized platform to manage student details, track company job postings, and seamlessly process job applications [cite: 509-515]. 

## 🎯 Core Objectives
* [cite_start]Create a centralized relational database for placement management[cite: 521].
* [cite_start]Automate the job application and selection tracking process [cite: 522-523].
* [cite_start]Ensure data consistency and reduce manual record-keeping errors [cite: 525-526].
* [cite_start]Manage detailed profiles for students, recruiting companies, and job roles[cite: 524].

## 🏗️ System Architecture
[cite_start]The project is conceptually designed around a Three-Tier Architecture[cite: 552]:
1. [cite_start]**Presentation Layer:** The user interface for students, companies, and placement officers [cite: 553-554].
2. [cite_start]**Application Layer:** Handles business logic, eligibility checks, and input validation [cite: 561-565]. 
3. [cite_start]**Database Layer:** The core relational schema ensuring secure data storage and integrity [cite: 571-574].

## 🗄️ Database Design & Integrity
The database strictly adheres to the following constraints and normalization rules:
* [cite_start]**Schema:** Contains 12 normalized tables (1NF, 2NF, 3NF) eliminating redundancy [cite: 709-711].
* [cite_start]**Entity Relationships:** Modeled using strict Silberschatz/Chen ER notation, correctly handling 1:1, 1:M, and M:N cardinalities [cite: 800-803].
* [cite_start]**Data Integrity:** Enforced via Primary Keys, Foreign Keys, Unique constraints, and NOT NULL constraints [cite: 692-705].
* [cite_start]**Referential Integrity:** Enforced cascaded updates/deletions to prevent orphaned records (e.g., restricting company deletion if active jobs exist) [cite: 706-708].

## 📊 Entity-Relationship Diagram
*(Upload the ER Diagram PNG to a `Diagrams` folder in this repo, then the image will appear here!)*
![ER Diagram](./Diagrams/ER_Diagram.png)

## 🚀 Quick Start (Running the Database)
1. Clone this repository to your local machine.
2. Open **MySQL Workbench** (or your preferred SQL client).
3. Import the `CareerTrack_Dump.sql` file.
4. Execute the script to automatically generate the schema, apply constraints, and populate the tables with sample synthetic data.

## 👨‍💻 Team Members & Contributions
* [cite_start]**Bhavitha Somireddy (24110350):** Conceptual design, entity/attribute analysis, and relationship justification [cite: 1156-1161].
* [cite_start]**Killada Eswara Valli (24110165):** ER structure mapping and cardinality verification [cite: 1162-1167].
* [cite_start]**Garv Singhal (24110119):** ER diagram design using standard notation and key mappings [cite: 1168-1172].
* [cite_start]**Pramith Joy (23110152):** Database implementation, logical constraints, and referential integrity [cite: 1173-1178].
* [cite_start]**Divyansh Saini (23110101):** Data validation, query testing, SQL dump generation, and final submission packaging [cite: 1179-1184].

---
*Developed for CS432 Semester II (2025-2026).*
