-- ==========================================
-- SafeTravel Database Initialization Script
-- ==========================================
-- Script này sẽ chạy tự động khi MySQL container khởi động lần đầu

-- Đảm bảo database được tạo với charset UTF8
CREATE DATABASE IF NOT EXISTS safetravel
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE safetravel;

-- Grant permissions cho user
GRANT ALL PRIVILEGES ON safetravel.* TO 'safetravel_user'@'%';
FLUSH PRIVILEGES;

-- Các bảng sẽ được tạo tự động bởi SQLAlchemy khi app khởi động
-- Nếu muốn seed data ban đầu, thêm các INSERT statements ở đây
