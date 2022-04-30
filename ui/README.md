# 部署说明

## 1. 准备TradingView的sdk
1. 从 https://github.com/tradingview/charting_library/ 获取SDK，解压后复制`charting_library` 到`/public`目录。
1. 复制`charting_library.min.js` 到 `/src`目录。
1. 复制`datafeeds` 目录到 `/public` 目录。

## 2. nodejs的包安装

下面的yarn和npm只需要二选一即可，不需要都执行。

### 2.1 yarn的方式
安装：
```shell
yarn install
```

启动：
```shell
yarn serve
```

### 2.2 npm的方式
安装：npm install

启动：npm run serve

如果遇到安装包的问题，请把当前环境信息带上，去提issue吧，本人在mac上测试通过，Windows和Linux的环境没有测试过。

## 3. 访问web地址

http://127.0.0.1:8080/
