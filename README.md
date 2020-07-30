Emotibot BOT API
===
[TOC]

取得機器人狀態 
---
基本信息
* Path： http://{HOST}:{PORT}/botstatus?bot_id={bot_id}
* Method： GET
### **CURL**
```gherkin=
curl --location --request GET 'http://localhost:8331/botstatus?bot_id=4b21158a395311e88a710242ac110002'
```
### **Response**
```gherkin=
{
    "status": 200,
    "message": "success",
    "result": {
        "bot_id": "4b21158a395311e88a710242ac110002",
        "work": 1,
        "return_flag": 1,
        "return_finish": 12
    }
}
```
| status | message |
| ----------- | -------- |
| 200| success |
| 204| bot_id doesn't exist |
| 422| Missing required parameters [bot_id] |
| 500| server db error |

更改機器人狀態
---
基本信息
* Path： {HOST}:{PORT}/botstatus
* Method： POST
### **CURL**
```gherkin=
curl --location --request POST 'http://localhost:8331/botstatus' \
--header 'Content-Type: application/json' \
--data-raw '{
    "bot_id":"4b21158a395311e88a710242ac110002",
    "work": 1,
    "return_flag": 1,
    "return_finish": 11
}'
```
### **Headers**

| 參數名稱 | 參數值 |
| ----------- | -------- |
| Content-Type| application/json |
### **Body**
|名稱	| 類型|是否必須|
| ----------- | -------- |-------- |
|bot_id|string|	必须|
|work|int|	必须|
|return_flag|int|	必须|	
|return_finish|int|	必须|	
### **Response**
```gherkin=
{
    "status": 200,
    "message": "success",
    "result": {
        "description": "Success, update work with param:{\"bot_id\": \"4b21158a395311e88a710242ac110002\", \"work\": 1, \"return_flag\": 1, \"return_finish\": 12}"
    }
}
```
| status | message |
| ----------- | -------- |
| 200| success |
| 415| content type should be [application/json] |
| 422| Missing required parameters [bot_id] or [work] or [return_flag] or [return_finish] |
| 500| server db error |
