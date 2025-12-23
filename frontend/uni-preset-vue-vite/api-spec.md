登录页面接口需求文档
1. 用户登录接口
描述
用于验证用户的账号和密码，完成登录操作。

接口路径: /api/auth/login
请求方法: POST
请求参数:
{
  "username": "string", // 用户名
  "password": "string"  // 密码
}
响应示例:
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "string", // 用户登录后的令牌
    "userInfo": {
      "id": "string",
      "username": "string",
      "email": "string"
    }
  }
}

2. 检查保存的登录信息接口
描述
用于检查本地是否保存了用户的登录信息（如记住密码功能）。

接口路径: /api/auth/check-credentials
请求方法: GET
请求参数: 无
响应示例:{
  "success": true,
  "data": {
    "username": "string", // 保存的用户名
    "rememberMe": true    // 是否记住密码
  }
}
3. 忘记密码接口
描述
用于处理用户忘记密码的情况，发送重置密码的邮件或短信。

接口路径: /api/auth/forgot-password
请求方法: POST
请求参数:{
  "username": "string" // 用户名或绑定的邮箱/手机号
}
响应示例:{
  "success": true,
  "message": "重置密码的链接已发送到您的邮箱"
}
4. 注册页面跳转接口（可选）
描述
用于跳转到注册页面时，检查是否需要额外的注册信息。

接口路径: /api/auth/register-info
请求方法: GET
请求参数: 无
响应示例:{
  "success": true,
  "data": {
    "extraFields": ["referralCode"] // 需要额外填写的字段
  }
}
5. 安全区域信息接口（小程序专用）
描述
用于获取设备的状态栏高度、胶囊高度等信息。

接口路径: /api/system/safe-area
请求方法: GET
请求参数: 无
响应示例:{
  "success": true,
  "data": {
    "statusBarHeight": 20,
    "capsuleHeight": 32,
    "topPadding": 60
  }
}
6. 保存用户登录信息接口
描述
用于保存用户的登录信息（如记住密码功能）。

接口路径: /api/auth/save-credentials
请求方法: POST
请求参数:{
  "username": "string", // 用户名
  "rememberMe": true    // 是否记住密码
}
响应示例:{
  "username": "string", // 用户名
  "rememberMe": true    // 是否记住密码
}
7. 加载用户登录信息接口
描述
用于加载用户的登录信息（如记住密码功能）。

接口路径: /api/auth/load-credentials
请求方法: GET
请求参数: 无
响应示例:{
  "success": true,
  "data": {
    "username": "string", // 保存的用户名
    "rememberMe": true    // 是否记住密码
  }
}
8. 登录和注册成功后的跳转接口
描述
用于在用户登录或注册成功后，获取跳转页面的相关信息（如推荐内容、动态列表等）。

接口路径: /api/user/post-login
请求方法: GET
请求参数:
Header: Authorization: Bearer <token> （用户登录后的令牌）
响应示例:
{
  "success": true,
  "data": {
    "redirectUrl": "/pages/discover/discover", // 跳转页面的路径
    "welcomeMessage": "欢迎回来，沐白！",     // 欢迎消息
    "recommendations": [                      // 推荐内容（可选）
      {
        "id": 1,
        "name": "沐白",
        "avatar": "https://picsum.photos/200?1",
        "time": "2分钟前",
        "text": "周末徒步，山顶风景太美啦！",
        "type": "image",
        "media": [
          "https://picsum.photos/400?2",
          "https://picsum.photos/400?3"
        ],
        "tag": "户外",
        "likes": 32,
        "comments": 6,
        "liked": false
      }
    ]
  }
}
备注
所有接口需要支持跨域请求。
登录接口需要返回 JWT 或其他形式的令牌，用于后续的身份验证。
忘记密码接口需要支持多种验证方式（如邮箱、短信）。
接口响应需包含明确的错误信息，便于前端处理。



注册页面接口需求文档
1. 用户注册接口
描述
用于用户提交注册信息，创建新账户。

接口路径: /api/auth/register
请求方法: POST
请求参数:{
  "nickname": "string",        // 用户昵称（2-20个字符）
  "password": "string",        // 用户密码（至少6位）
  "confirmPassword": "string", // 确认密码（需与密码一致）
  "gender": "string",          // 性别（"male" 或 "female"）
  "age": "number"              // 年龄（18-100）
}
响应示例:{
  "success": true,
  "message": "注册成功",
  "data": {
    "userId": "string", // 新注册用户的ID
    "nickname": "string"
  }
}
2. 检查昵称是否重复接口
描述
用于检查用户输入的昵称是否已被占用。

接口路径: /api/auth/check-nickname
请求方法: GET
请求参数:{
  "nickname": "string" // 用户输入的昵称
}
响应示例:{
  "nickname": "string" // 用户输入的昵称
}
或{
  "success": false,
  "message": "昵称已被占用"
}
3. 验证密码强度接口（可选）
描述
用于验证用户输入的密码强度。

接口路径: /api/auth/validate-password-strength
请求方法: POST
请求参数:{
  "password": "string" // 用户输入的密码
}
响应示例:{
  "success": true,
  "strength": "strong", // 密码强度（"weak", "medium", "strong"）
  "message": "密码强度良好"
}
4. 注册成功后的跳转接口（可选）
描述
注册成功后，检查是否需要跳转到其他页面（如完善信息页面）。

接口路径: /api/user/post-register
请求方法: GET
请求参数:
Header: Authorization: Bearer <token>
响应示例:{
  "success": true,
  "data": {
    "nextStep": "complete-profile", // 下一步操作（如完善信息）
    "redirectUrl": "/pages/profile/complete"
  }
}
5. 获取注册页面配置接口（可选）
描述
用于获取注册页面的动态配置（如性别选项、年龄范围等）。

接口路径: /api/auth/register-config
请求方法: GET
请求参数: 无
响应示例:{
  "success": true,
  "data": {
    "genderOptions": ["male", "female"], // 性别选项
    "ageRange": [18, 100]               // 年龄范围
  }
}
备注
所有接口需要支持跨域请求。
注册接口需对用户输入进行严格校验，确保数据合法性。
检查昵称是否重复接口需提供实时反馈，提升用户体验。
接口响应需包含明确的错误信息，便于前端处理。

发现页面接口需求文档
1. 获取动态列表接口
描述
用于获取发现页面的动态列表，包括好友动态、图片、视频等内容。

接口路径: /api/posts
请求方法: GET
请求参数:{
  "page": 1,          // 页码（默认1）
  "pageSize": 10      // 每页条数（默认10）
}
响应示例:{
  "success": true,
  "data": {
    "posts": [
      {
        "id": 1,
        "name": "沐白",
        "avatar": "https://picsum.photos/200?1",
        "time": "2分钟前",
        "text": "周末徒步，山顶风景太美啦！",
        "type": "image",
        "media": [
          "https://picsum.photos/400?2",
          "https://picsum.photos/400?3",
          "https://picsum.photos/400?4"
        ],
        "tag": "户外",
        "likes": 32,
        "comments": 6,
        "liked": false
      }
    ],
    "total": 100 // 动态总数
  }
}
2. 点赞动态接口
描述
用于点赞或取消点赞动态。

接口路径: /api/posts/:id/like
请求方法: POST
请求参数:{
  "liked": true // 是否点赞（true: 点赞, false: 取消点赞）
}
响应示例:{
  "success": true,
  "message": "操作成功",
  "data": {
    "likes": 33 // 当前点赞数
  }
}
3. 获取动态评论接口
描述
用于获取指定动态的评论列表。

接口路径: /api/posts/:id/comments
请求方法: GET
请求参数:{
  "page": 1,          // 页码（默认1）
  "pageSize": 10      // 每页条数（默认10）
}
响应示例:{
  "success": true,
  "data": {
    "comments": [
      {
        "id": 101,
        "name": "小美",
        "avatar": "https://picsum.photos/200?10",
        "content": "风景真不错！下次也想去",
        "time": "1分钟前"
      }
    ],
    "total": 50 // 评论总数
  }
}
4. 发布评论接口
描述
用于发布对动态的评论。

接口路径: /api/posts/:id/comments
请求方法: POST
请求参数:{
  "content": "string" // 评论内容
}
响应示例:{
  "success": true,
  "message": "评论成功",
  "data": {
    "id": 201,
    "name": "我",
    "avatar": "https://picsum.photos/200",
    "content": "这是我的评论",
    "time": "刚刚"
  }
}
5. 获取消息通知接口
描述
用于获取用户的消息通知列表。

接口路径: /api/notifications
请求方法: GET
请求参数:{
  "page": 1,          // 页码（默认1）
  "pageSize": 10      // 每页条数（默认10）
}
响应示例:{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 1,
        "type": "like",
        "name": "小美",
        "avatar": "https://picsum.photos/200?10",
        "time": "刚刚",
        "read": false,
        "postId": 1,
        "postText": "周末徒步，山顶风景太美啦！"
      }
    ],
    "total": 20 // 通知总数
  }
}
6. 标记通知为已读接口
描述
用于标记单条或全部通知为已读。

接口路径: /api/notifications/mark-as-read
请求方法: POST
请求参数:{
  "notificationIds": [1, 2, 3] // 要标记为已读的通知ID列表（为空时标记全部）
}
响应示例:{
  "success": true,
  "message": "操作成功"
}
7. 搜索接口
描述
用于搜索好友、话题或内容。

接口路径: /api/search
请求方法: GET
请求参数:{
  "query": "string", // 搜索关键词
  "type": "all"      // 搜索类型（可选值: "all", "friends", "topics", "posts"）
}
响应示例:{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "type": "friend",
        "name": "小美",
        "avatar": "https://picsum.photos/200?10"
      },
      {
        "id": 2,
        "type": "post",
        "content": "周末徒步，山顶风景太美啦！",
        "media": ["https://picsum.photos/400?2"]
      }
    ]
  }
}
备注
所有接口需要支持分页功能。
点赞、评论等操作需返回最新的动态数据。
消息通知接口需支持未读消息数量统计。
搜索接口需支持多类型搜索，返回结果需按类型分类。

搜索页面接口需求文档
1. 搜索接口
描述
用于根据关键词、标签和日期筛选内容，返回搜索结果。

接口路径: /api/search
请求方法: GET
请求参数:{
  "keyword": "string", // 搜索关键词（可选）
  "tag": "string",     // 搜索标签（可选）
  "date": "string",    // 搜索日期（格式: YYYY-MM-DD，可选）
  "page": 1,           // 页码（默认1）
  "pageSize": 10       // 每页条数（默认10）
}
响应示例:{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "name": "沐白",
        "avatar": "https://picsum.photos/200?1",
        "time": "2分钟前",
        "text": "周末徒步，山顶风景太美啦！",
        "type": "image",
        "media": [
          "https://picsum.photos/400?2",
          "https://picsum.photos/400?3",
          "https://picsum.photos/400?4"
        ],
        "tag": "户外",
        "likes": 32,
        "comments": 6,
        "liked": false
      }
    ],
    "total": 100 // 搜索结果总数
  }
}
2. 获取热门标签接口
描述
用于获取当前系统中的热门标签列表。

接口路径: /api/tags/hot
请求方法: GET
请求参数: 无
响应示例:{
  "success": true,
  "data": {
    "tags": ["户外", "美食", "旅行", "摄影", "运动", "学习"]
  }
}
3. 获取搜索建议接口
描述
用于根据用户输入的关键词，返回相关的搜索建议。

接口路径: /api/search/suggestions
请求方法: GET
请求参数:{
  "keyword": "string" // 用户输入的关键词
}
响应示例:{
  "success": true,
  "data": {
    "suggestions": ["沐白", "阿宁", "小美", "旅行者", "摄影师"]
  }
}
4. 保存搜索历史接口
描述
用于保存用户的搜索历史记录。

接口路径: /api/search/history
请求方法: POST
请求参数:{
  "keyword": "string", // 搜索关键词
  "tag": "string",     // 搜索标签（可选）
  "date": "string"     // 搜索日期（格式: YYYY-MM-DD，可选）
}
响应示例:{
  "success": true,
  "message": "搜索历史已保存"
}
5. 获取搜索历史接口
描述
用于获取用户的搜索历史记录。

接口路径: /api/search/history
请求方法: GET
请求参数: 无
响应示例:{
  "success": true,
  "data": {
    "history": [
      {
        "keyword": "徒步",
        "tag": "户外",
        "date": "2023-10-01"
      },
      {
        "keyword": "美食",
        "tag": "美食",
        "date": "2023-09-30"
      }
    ]
  }
}
6. 清除搜索历史接口
描述
用于清除用户的搜索历史记录。

接口路径: /api/search/history/clear
请求方法: DELETE
请求参数: 无
响应示例:{
  "success": true,
  "message": "搜索历史已清除"
}
7. 点赞动态接口
描述
用于点赞或取消点赞搜索结果中的动态。

接口路径: /api/posts/:id/like
请求方法: POST
请求参数:{
  "liked": true // 是否点赞（true: 点赞, false: 取消点赞）
}
响应示例:{
  "success": true,
  "message": "操作成功",
  "data": {
    "likes": 33 // 当前点赞数
  }
}
8. 获取动态评论接口
描述
用于获取搜索结果中动态的评论列表。

接口路径: /api/posts/:id/comments
请求方法: GET
请求参数:{
  "page": 1,          // 页码（默认1）
  "pageSize": 10      // 每页条数（默认10）
}
响应示例:{
  "success": true,
  "data": {
    "comments": [
      {
        "id": 101,
        "name": "小美",
        "avatar": "https://picsum.photos/200?10",
        "content": "风景真不错！下次也想去",
        "time": "1分钟前"
      }
    ],
    "total": 50 // 评论总数
  }
}
9. 发布评论接口
描述
用于发布对搜索结果中动态的评论。

接口路径: /api/posts/:id/comments
请求方法: POST
请求参数:{
  "content": "string" // 评论内容
}
响应示例:{
  "success": true,
  "message": "评论成功",
  "data": {
    "id": 201,
    "name": "我",
    "avatar": "https://picsum.photos/200",
    "content": "这是我的评论",
    "time": "刚刚"
  }
}
备注
搜索接口需支持关键词、标签和日期的组合筛选。
搜索建议接口需根据用户输入实时返回相关建议。
搜索历史接口需支持分页功能（如历史记录较多时）。
点赞和评论接口需返回最新的动态数据，确保前端实时更新。