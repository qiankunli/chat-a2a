CREATE TABLE IF NOT EXISTS `migration` (
    `id` TINYINT NOT NULL COMMENT '主键, 只允许为 1',
    `version` VARCHAR(32) NOT NULL COMMENT '当前数据库表结构版本',
    `update_time` DATETIME NOT NULL COMMENT '更新时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# IGNORE 表示若存在该主键(id = 1)则不执行插入
INSERT IGNORE INTO `migration` (`id`, `version`, `update_time`) VALUES (1, 'v0.0.0', NOW());
