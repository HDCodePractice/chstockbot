# chstockbot

构建一个chstockbot，让它帮助我们把几个群有效的管理起来，同时提供了夕阳红以及毛毛投的相关提醒支持。

[![Build Publish Docker image](https://github.com/HDCodePractice/chstockbot/actions/workflows/build_and_publish_docker.yaml/badge.svg)](https://github.com/HDCodePractice/chstockbot/actions/workflows/build_and_publish_docker.yaml)  [![Schedule Run Sendxyh](https://github.com/HDCodePractice/chstockbot/actions/workflows/schedule_run_xyh.yaml/badge.svg?event=schedule)](https://github.com/HDCodePractice/chstockbot/actions/workflows/schedule_run_xyh.yaml)

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

### chstockbot

#### Linux & MacOS

请确认你的Linux或MacOS上已经安装好Docker和Docker Compose。如果你还没有安装，请参考[安装Docker](https://docs.docker.com/engine/installation/)和[安装Docker Compose](https://docs.docker.com/compose/install/)。我们会使用Docker Compose来运行sendxyh，使用Cron来设置定时任务。

#### 准备配置文件

将[docker-compose.yml](https://github.com/HDCodePractice/chstockbot/blob/main/docker-compose.yml)放到你的运行目录下。并在相同的目录里参考[example.env](https://github.com/HDCodePractice/chstockbot/blob/main/example.env)来放入相应的配置信息。

然后将当前目录变换到 ```docker-compose.yml``` 文件所在的目录。

#### 更新Docker的镜像

```
docker-compose pull
```

#### 启动

```
docker-compose up -d
```

#### 停止

```
docker-compose down
```

#### 查看运行log

```
docker-compose logs -f
```

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


##### 设置Docker

从Docker Hub更新chsstockbot镜像：

```
docker pull hdcola/chstockbot:latest
```

在目录中准备一个 `local.env` 文件，内容参考如下：

```
BOT_TOKEN=YOU_BOT_TOKEN
DEBUG=False
XYHTICKER=[["SPY",10,50,100,200],["QQQ",13,55,100,150,200],["IWM",13,55,100,150,200]]
XYHCHAT=
XYHLOG=
XYHSOURCE=stooq
ADMINS=
ADMIN_GROUP=
GROUPS=
```

测试运行

```
docker run --rm --env-file local.env -it hdcola/chstockbot:latest python /chstockbot/sendxyh.py -c /data
```

##### 设置crontab

执行以下命令，将crontab添加到你的用户下：

```
crontab -e
```

之后在你的crontab中添加以下内容：

```
# 每周一到周五的下午5:00发送夕阳红
0 22 * * 1-5 /usr/local/bin/docker run --rm --env-file local.env hdcola/chstockbot:latest python /chstockbot/sendxyh.py -c /data
```

注意：这里请将 `local.env` 前面加上你的绝对路径。