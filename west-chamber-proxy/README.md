项目目的
--------
* 不需要服务器的本地翻墙代理工具。
* [项目维护地址](https://github.com/liruqi/west-chamber-season-3/tree/master/west-chamber-proxy)
* [Follow up](https://plus.google.com/b/108661470402896863593/)
* [捐赠本项目](https://me.alipay.com/liruqi)

使用方法
--------
* Windows

    1. 下载[客户端](https://github.com/downloads/liruqi/west-chamber-season-3/west-chamber-proxy-20120131.zip)，解压缩，双击 exe
    2. 把浏览器HTTP/HTTPS 代理设置为 127.0.0.1:1998。
    3. Windows 版本更新比较慢。如果希望使用最新代码，先下载 python 2.7，[32位](http://python.org/ftp/python/2.7.2/python-2.7.2.msi) / [64位](http://python.org/ftp/python/2.7.2/python-2.7.2.amd64.msi) ，然后下载[代码](https://github.com/liruqi/west-chamber-season-3/zipball/master)，解压缩，进入 west-chamber-proxy 文件夹，双击 westchamberproxy.py。

* Mac / Linux

    1. 下载项目代码: [zip](https://github.com/liruqi/west-chamber-season-3/zipball/master)
    1. 解压缩，打开终端，cd 到代码目录，cd west-chamber-proxy; python westchamberproxy.py
    2. 把浏览器HTTP/HTTPS 代理设置为 127.0.0.1:1998。

* Android

    基于[GAE Proxy](http://code.google.com/p/gaeproxy/)修改的。Google Market 上的[地址](https://market.android.com/details?id=org.westchamberproxy)。

* iOS
    
    目前不打算自己做一个iOS 应用放在 appstore上。因为这需要做成浏览器，我不喜欢做自己不擅长而且重复的事情。iOS 上要使用代理有两个办法。

    1. 局域网内的其它设备(PC, Android 设备)上安装本代理，然后把 iOS 设备的 HTTP 代理设置到该设备上。（或者在国内有服务器的同学，自己搭建HTTP 代理）
    2. 类似GoAgent 那种iOS客户端的办法。需要越狱。单我本人没有iOS设备，所以，暂不研究了。

* Chrome Extension

    安装[SwitchySharp](https://chrome.google.com/webstore/detail/dpplabbmogkhghncfbfdeeokoefdjegm) 插件，然后导入这个设置 https://github.com/liruqi/west-chamber-season-3/raw/master/west-chamber-proxy/chrome/SwitchyOptions.bak

开发者
------
* [XIAOXIA](http://xiaoxia.org), 原始版本作者
* [LIRUQI](http://liruqi.info), 后续开发, 各平台的打包、发布

DNS污染
-------
有实现用户态反DNS污染。而且独立于系统的DNS配置。

IP封锁
------
由于不依赖与第三方服务器，对于IP封锁也没有优美的解决方案。目前通过更新配置文件的方式，尽量避免IP封锁。
现在是通过 Google code 上[SmartHosts项目](http://code.google.com/p/smarthosts/) 自动获取的[配置文件](http://smarthosts.googlecode.com/svn/trunk/hosts)

可用性
------
1. 如果国外网站IP被封锁，使用本工具可能无法访问。
2. 如果国外网站被关键词过滤，且没有严格遵守 [rfc2616 - section 4.1](http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html)，本工具可能不生效。

问题反馈
--------
在[这里](https://github.com/liruqi/west-chamber-season-3/issues) 反馈各种问题。 

软件更新
-------
日常会有配置文件更新。如果有程序的更新，会在下载页面中给出。

TODO
----
* [ALL] 整理被blocked 的 IP列表，走网页代理
* [ALL] merge accelerates from [ccp0101/dnschina](https://github.com/ccp0101/dnschina)
* [Android] 实现系统HTTP 代理的设置，这样系统自带的浏览器也可以用。
* [Android] 用 Java 重写代理逻辑，用户就不用下载依赖的 python 软件包。

UPDATE LOG
---
* 2011-11-23 解决android 客户端的远程 dns 解析的问题。
* 2011-11-24 对于IP被封锁的站点，走网页代理。
* 2012-01-08 联通的WLAN热点下失效的问题，联通自己解决了。[ref](http://weibo.com/1641981222/xFx46sR4c)
* 2012-01-05 HTTPS 支持。
* 2012-01-28 Windows 平台支持；国内站点 Comet 连接，停止重定向到网页代理。
* 2012-01-31 停止维护chrome extension, 而是类似于goagent，直接提供代理程序，以及 SwitchySharp 备份。
* 2012-02-24 修复Google plus 链接重定向错误 (plus.url.google.com => plus.url.google.com.hk)
* 2012-02-29 修复不支持 GET path 中不带域名信息的服务器(例如www.swaneye.com)


