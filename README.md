# Quiz Master - V1

## Overview

Quiz Master is a multi-user application designed as an exam preparation site for multiple courses. It supports two roles: Admin and User. The Admin manages the application, while Users can register, log in, and attempt quizzes.

## Setup

- **Create Virtual ENV**: python3 -m venv venv
- **Enter into existing virtual ENV**: .\venv\Scripts\activate
- **Install required dependency**: pip install -r requirements.txt
- **Run the application locally**: python app.py

## Frameworks Used

- **Backend**: Flask
- **Frontend**: Jinja2 templating, HTML, CSS, Bootstrap
- **Database**: SQLite

## Roles and Responsibilities

### Admin

- Root access with no registration required
- Manages users, subjects, chapters, and quizzes
- Creates subjects and chapters
- Adds quiz questions under chapters
- Admin dashboard for management tasks

### User

- Registers and logs in
- Attempts quizzes
- Views quiz scores
- User dashboard for quiz attempts and scores

## Data Models

### User

- `id`: VARCHAR(100), Primary key
- `email`: VARCHAR(100), Unique, Not null
- `password`: VARCHAR(100), Not null
- `full_name`: VARCHAR(100), Not null
- `qualification`: VARCHAR(100), Not null
- `dob`: DATE, Not null
- `isActive`: Boolean, Default True, Not null
- `user_type`: Enum('admin', 'user'), Not null
- `created_at`: TIMESTAMP, Not null
- `updated_at`: TIMESTAMP, Not null

### Subject

- `id`: VARCHAR(100), Primary key
- `name`: VARCHAR(100), Not null
- `description`: VARCHAR(100), Not null
- `created_at`: TIMESTAMP, Not null
- `updated_at`: TIMESTAMP, Not null
- `code`: VARCHAR(100), Not null

### Chapter

- `id`: VARCHAR(100), Primary key
- `name`: VARCHAR(100), Not null
- `description`: VARCHAR(100), Not null
- `subject_id`: VARCHAR(100), Foreign key to Subject, Not null
- `created_at`: TIMESTAMP, Not null
- `updated_at`: TIMESTAMP, Not null
- `chapter_number`: Integer, Not null
- `code`: VARCHAR(100), Not null
- `pages`: Integer, Not null

### Quiz

- `id`: VARCHAR(100), Primary key
- `quiz_title`: VARCHAR(100), Not null
- `chapter_id`: VARCHAR(100), Foreign key to Chapter, Not null
- `chapter_code`: VARCHAR(100), Foreign key to Chapter, Not null
- `date_of_quiz`: DATE, Not null
- `time_duration_hr`: Integer, Not null
- `time_duration_min`: Integer, Not null
- `remarks`: VARCHAR(100), Not null
- `created_at`: TIMESTAMP, Not null
- `updated_at`: TIMESTAMP, Not null
- `is_active`: Boolean, Default True, Not null
- `user_id`: VARCHAR(100), Foreign key to User, Nullable
- `total_marks`: Integer, Not null

### Question

- `id`: VARCHAR(100), Primary key
- `quiz_id`: VARCHAR(100), Foreign key to Quiz, Not null
- `question_title`: VARCHAR(100), Not null
- `question_statement`: VARCHAR(100), Not null
- `chapter_id`: VARCHAR(100), Foreign key to Chapter, Not null
- `chapter_code`: VARCHAR(100), Foreign key to Chapter, Not null
- `option_1`: VARCHAR(100), Not null
- `option_2`: VARCHAR(100), Not null
- `option_3`: VARCHAR(100), Not null
- `option_4`: VARCHAR(100), Not null
- `created_at`: TIMESTAMP, Not null
- `updated_at`: TIMESTAMP, Not null
- `correct_option`: Integer, Not null
- `marks`: Integer, Not null

### Score

- `id`: VARCHAR(100), Primary key
- `quiz_id`: VARCHAR(100), Foreign key to Quiz, Not null
- `user_id`: VARCHAR(100), Foreign key to User, Not null
- `question_attempted`: Integer, Not null
- `question_corrected`: Integer, Not null
- `question_wronged`: Integer, Not null
- `total_scored`: Integer, Not null
- `created_at`: TIMESTAMP, Not null
- `updated_at`: TIMESTAMP, Not null
- `unique_user_quiz_score`: Unique constraint on `quiz_id` and `user_id`

### Attempt

- `id`: VARCHAR(100), Primary key
- `quiz_id`: VARCHAR(100), Foreign key to Quiz, Not null
- `user_id`: VARCHAR(100), Foreign key to User, Not null
- `score_id`: VARCHAR(100), Foreign key to Score, Not null
- `question_id`: VARCHAR(100), Foreign key to Question, Not null
- `actual_answer`: Integer, Not null
- `attempted_answer`: Integer, Not null
- `created_at`: TIMESTAMP, Not null
- `updated_at`: TIMESTAMP, Not null
- `unique_user_quiz_question_attempt`: Unique constraint on `quiz_id`, `user_id`, and `question_id`

## Core Functionalities

### Admin

- Admin login
- Create, edit, delete subjects and chapters
- Create, edit, delete quizzes and questions
- Search users, subjects, quizzes
- View summary charts

### User

- User registration and login
- Attempt quizzes with a timer
- View quiz scores and history
- View summary charts
