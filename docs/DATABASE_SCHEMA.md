cat > DATABASE_SCHEMA.md << 'EOF'
# 📘 Placement Preparation Platform  
## Production Database Schema Documentation

---

# 1. Overview

This document defines the production-level MySQL database schema for the Placement Preparation, Learning & Domain Mentorship Platform.

Design Goals:

- Scalable to 100k+ users
- Strict learning progression
- Subscription-based access
- Gamification & leaderboard ready
- Multi-tenant (college-based)
- Analytics-friendly

Database Engine: InnoDB  
Primary Key Type: BIGINT UNSIGNED AUTO_INCREMENT  

---

# 2. Users & Authentication

## 2.1 users

Stores all users.

| Column | Type | Constraints |
|--------|------|------------|
| id | BIGINT UNSIGNED | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NULL |
| mobile | VARCHAR(20) | NULL |
| role | ENUM('FREE','SUBSCRIBER','COLLEGE_ADMIN','SUPER_ADMIN') | NOT NULL |
| college_id | BIGINT UNSIGNED | FK → colleges.id |
| status | ENUM('ACTIVE','SUSPENDED','DELETED') | DEFAULT 'ACTIVE' |
| created_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NOT NULL |
| last_login | DATETIME | NULL |

---

## 2.2 colleges

| Column | Type |
|--------|------|
| id | BIGINT PK |
| name | VARCHAR(255) |
| code | VARCHAR(50) UNIQUE |
| agreement_type | ENUM('FREE','PAID','CUSTOM') |
| status | ENUM('ACTIVE','INACTIVE') |
| created_at | DATETIME |

---

## 2.3 user_stats

Stores aggregated gamification data.

| Column | Type |
|--------|------|
| user_id | BIGINT PK FK |
| total_points | INT DEFAULT 0 |
| total_stars | INT DEFAULT 0 |
| current_streak | INT DEFAULT 0 |
| last_active_date | DATE |

---

## 2.4 activity_logs

| Column | Type |
|--------|------|
| id | BIGINT PK |
| user_id | BIGINT FK |
| activity_type | VARCHAR(100) |
| reference_id | BIGINT |
| metadata | JSON |
| created_at | DATETIME |

---

# 3. Subscription System

## 3.1 subscription_plans

| Column | Type |
|--------|------|
| id | BIGINT PK |
| name | VARCHAR(100) |
| price | DECIMAL(10,2) |
| duration_days | INT |
| is_active | BOOLEAN |

---

## 3.2 user_subscriptions

| Column | Type |
|--------|------|
| id | BIGINT PK |
| user_id | BIGINT FK |
| plan_id | BIGINT FK |
| start_date | DATETIME |
| end_date | DATETIME |
| status | ENUM('ACTIVE','EXPIRED','CANCELLED') |

---

# 4. Content Structure

## 4.1 categories

| Column | Type |
|--------|------|
| id | BIGINT PK |
| name | VARCHAR(100) |
| type | ENUM('PROGRAMMING','APTITUDE','DOMAIN','COMPANY') |
| parent_id | BIGINT NULL |
| order_index | INT |

---

## 4.2 courses

| Column | Type |
|--------|------|
| id | BIGINT PK |
| category_id | BIGINT FK |
| title | VARCHAR(255) |
| description | TEXT |
| is_premium | BOOLEAN |
| status | ENUM('ACTIVE','INACTIVE') |

---

## 4.3 modules

| Column | Type |
|--------|------|
| id | BIGINT PK |
| course_id | BIGINT FK |
| title | VARCHAR(255) |
| order_index | INT |
| total_points | INT DEFAULT 10 |

---

## 4.4 topics

| Column | Type |
|--------|------|
| id | BIGINT PK |
| module_id | BIGINT FK |
| title | VARCHAR(255) |
| content | LONGTEXT |
| video_url | VARCHAR(500) |
| order_index | INT |

---

# 5. Learning Progress

## 5.1 topic_progress

| Column | Type |
|--------|------|
| id | BIGINT PK |
| user_id | BIGINT FK |
| topic_id | BIGINT FK |
| is_completed | BOOLEAN |
| completed_at | DATETIME |

UNIQUE(user_id, topic_id)

---

## 5.2 module_progress

| Column | Type |
|--------|------|
| id | BIGINT PK |
| user_id | BIGINT FK |
| module_id | BIGINT FK |
| is_completed | BOOLEAN |
| points_awarded | INT |
| completed_at | DATETIME |

UNIQUE(user_id, module_id)

---

# 6. Question Bank

## 6.1 questions

| Column | Type |
|--------|------|
| id | BIGINT PK |
| topic_id | BIGINT FK |
| type | ENUM('MCQ','MATCH') |
| question_text | TEXT |
| explanation | TEXT |
| difficulty | ENUM('EASY','MEDIUM','HARD') |
| status | ENUM('ACTIVE','INACTIVE') |

---

## 6.2 question_options

| Column | Type |
|--------|------|
| id | BIGINT PK |
| question_id | BIGINT FK |
| option_text | TEXT |
| is_correct | BOOLEAN |

---

# 7. Practice Engine

## 7.1 user_practice_attempts

| Column | Type |
|--------|------|
| id | BIGINT PK |
| user_id | BIGINT FK |
| question_id | BIGINT FK |
| selected_option_id | BIGINT FK |
| is_correct | BOOLEAN |
| notes | TEXT |
| marked_review | BOOLEAN |
| attempted_at | DATETIME |

UNIQUE(user_id, question_id)

---

# 8. Assignment Engine

## 8.1 tests

| Column | Type |
|--------|------|
| id | BIGINT PK |
| title | VARCHAR(255) |
| type | ENUM('TOPIC','FULL_LENGTH','MOCK') |
| max_score | INT |
| status | ENUM('ACTIVE','INACTIVE') |

---

## 8.2 test_questions

| Column | Type |
|--------|------|
| id | BIGINT PK |
| test_id | BIGINT FK |
| question_id | BIGINT FK |

---

## 8.3 test_attempts

| Column | Type |
|--------|------|
| id | BIGINT PK |
| user_id | BIGINT FK |
| test_id | BIGINT FK |
| score | INT |
| is_submitted | BOOLEAN |
| submitted_at | DATETIME |

UNIQUE(user_id, test_id)

---

# 9. Coding Engine

## 9.1 coding_problems

| Column | Type |
|--------|------|
| id | BIGINT PK |
| language | VARCHAR(50) |
| title | VARCHAR(255) |
| description | LONGTEXT |
| difficulty | ENUM('EASY','MEDIUM','HARD') |
| points | INT |
| status | ENUM('ACTIVE','INACTIVE') |

---

## 9.2 coding_test_cases

| Column | Type |
|--------|------|
| id | BIGINT PK |
| problem_id | BIGINT FK |
| input_data | TEXT |
| expected_output | TEXT |
| is_sample | BOOLEAN |

---

## 9.3 coding_submissions

| Column | Type |
|--------|------|
| id | BIGINT PK |
| user_id | BIGINT FK |
| problem_id | BIGINT FK |
| code | LONGTEXT |
| status | ENUM('PASSED','FAILED') |
| points_awarded | INT |
| submitted_at | DATETIME |

---

# 10. Domain System

## 10.1 domains

| Column | Type |
|--------|------|
| id | BIGINT PK |
| name | VARCHAR(255) |
| description | TEXT |

---

## 10.2 domain_courses

| Column | Type |
|--------|------|
| id | BIGINT PK |
| domain_id | BIGINT FK |
| course_id | BIGINT FK |
| order_index | INT |

---

# 11. Indexing Strategy

Create indexes on:

- user_id
- course_id
- module_id
- topic_id
- question_id
- test_id
- problem_id

Composite indexes:

- (user_id, question_id)
- (user_id, test_id)
- (user_id, problem_id)

---

# 12. Production Guidelines

- Use transactions for module completion & test submission
- Do NOT store derived percentages
- Maintain user_stats for fast leaderboard
- Keep activity_logs for future analytics
- Use BIGINT for scalability

---

# 13. Core Table Count

Users & Auth: 4  
Subscription: 2  
Content: 4  
Progress: 2  
Questions: 2  
Practice: 1  
Assignments: 3  
Coding: 3  
Domain: 2  

Total Core Tables: 23  
Expandable to 25+ with payments, badges, notifications.


---

# 14. Table Explanations & Example Data

---

## users

### Purpose
Stores all platform users including learners, college admins, and super admins.

### Example Data

| id | email | first_name | role | college_id | status |
|----|--------|------------|------|------------|--------|
| 1 | eswar@gmail.com | Eswar | SUBSCRIBER | 2 | ACTIVE |
| 2 | admin@abc.edu | Priya | COLLEGE_ADMIN | 2 | ACTIVE |

---

## colleges

### Purpose
Stores partner college details for multi-tenant support.

### Example Data

| id | name | code | agreement_type | status |
|----|------|------|----------------|--------|
| 2 | ABC Engineering College | ABC2026 | PAID | ACTIVE |

---

## user_stats

### Purpose
Stores aggregated gamification stats for leaderboard performance.

### Example Data

| user_id | total_points | total_stars | current_streak |
|----------|--------------|-------------|----------------|
| 1 | 850 | 3 | 7 |

---

## activity_logs

### Purpose
Stores user activity events for analytics & audit trail.

### Example Data

| id | user_id | activity_type | reference_id | created_at |
|----|----------|---------------|--------------|------------|
| 101 | 1 | MODULE_COMPLETED | 12 | 2026-02-28 10:30:00 |

---

## subscription_plans

### Purpose
Defines available subscription plans.

### Example Data

| id | name | price | duration_days |
|----|------|--------|---------------|
| 1 | Premium Plan | 2999.00 | 365 |

---

## user_subscriptions

### Purpose
Tracks user subscription history.

### Example Data

| id | user_id | plan_id | start_date | end_date | status |
|----|----------|----------|------------|------------|--------|
| 1 | 1 | 1 | 2026-01-01 | 2026-12-31 | ACTIVE |

---

## categories

### Purpose
Hierarchical grouping of content.

### Example Data

| id | name | type |
|----|------|------|
| 1 | Programming | PROGRAMMING |
| 2 | Aptitude | APTITUDE |

---

## courses

### Purpose
Represents individual learning courses.

### Example Data

| id | title | category_id | is_premium |
|----|--------|--------------|------------|
| 10 | Python Basics | 1 | TRUE |

---

## modules

### Purpose
Course divided into ordered modules.

### Example Data

| id | title | course_id | order_index |
|----|--------|-----------|------------|
| 101 | Introduction to Python | 10 | 1 |

---

## topics

### Purpose
Individual learning topics inside modules.

### Example Data

| id | title | module_id | order_index |
|----|--------|------------|------------|
| 1001 | Variables and Data Types | 101 | 1 |

---

## topic_progress

### Purpose
Tracks user completion of topics.

### Example Data

| id | user_id | topic_id | is_completed |
|----|----------|----------|--------------|
| 1 | 1 | 1001 | TRUE |

---

## module_progress

### Purpose
Tracks module completion and awarded points.

### Example Data

| id | user_id | module_id | is_completed | points_awarded |
|----|----------|-----------|--------------|----------------|
| 1 | 1 | 101 | TRUE | 10 |

---

## questions

### Purpose
Stores MCQ or matching questions.

### Example Data

| id | topic_id | difficulty | status |
|----|----------|------------|--------|
| 5001 | 1001 | EASY | ACTIVE |

---

## question_options

### Purpose
Stores answer options for MCQs.

### Example Data

| id | question_id | option_text | is_correct |
|----|--------------|------------|------------|
| 1 | 5001 | int | TRUE |
| 2 | 5001 | string | FALSE |

---

## user_practice_attempts

### Purpose
Tracks practice attempts (no final submission).

### Example Data

| id | user_id | question_id | is_correct |
|----|----------|-------------|------------|
| 1 | 1 | 5001 | TRUE |

---

## tests

### Purpose
Defines assignment or full-length tests.

### Example Data

| id | title | type | max_score |
|----|--------|------|-----------|
| 1 | Python Module Test | TOPIC | 20 |

---

## test_questions

### Purpose
Maps questions to tests.

### Example Data

| id | test_id | question_id |
|----|----------|-------------|
| 1 | 1 | 5001 |

---

## test_attempts

### Purpose
Tracks one-time test submissions.

### Example Data

| id | user_id | test_id | score | is_submitted |
|----|----------|----------|--------|--------------|
| 1 | 1 | 1 | 18 | TRUE |

---

## coding_problems

### Purpose
Stores coding challenges.

### Example Data

| id | title | difficulty | points |
|----|--------|------------|--------|
| 1 | Reverse String | EASY | 5 |

---

## coding_test_cases

### Purpose
Stores input-output validation cases.

### Example Data

| id | problem_id | is_sample |
|----|------------|------------|
| 1 | 1 | TRUE |

---

## coding_submissions

### Purpose
Stores user code submissions.

### Example Data

| id | user_id | problem_id | status | points_awarded |
|----|----------|------------|--------|----------------|
| 1 | 1 | 1 | PASSED | 5 |

---

## domains

### Purpose
Represents domain mentorship paths.

### Example Data

| id | name |
|----|------|
| 1 | Data Science |

---

## domain_courses

### Purpose
Maps courses to domains in strict order.

### Example Data

| id | domain_id | course_id | order_index |
|----|------------|------------|------------|
| 1 | 1 | 10 | 1 |

---

EOF