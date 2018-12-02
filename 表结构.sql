CREATE TABLE `movies_copy1` (
  `id` int(10) NOT NULL AUTO_INCREMENT COMMENT '排序',
  `movie_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '电影序号',
  `movie_link` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '电影链接',
  `name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '电影名',
  `director` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '导演',
  `screenwriter` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '编剧',
  `actor` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '演员',
  `style` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '类型',
  `production` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '制片国家/地区',
  `language` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '语言',
  `thetime` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '上映时间',
  `time` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '片长',
  `IMDb` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT ' IMDb链接',
  `socre` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT ' 评分',
  `intro` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT ' 介绍',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59052 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci