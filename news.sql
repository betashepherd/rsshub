CREATE TABLE `news` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '新闻标题',
  `link` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '链接',
  `summary` text COLLATE utf8mb4_unicode_ci COMMENT '摘要$markdown',
  `content` longtext COLLATE utf8mb4_unicode_ci COMMENT '详情$markdown',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `news_link_index` (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;