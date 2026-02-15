# CareerTrack - Placement Management System 

A robust, database-driven software solution designed to automate and manage the college placement process efficiently. Developed as part of the CS432 Databases course at IIT Gandhinagar.

## 📌 Project Overview
Many institutions handle placement activities manually, leading to data duplication, delayed communication, and inconsistent records. CareerTrack provides a centralized platform to manage student details, track company job postings, and seamlessly process job applications.

## 🎯 Core Objectives
* Create a centralized relational database for placement management.
* Automate the job application and selection tracking process.
* Ensure data consistency and reduce manual record-keeping errors.
* Manage detailed profiles for students, recruiting companies, and job roles.

## 🏗️ System Architecture
The project is conceptually designed around a Three-Tier Architecture:
1. **Presentation Layer:** The user interface for students, companies, and placement officers.
2. **Application Layer:** Handles business logic, eligibility checks, and input validation. 
3. **Database Layer:** The core relational schema ensuring secure data storage and integrity.

## 🗄️ Database Design & Integrity
The database strictly adheres to the following constraints and normalization rules:
* **Schema:** Contains 12 normalized tables (1NF, 2NF, 3NF) eliminating redundancy.
* **Entity Relationships:** Modeled using strict Silberschatz/Chen ER notation, correctly handling 1:1, 1:M, and M:N cardinalities.
* **Data Integrity:** Enforced via Primary Keys, Foreign Keys, Unique constraints, and NOT NULL constraints.
* **Referential Integrity:** Enforced cascaded updates/deletions to prevent orphaned records (e.g., restricting company deletion if active jobs exist).

## 📊 Entity-Relationship Diagram
*(Upload the ER Diagram PNG to a `Diagrams` folder in this repo, then the image will appear here!)*
![ER Diagram](./Diagrams/ER_Diagram.png)

## 🚀 Quick Start (Running the Database)
1. Clone this repository to your local machine.
2. Open **MySQL Workbench** (or your preferred SQL client).
3. Import the `database.sql` file.
4. Execute the script to automatically generate the schema, apply constraints, and populate the tables with sample synthetic data.

## 👨‍💻 Team Members & Contributions
* **Bhavitha Somireddy (24110350):** Conceptual design, entity/attribute analysis, and relationship justification.
* **Killada Eswara Valli (24110165):** ER structure mapping and cardinality verification.
* **Garv Singhal (24110119):** ER diagram design using standard notation and key mappings.
* **Pramith Joy (23110152):** Database implementation, logical constraints, and referential integrity.
* **Divyansh Saini (23110101):** Data validation, query testing, SQL dump generation, and final submission packaging.

---
*Developed for CS432 Semester II (2025-2026).*
