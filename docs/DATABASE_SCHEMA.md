# 📘 Fynity — Placement Preparation Platform
## Production MySQL Database Schema (Corrected & Complete)

---

# 1. Overview

**Database Engine:** MySQL 8.0+ InnoDB  
**Primary Key Type:** BIGINT UNSIGNED AUTO_INCREMENT  
**Character Set:** utf8mb4  
**Collation:** utf8mb4_unicode_ci  

**Design Goals:**
- Scalable to 100k+ users
- Strict learning progression (locked modules)
- Subscription-based access control
- Gamification & leaderboard ready
- Multi-tenant (college-based)
- Analytics-friendly
- Razorpay payment integration

**Total Tables: 35**

---

# 2. Users & Authentication

## 2.1 `users`

Stores all platform users.

```sql
CREATE TABLE users (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    first_name      VARCHAR(100)    NOT NULL,
    last_name       VARCHAR(100)    NULL,
    mobile          VARCHAR(20)     NULL,
    role            ENUM('FREE','SUBSCRIBER','COLLEGE_ADMIN','SUPER_ADMIN') NOT NULL DEFAULT 'FREE',
    college_id      BIGINT UNSIGNED NULL,
    status          ENUM('ACTIVE','SUSPENDED','DELETED') NOT NULL DEFAULT 'ACTIVE',
    email_verified  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login      DATETIME        NULL,

    CONSTRAINT fk_users_college FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL,
    INDEX idx_users_role (role),
    INDEX idx_users_college (college_id),
    INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 2.2 `colleges`

Partner college details for multi-tenant support.

```sql
CREATE TABLE colleges (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(255)    NOT NULL,
    code            VARCHAR(50)     NOT NULL UNIQUE,
    agreement_type  ENUM('FREE','PAID','CUSTOM') NOT NULL DEFAULT 'PAID',
    status          ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 2.3 `student_profiles`

Stores college-student-specific registration details (branch, year, CGPA, etc.).

```sql
CREATE TABLE student_profiles (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL UNIQUE,
    college_id      BIGINT UNSIGNED NOT NULL,
    branch          VARCHAR(150)    NOT NULL,
    current_year    TINYINT UNSIGNED NOT NULL COMMENT '1 to 4',
    semester        TINYINT UNSIGNED NOT NULL COMMENT '1 to 8',
    cgpa            DECIMAL(4,2)    NULL,
    roll_number     VARCHAR(50)     NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sp_user    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    CONSTRAINT fk_sp_college FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 2.4 `user_stats`

Aggregated gamification data per user. Updated via triggers or application logic.

```sql
CREATE TABLE user_stats (
    user_id             BIGINT UNSIGNED PRIMARY KEY,
    total_points        INT UNSIGNED    NOT NULL DEFAULT 0,
    total_stars         TINYINT UNSIGNED NOT NULL DEFAULT 0,
    total_badges        TINYINT UNSIGNED NOT NULL DEFAULT 0,
    current_streak      INT UNSIGNED    NOT NULL DEFAULT 0,
    longest_streak      INT UNSIGNED    NOT NULL DEFAULT 0,
    last_active_date    DATE            NULL,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_ustats_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 2.5 `activity_logs`

Audit trail for all major user events. Used for analytics.

```sql
CREATE TABLE activity_logs (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    activity_type   VARCHAR(100)    NOT NULL COMMENT 'e.g. MODULE_COMPLETED, TEST_SUBMITTED, CODING_SOLVED',
    reference_id    BIGINT UNSIGNED NULL     COMMENT 'ID of the related entity',
    metadata        JSON            NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_actlog_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_actlog_user (user_id),
    INDEX idx_actlog_type (activity_type),
    INDEX idx_actlog_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 3. Subscription & Payments

## 3.1 `subscription_plans`

Defines available plans (e.g. Basic, Domain Bundle, Full Premium).

```sql
CREATE TABLE subscription_plans (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    description     TEXT            NULL,
    price           DECIMAL(10,2)   NOT NULL,
    duration_days   INT UNSIGNED    NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 3.2 `plan_access_rules`

Maps which subscription plans unlock which content categories/domains.

```sql
CREATE TABLE plan_access_rules (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    plan_id         BIGINT UNSIGNED NOT NULL,
    access_type     ENUM('CATEGORY','DOMAIN','ALL') NOT NULL DEFAULT 'ALL',
    reference_id    BIGINT UNSIGNED NULL COMMENT 'category_id or domain_id when access_type is not ALL',

    CONSTRAINT fk_par_plan FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE CASCADE,
    INDEX idx_par_plan (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 3.3 `user_subscriptions`

Tracks a user's active and historical subscriptions.

```sql
CREATE TABLE user_subscriptions (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    plan_id         BIGINT UNSIGNED NOT NULL,
    payment_id      BIGINT UNSIGNED NULL,
    start_date      DATETIME        NOT NULL,
    end_date        DATETIME        NOT NULL,
    status          ENUM('ACTIVE','EXPIRED','CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_usub_user    FOREIGN KEY (user_id)    REFERENCES users(id)               ON DELETE CASCADE,
    CONSTRAINT fk_usub_plan    FOREIGN KEY (plan_id)    REFERENCES subscription_plans(id)  ON DELETE RESTRICT,
    CONSTRAINT fk_usub_payment FOREIGN KEY (payment_id) REFERENCES payments(id)            ON DELETE SET NULL,
    INDEX idx_usub_user   (user_id),
    INDEX idx_usub_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 3.4 `payments`

Razorpay payment records.

```sql
CREATE TABLE payments (
    id                      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id                 BIGINT UNSIGNED NOT NULL,
    plan_id                 BIGINT UNSIGNED NOT NULL,
    razorpay_order_id       VARCHAR(100)    NOT NULL UNIQUE,
    razorpay_payment_id     VARCHAR(100)    NULL UNIQUE,
    razorpay_signature      VARCHAR(255)    NULL,
    amount                  DECIMAL(10,2)   NOT NULL,
    currency                VARCHAR(10)     NOT NULL DEFAULT 'INR',
    status                  ENUM('CREATED','PAID','FAILED','REFUNDED') NOT NULL DEFAULT 'CREATED',
    created_at              DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_pay_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT fk_pay_plan FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE RESTRICT,
    INDEX idx_pay_user   (user_id),
    INDEX idx_pay_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 4. Content Structure

## 4.1 `categories`

Top-level grouping for all content: Programming, Aptitude, Company, Domain.

```sql
CREATE TABLE categories (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    type            ENUM('PROGRAMMING','APTITUDE','DOMAIN','COMPANY') NOT NULL,
    parent_id       BIGINT UNSIGNED NULL,
    order_index     INT UNSIGNED    NOT NULL DEFAULT 0,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_cat_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_cat_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 4.2 `courses`

Individual learning courses (e.g. Python, SQL, Quantitative Aptitude).

```sql
CREATE TABLE courses (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_id     BIGINT UNSIGNED NOT NULL,
    title           VARCHAR(255)    NOT NULL,
    description     TEXT            NULL,
    thumbnail_url   VARCHAR(500)    NULL,
    is_premium      BOOLEAN         NOT NULL DEFAULT TRUE,
    status          ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_course_cat FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_course_cat (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 4.3 `modules`

Ordered modules inside a course. Each carries 10 points on completion.

```sql
CREATE TABLE modules (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    course_id       BIGINT UNSIGNED NOT NULL,
    title           VARCHAR(255)    NOT NULL,
    order_index     INT UNSIGNED    NOT NULL DEFAULT 0,
    total_points    INT UNSIGNED    NOT NULL DEFAULT 10,

    CONSTRAINT fk_mod_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_mod_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 4.4 `topics`

Individual learning topics inside a module.

```sql
CREATE TABLE topics (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    module_id       BIGINT UNSIGNED NOT NULL,
    title           VARCHAR(255)    NOT NULL,
    content         LONGTEXT        NULL,
    video_url       VARCHAR(500)    NULL,
    order_index     INT UNSIGNED    NOT NULL DEFAULT 0,

    CONSTRAINT fk_topic_mod FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    INDEX idx_topic_mod (module_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 5. Learning Progress

## 5.1 `topic_progress`

Tracks which topics a user has completed.

```sql
CREATE TABLE topic_progress (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    topic_id        BIGINT UNSIGNED NOT NULL,
    is_completed    BOOLEAN         NOT NULL DEFAULT FALSE,
    completed_at    DATETIME        NULL,

    UNIQUE KEY uq_tp_user_topic (user_id, topic_id),
    CONSTRAINT fk_tp_user  FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    CONSTRAINT fk_tp_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    INDEX idx_tp_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 5.2 `module_progress`

Tracks module completion. Points awarded only after all topics + mini test are done.

```sql
CREATE TABLE module_progress (
    id                      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id                 BIGINT UNSIGNED NOT NULL,
    module_id               BIGINT UNSIGNED NOT NULL,
    topics_completed        INT UNSIGNED    NOT NULL DEFAULT 0,
    mini_test_submitted     BOOLEAN         NOT NULL DEFAULT FALSE,
    is_completed            BOOLEAN         NOT NULL DEFAULT FALSE,
    points_awarded          INT UNSIGNED    NOT NULL DEFAULT 0,
    completed_at            DATETIME        NULL,

    UNIQUE KEY uq_mp_user_module (user_id, module_id),
    CONSTRAINT fk_mp_user   FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    CONSTRAINT fk_mp_module FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    INDEX idx_mp_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 5.3 `course_completions`

Records when a user finishes all modules in a course and earns a Star.

```sql
CREATE TABLE course_completions (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    course_id       BIGINT UNSIGNED NOT NULL,
    star_awarded    BOOLEAN         NOT NULL DEFAULT TRUE,
    completed_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_cc_user_course (user_id, course_id),
    CONSTRAINT fk_cc_user   FOREIGN KEY (user_id)   REFERENCES users(id)    ON DELETE CASCADE,
    CONSTRAINT fk_cc_course FOREIGN KEY (course_id) REFERENCES courses(id)  ON DELETE CASCADE,
    INDEX idx_cc_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 6. Question Bank

## 6.1 `questions`

MCQ or matching questions linked to a topic.

```sql
CREATE TABLE questions (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    topic_id        BIGINT UNSIGNED NOT NULL,
    type            ENUM('MCQ','MATCH') NOT NULL DEFAULT 'MCQ',
    question_text   TEXT            NOT NULL,
    explanation     TEXT            NULL,
    difficulty      ENUM('EASY','MEDIUM','HARD') NOT NULL DEFAULT 'EASY',
    status          ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_q_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    INDEX idx_q_topic      (topic_id),
    INDEX idx_q_difficulty (difficulty),
    INDEX idx_q_status     (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 6.2 `question_options`

Answer options for MCQ questions.

```sql
CREATE TABLE question_options (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    question_id     BIGINT UNSIGNED NOT NULL,
    option_text     TEXT            NOT NULL,
    is_correct      BOOLEAN         NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_qopt_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_qopt_question (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 7. Practice MCQ Engine

## 7.1 `user_practice_attempts`

Tracks per-question practice attempts. Allows re-attempts (no UNIQUE on user+question).  
Latest attempt per question is the canonical state.

```sql
CREATE TABLE user_practice_attempts (
    id                  BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id             BIGINT UNSIGNED NOT NULL,
    question_id         BIGINT UNSIGNED NOT NULL,
    selected_option_id  BIGINT UNSIGNED NULL,
    is_correct          BOOLEAN         NULL,
    notes               TEXT            NULL,
    marked_review       BOOLEAN         NOT NULL DEFAULT FALSE,
    is_submitted        BOOLEAN         NOT NULL DEFAULT FALSE,
    attempted_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_upa_user     FOREIGN KEY (user_id)            REFERENCES users(id)            ON DELETE CASCADE,
    CONSTRAINT fk_upa_question FOREIGN KEY (question_id)        REFERENCES questions(id)        ON DELETE CASCADE,
    CONSTRAINT fk_upa_option   FOREIGN KEY (selected_option_id) REFERENCES question_options(id) ON DELETE SET NULL,
    INDEX idx_upa_user     (user_id),
    INDEX idx_upa_question (question_id),
    INDEX idx_upa_user_q   (user_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

> **Note:** No UNIQUE constraint here — practice is repeatable. Application upserts on `(user_id, question_id)` to update the latest state.

---

# 8. Assignment / Test Engine

## 8.1 `tests`

Defines all tests: topic-wise, full-length, mock, and end-of-module mini tests.

```sql
CREATE TABLE tests (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    module_id       BIGINT UNSIGNED NULL    COMMENT 'Set for MODULE_MINI tests only',
    title           VARCHAR(255)    NOT NULL,
    type            ENUM('TOPIC','FULL_LENGTH','MOCK','MODULE_MINI') NOT NULL,
    max_score       INT UNSIGNED    NOT NULL DEFAULT 0,
    duration_mins   INT UNSIGNED    NULL     COMMENT 'NULL = no time limit',
    status          ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_test_module FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL,
    INDEX idx_test_type   (type),
    INDEX idx_test_module (module_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 8.2 `test_questions`

Maps questions to tests.

```sql
CREATE TABLE test_questions (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    test_id         BIGINT UNSIGNED NOT NULL,
    question_id     BIGINT UNSIGNED NOT NULL,
    order_index     INT UNSIGNED    NOT NULL DEFAULT 0,

    UNIQUE KEY uq_tq_test_question (test_id, question_id),
    CONSTRAINT fk_tq_test     FOREIGN KEY (test_id)     REFERENCES tests(id)     ON DELETE CASCADE,
    CONSTRAINT fk_tq_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 8.3 `test_attempts`

One valid submission per test per user. Interrupted tests are discarded.

```sql
CREATE TABLE test_attempts (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    test_id         BIGINT UNSIGNED NOT NULL,
    score           INT UNSIGNED    NOT NULL DEFAULT 0,
    total_correct   INT UNSIGNED    NOT NULL DEFAULT 0,
    is_submitted    BOOLEAN         NOT NULL DEFAULT FALSE,
    started_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submitted_at    DATETIME        NULL,

    UNIQUE KEY uq_ta_user_test (user_id, test_id),
    CONSTRAINT fk_ta_user FOREIGN KEY (user_id) REFERENCES users(id)  ON DELETE CASCADE,
    CONSTRAINT fk_ta_test FOREIGN KEY (test_id) REFERENCES tests(id)  ON DELETE CASCADE,
    INDEX idx_ta_user (user_id),
    INDEX idx_ta_test (test_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 8.4 `test_answer_snapshots`

Stores user's selected answers on a submitted test (for review mode).

```sql
CREATE TABLE test_answer_snapshots (
    id                  BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    attempt_id          BIGINT UNSIGNED NOT NULL,
    question_id         BIGINT UNSIGNED NOT NULL,
    selected_option_id  BIGINT UNSIGNED NULL,
    is_correct          BOOLEAN         NULL,

    CONSTRAINT fk_tas_attempt  FOREIGN KEY (attempt_id)         REFERENCES test_attempts(id)    ON DELETE CASCADE,
    CONSTRAINT fk_tas_question FOREIGN KEY (question_id)        REFERENCES questions(id)        ON DELETE CASCADE,
    CONSTRAINT fk_tas_option   FOREIGN KEY (selected_option_id) REFERENCES question_options(id) ON DELETE SET NULL,
    INDEX idx_tas_attempt (attempt_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 9. Coding Engine

## 9.1 `coding_problems`

Coding challenges organized by language and difficulty.

```sql
CREATE TABLE coding_problems (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    language        VARCHAR(50)     NOT NULL COMMENT 'e.g. Python, Java, SQL',
    title           VARCHAR(255)    NOT NULL,
    description     LONGTEXT        NOT NULL,
    constraints_txt TEXT            NULL,
    difficulty      ENUM('EASY','MEDIUM','HARD') NOT NULL,
    points          INT UNSIGNED    NOT NULL DEFAULT 5,
    status          ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_cp_language   (language),
    INDEX idx_cp_difficulty (difficulty)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 9.2 `coding_test_cases`

Input/output validation cases per problem.

```sql
CREATE TABLE coding_test_cases (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    problem_id      BIGINT UNSIGNED NOT NULL,
    input_data      TEXT            NOT NULL,
    expected_output TEXT            NOT NULL,
    is_sample       BOOLEAN         NOT NULL DEFAULT FALSE COMMENT 'Shown to learner on problem page',

    CONSTRAINT fk_ctc_problem FOREIGN KEY (problem_id) REFERENCES coding_problems(id) ON DELETE CASCADE,
    INDEX idx_ctc_problem (problem_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 9.3 `user_coding_progress`

Canonical completion state per user per problem. Prevents double point-awarding on re-submission.

```sql
CREATE TABLE user_coding_progress (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    problem_id      BIGINT UNSIGNED NOT NULL,
    is_completed    BOOLEAN         NOT NULL DEFAULT FALSE,
    points_awarded  INT UNSIGNED    NOT NULL DEFAULT 0,
    marked_review   BOOLEAN         NOT NULL DEFAULT FALSE,
    first_solved_at DATETIME        NULL,

    UNIQUE KEY uq_ucp_user_problem (user_id, problem_id),
    CONSTRAINT fk_ucp_user    FOREIGN KEY (user_id)    REFERENCES users(id)            ON DELETE CASCADE,
    CONSTRAINT fk_ucp_problem FOREIGN KEY (problem_id) REFERENCES coding_problems(id)  ON DELETE CASCADE,
    INDEX idx_ucp_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 9.4 `coding_submissions`

Full log of all code submissions (run history).

```sql
CREATE TABLE coding_submissions (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    problem_id      BIGINT UNSIGNED NOT NULL,
    code            LONGTEXT        NOT NULL,
    language        VARCHAR(50)     NOT NULL,
    status          ENUM('PASSED','FAILED','ERROR') NOT NULL,
    submitted_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cs_user    FOREIGN KEY (user_id)    REFERENCES users(id)           ON DELETE CASCADE,
    CONSTRAINT fk_cs_problem FOREIGN KEY (problem_id) REFERENCES coding_problems(id) ON DELETE CASCADE,
    INDEX idx_cs_user    (user_id),
    INDEX idx_cs_problem (problem_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

> **Note:** Points are managed in `user_coding_progress`, NOT here. This table is logs only.

---

# 10. Domain / Mentorship System

## 10.1 `domains`

Domain mentorship paths (Data Science, ML, AI, etc.).

```sql
CREATE TABLE domains (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(255)    NOT NULL,
    description     TEXT            NULL,
    thumbnail_url   VARCHAR(500)    NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 10.2 `domain_courses`

Maps courses to a domain in strict sequential order.

```sql
CREATE TABLE domain_courses (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    domain_id       BIGINT UNSIGNED NOT NULL,
    course_id       BIGINT UNSIGNED NOT NULL,
    order_index     INT UNSIGNED    NOT NULL DEFAULT 0,

    UNIQUE KEY uq_dc_domain_course (domain_id, course_id),
    CONSTRAINT fk_dc_domain FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    CONSTRAINT fk_dc_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 10.3 `user_domain_progress`

Tracks a user's overall domain completion and Star award.

```sql
CREATE TABLE user_domain_progress (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    domain_id       BIGINT UNSIGNED NOT NULL,
    is_completed    BOOLEAN         NOT NULL DEFAULT FALSE,
    star_awarded    BOOLEAN         NOT NULL DEFAULT FALSE,
    completed_at    DATETIME        NULL,

    UNIQUE KEY uq_udp_user_domain (user_id, domain_id),
    CONSTRAINT fk_udp_user   FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    CONSTRAINT fk_udp_domain FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    INDEX idx_udp_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 11. Company Preparation

## 11.1 `companies`

Company-specific preparation sections (TCS, Infosys, Amazon, etc.).

```sql
CREATE TABLE companies (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(150)    NOT NULL,
    logo_url        VARCHAR(500)    NULL,
    description     TEXT            NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 11.2 `company_content`

Company-specific content items (hiring patterns, HR questions, mock tests, etc.).

```sql
CREATE TABLE company_content (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id      BIGINT UNSIGNED NOT NULL,
    content_type    ENUM('HIRING_PATTERN','PREVIOUS_MCQ','CODING','MOCK_TEST','TECHNICAL_INTERVIEW','HR_INTERVIEW') NOT NULL,
    title           VARCHAR(255)    NOT NULL,
    content         LONGTEXT        NULL,
    is_premium      BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cc_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_cc_company (company_id),
    INDEX idx_cc_type    (content_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 12. Gamification

## 12.1 `badges`

Defines available badges on the platform.

```sql
CREATE TABLE badges (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    description     TEXT            NULL,
    icon_url        VARCHAR(500)    NULL,
    condition_type  ENUM('POINTS_THRESHOLD','STREAK','COURSE_COMPLETE','DOMAIN_COMPLETE','CODING_SOLVED') NOT NULL,
    condition_value INT UNSIGNED    NOT NULL COMMENT 'e.g. 500 points, 7-day streak, 10 problems solved',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 12.2 `user_badges`

Tracks which badges a user has earned.

```sql
CREATE TABLE user_badges (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    badge_id        BIGINT UNSIGNED NOT NULL,
    earned_at       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_ub_user_badge (user_id, badge_id),
    CONSTRAINT fk_ub_user  FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    CONSTRAINT fk_ub_badge FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
    INDEX idx_ub_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

# 13. Indexing Summary

```sql
-- Fast leaderboard queries
CREATE INDEX idx_user_stats_points ON user_stats(total_points DESC);
CREATE INDEX idx_user_stats_stars  ON user_stats(total_stars DESC);

-- Subscription access checks
CREATE INDEX idx_usub_user_status ON user_subscriptions(user_id, status);
CREATE INDEX idx_usub_end_date    ON user_subscriptions(end_date);

-- Content browsing
CREATE INDEX idx_courses_category ON courses(category_id, status);
CREATE INDEX idx_modules_course   ON modules(course_id, order_index);
CREATE INDEX idx_topics_module    ON topics(module_id, order_index);

-- Progress lookups
CREATE INDEX idx_mp_user_completed ON module_progress(user_id, is_completed);
CREATE INDEX idx_cc_user_course    ON course_completions(user_id, course_id);
CREATE INDEX idx_udp_user_domain   ON user_domain_progress(user_id, is_completed);

-- Coding
CREATE INDEX idx_cp_lang_diff     ON coding_problems(language, difficulty, status);
CREATE INDEX idx_ucp_user_done    ON user_coding_progress(user_id, is_completed);
```

---

# 14. Table Count Summary

| Group                  | Tables |
|------------------------|--------|
| Users & Auth           | 5      |
| Subscription & Payment | 4      |
| Content Structure      | 4      |
| Learning Progress      | 3      |
| Question Bank          | 2      |
| Practice Engine        | 1      |
| Assignment Engine      | 4      |
| Coding Engine          | 4      |
| Domain System          | 3      |
| Company Preparation    | 2      |
| Gamification           | 2      |
| **Total**              | **34** |

---

# 15. Key Business Rules Enforced by Schema

| Rule | Enforced By |
|------|------------|
| Module locked until previous 100% complete | `module_progress.is_completed` checked in application before unlocking |
| End-of-module mini test required | `module_progress.mini_test_submitted = TRUE` required before setting `is_completed = TRUE` |
| 1 Star per completed course | `course_completions` UNIQUE on `(user_id, course_id)` |
| 1 Star per completed domain | `user_domain_progress` UNIQUE on `(user_id, domain_id)` |
| Assignment: no retake after submission | `test_attempts` UNIQUE on `(user_id, test_id)` |
| Interrupted test discards progress | `is_submitted = FALSE` rows ignored; app deletes on re-open |
| Coding: no double points on re-submission | Points tracked in `user_coding_progress`, not `coding_submissions` |
| Practice: unlimited re-attempts | No UNIQUE constraint on `user_practice_attempts` |
| Razorpay payment tracked end-to-end | `payments` table with `razorpay_order_id`, `razorpay_payment_id`, signature |

---

# 16. Production Guidelines

- Use **transactions** for module completion (topics check + mini test check + points award + next module unlock)
- Use **transactions** for test submission (save answers snapshot + compute score + award points)
- **Never store derived percentages** — calculate from `topic_progress` counts at query time
- Keep `user_stats` denormalized for fast leaderboard reads — update via application after each event
- Use `activity_logs` for all significant events — feeds future analytics and AI recommendation features
- Set `STRICT_TRANS_TABLES` SQL mode to enforce data integrity
- Enable `general_log` in dev, disable in production
- Rotate `password_hash` fields with bcrypt (cost factor 12+)
