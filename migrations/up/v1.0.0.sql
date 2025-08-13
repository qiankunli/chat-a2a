CREATE TABLE IF NOT EXISTS  `conversation` (
    `id` varchar(36) NOT NULL COMMENT 'id',
    `name` varchar(50) NOT NULL COMMENT '名称',
    `introduction` varchar(255) DEFAULT NULL COMMENT '简介',
    `create_time` datetime DEFAULT (now()) COMMENT '创建时间',
    `update_time` datetime DEFAULT (now()) COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS  `message` (
    `id` varchar(36) NOT NULL COMMENT 'id',
    `conversation_id` varchar(36) NOT NULL COMMENT 'conversation id',
    `intention_id` varchar(36) NOT NULL COMMENT '意图id',
    `role` varchar(36) DEFAULT NULL COMMENT '角色',
    `type` varchar(36) DEFAULT NULL COMMENT '类型',
    `agent` varchar(128) DEFAULT NULL COMMENT 'agent名称',
    `content` text DEFAULT NULL COMMENT '内容',
    `create_time` datetime DEFAULT (now()) COMMENT '创建时间',
    `update_time` datetime DEFAULT (now()) COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_conversation_id` (`conversation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

