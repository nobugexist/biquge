## 目标是全站爬取笔趣阁小说，全站共计章节2400w左右（仅供交流学习，请勿对网站进行长时间高并发访问）
---
### 技术框架：asyncio + aiohttp + redis + motor
### 爬取速度，预计能够单机每日200w左右（测试后才知道真正的速度，这是抓取一万条的速度推算的量）

## 流程说明
+ urlcrawler 对所有小说主页进行子url提取，放入到redis的wait的列表中中，在mongodb中创建book_list,用来存储每本书的作者，id，最后更新日期，简介
+ singpagecrawler 从redis的wait中取出url，拼接后进行访问，访问后进行状态判断，状态码为200，则访问成功加入到，redis的finish的集合中，
否则访问失败，重新放入wait列表，访问小说章节后，会对返回的信息进行提取，将正文信息选择存入mongodb数据库或者直接zlib压缩后存入文件中


#类说明
## crawler
+ urlcrawler 依次遍历访问所有小说的主页面，抓取小说的子url
+ singpagecrawler 访问具体小说章节，提取正文内容，

## config
+ config 保存mongdb,redis,并发量等配置信息

## storage
+ redisclient 对redis的包装类
+ aiomongoclient 对异步操作mongodb的包装类
+ directstorage 将文件直接压缩后保存操作的包装类

## parse
+ parser 对小说主页面，每个章节页面提取信息方法的包装



##可以改进的地方
+ 在urlcrawler中，采用了超长timeout（120秒）尽量避免爬取失败，小说主页url没有错误重爬的机制，
+ 现在采用的是直接使用redis读取url的方式，可以使用rabbitmq来在分布式中进行主机通信，更加可靠
+ 没有考虑到宕机时的问题，应该加入断点续传的机制
+ 只使用了多协程，还可以再加上多进程，调用aiomultiprocess库，更好的利用多核的能力，降低gil全局锁的影响