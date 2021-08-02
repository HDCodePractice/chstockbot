# chstockbot

构建一个chstockbot，让它帮助我们把几个群有交的管理起来

## 支持功能
* 支持/help 获取帮助
* 支持/r 举报用户
* admin组支持 /kk 移除被举报人 /kr 移除举报人
* 每天发送夕阳红信息； 包括指定股票的当日调整后收盘价；指定周期的均价； spx500 和ndx100 高于50周期均价的百分比
* 支持计算指定日期的毛毛投的利润率（包括大毛毛和小毛毛）
## 发送消息
* sendxyh.py -d yyyymmdd
* sendmmt.py -s yyyymmdd -e yyyymmdd

## 功能需求

* 访问chstockbot得到几个群的入群链接和频道链接
* 在群里支持/help来得到在群里的帮助
* 在配置文件里支持'Admins':[]来设置管理员，可以对举报进行处理
* 在群里支持回复一个消息内容为 /r 来举报一个人，可以在 AdminGroup 里收到举报内容如下："FirstName (id):举报 FirstName (id) 有异常，请管理员们帮忙核实踢除"，在AdminGroup里可以使用 /k uid 将一个人从所有的群、频道里踢了
* 发现一个新用户进群，跟这个用户提示一个问题，回答正确批准通过，回答错误就当做是机器人踢了，并ban 30分钟不能进群

## 运行部署

### 定时任务（sendxyh、sendmmt）

#### Github Action Cron

定时任务在设计上支持了Github Action的执行。需要运行，你只需要fork本项目。

##### sendxyh

查看 `.github/workflows/schedule_run_xyh.yaml` 最后的 sendxyh 中的env说明来修改。

在你的代码库的Setting-Secrets加入以下环境变量：

```
BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
XYHCHAT: ${{ secrets.XYHCHAT }}
XYHLOG: ${{ secrets.XYHLOG }}
```

