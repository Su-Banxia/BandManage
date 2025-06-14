USE band_manage;

-- 成员表 (必须首先创建，因为其他表有外键依赖)
CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 乐队表
CREATE TABLE bands (
    band_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    genre VARCHAR(50),
    founding_date DATE NOT NULL,
    leader_id INT NOT NULL,
    description TEXT,
    status ENUM('正常活动', '停止活动') NOT NULL DEFAULT '正常活动',
    FOREIGN KEY (leader_id) REFERENCES members(member_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 成员与乐队关系表
CREATE TABLE member_band (
    band_id INT NOT NULL,
    member_id INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (band_id, member_id),
    FOREIGN KEY (band_id) REFERENCES bands(band_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 可用房间表
CREATE TABLE rooms (
    room_id VARCHAR(20) NOT NULL PRIMARY KEY,  
    type ENUM('排练室', '仓库') NOT NULL,
    location_description VARCHAR(255),        -- 选填，允许NULL
    is_available ENUM('是', '否') NOT NULL DEFAULT '否',
    CHECK (type <> '仓库' OR is_available = '否')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 排练时间表
CREATE TABLE rehearsals (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    band_id INT NOT NULL,
    room_id VARCHAR(20) NOT NULL,            
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    purpose VARCHAR(255),
    status ENUM('已预约', '取消') NOT NULL DEFAULT '已预约',
    FOREIGN KEY (band_id) REFERENCES bands(band_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 表演表
CREATE TABLE performances (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_time DATETIME NOT NULL,
    duration INT NOT NULL COMMENT '持续时间（分钟）',
    location VARCHAR(100) NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 表演曲目表
CREATE TABLE performance_songs (
    song_id INT AUTO_INCREMENT PRIMARY KEY,
    performance_id INT NOT NULL,
    band_id INT NOT NULL,
    song_name VARCHAR(100) NOT NULL,
    song_order INT NOT NULL,
    FOREIGN KEY (performance_id) REFERENCES performances(performance_id) ON DELETE CASCADE,
    FOREIGN KEY (band_id) REFERENCES bands(band_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 设备表
CREATE TABLE equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    status ENUM('可用', '借出', '维修中', '损坏或丢失') NOT NULL DEFAULT '可用',
    storage_room_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (storage_room_id) REFERENCES rooms(room_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 设备租赁表
CREATE TABLE equipment_rentals (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,
    borrower_id INT NOT NULL COMMENT '借用人ID',
    rent_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE RESTRICT,
    FOREIGN KEY (borrower_id) REFERENCES members(member_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;