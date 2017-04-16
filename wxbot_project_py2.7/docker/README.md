# 本地构建 wechat_bot docker 镜像

拉下镜像:

```bash
docker pull ubuntu:16.04
```

打包本项目，将压缩包放到`docker`目录下:

```
tar -czf weixin_bot.tar.gz wxbot_project_py2.7/
```

切换到`docker`目录，执行`build`命令:

```bash
docker build -t wechat-bot .
```

导出镜像:

```bash
docker save wechat-bot > wechat.tar
```

导入镜像:

```bash
docker load < wechat.tar
```

运行:

```bash
docker run -d -P --name xxx -v /src/data/dir:/Wechat_bot/test wechat-bot
```

删除镜像:

```bash
docker rmi -f wechat-bot
```

查看log:

```bash
docker log wechat-bot
```
