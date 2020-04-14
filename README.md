# quant-learn
量化交易学习

## 搭建环境

通过 docker 搭建依赖环境，包含：python3.7+ 、conda，已安装的依赖包：numpy、pandas、TA-Lib、futu-api。

1. 构建镜像
```
docker build -t quant .
```

2. 运行容器
```
docker run -ti --name quant-learn quant /bin/sh
```

