# chstockbot

构建一个chstockbot，让它帮助我们把几个群有交的管理起来

## 功能需求

* 访问chstockbot得到几个群的入群链接和频道链接
* 在群里支持/help来得到在群里的帮助
* 在配置文件里支持'Admins':[]来设置管理员，可以对举报进行处理
* 在群里支持回复一个消息内容为 /r 来举报一个人，可以在 AdminGroup 里收到举报内容如下："FirstName (id):举报 FirstName (id) 有异常，请管理员们帮忙核实踢除"，在AdminGroup里可以使用 /k uid 将一个人从所有的群、频道里踢了
* 发现一个新用户进群，跟这个用户提示一个问题，回答正确批准通过，回答错误就当做是机器人踢了，并ban 30分钟不能进群

## 课程内容

### ToDo List

* 分支是什么，有什么用？
* 了解如何使用github和提交pull request
* 如何merge各个分支的变更
* 接收到一个包括 @ 内容的command时如何处理？
* 如何给指定的用户or群发送消息
* 如何简单的拼凑出你想要的字符串
* 如何在发出的内容里加link
* 如何将一个人从群里踢出去
* 如何将一个人unban
* 如何使用List来判断当前用户是否是Admins的成员
* 如何获取一个用户进群的信息
* 如何使用VSCode对Python进行单步调试运行

### 学习记录

第二课(2021/5/2)：

* 了解telegram bot的运行机制Updater、Dispatcher、Chat以及CommandHandler到你的处理函数的处理流程
* 了解如何使用和查找python-telegram-bot的文档
* 课堂小抄( https://docs.google.com/presentation/d/1ZhygqeSw5OoVgwciSEByZFm17DRZeXbUvuF5jXxRG5s/edit?usp=sharing )
* 作业： 完成rewards命令，从0到200出一个随机数，如果大于零，用一个随机的话语提示你要得到一个奖励。如果为0，提用一个随机的话语提示你很惨。
* 附加学习作业：阅读github desktop的建立分支和推送分支部分的说明：https://docs.github.com/cn/desktop/contributing-and-collaborating-using-github-desktop/managing-branches#creating-a-branch 建立一个自己的名字的分支并推送到自己的github上去。

第一课(2021/4/25)：

* fork一个repo
* clone一个repo到本地
* 运行第一个echo bot
* 了解命令
* 作业: 自己的机器人支持 /group 的命令，返回两个作业小组的进群链接。单独与bot对话返回的内容与在群里对话返回的内容是不同的。
