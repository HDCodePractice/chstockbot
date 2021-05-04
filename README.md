# chstockbot

## 功能需求

* 访问chstockbot得到几个群的入群链接和频道链接
* 在群里支持/help来得到在群里的帮助
* 在配置文件里支持'Admins':[]来设置管理员，可以对举报进行处理
* 在群里支持 /r @id 来举报一个人，可以在 AdminGroup 里收到举报内容如下："FirstName (id):举报 FirstName (id) 有异常，请管理员们帮忙核实踢除"，在AdminGroup里可以使用 /k uid 将一个人从所有的群、频道里踢了

## 课程内容

构建一个chstockbot，让它帮助我们把几个群有交的管理起来

第一课：
* 了解如何使用github和提交pull request
* 了解一下基础的运行方法
* telegram bot的command是什么
* 如何为bot增加一个command
* 完成 /start /help command

也许：
* 了解update里有什么
* 了解chatid是什么
* 学习if语句，为不同的chatid返回不同的值
