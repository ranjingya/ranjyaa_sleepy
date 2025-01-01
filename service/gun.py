# 并行工作进程数（必须只能是1，否则socket会出问题）
workers = 1
# 指定每个工作者的线程数
threads = 2
# 监听内网端口5002
bind = '0.0.0.0:5002'
# 工作模式协程
worker_class = 'gevent'
# 请求超时时间，超时后worker会重启
timeout = 60
# 设置最大并发量
worker_connections = 100
# 设置进程文件目录
pidfile = 'gunicorn.pid'
# 设置访问日志和错误信息日志路径
accesslog = 'gunicorn_access.log'
errorlog = 'gunicorn_error.log'
# 设置日志记录水平
loglevel = 'info'
