import multiprocessing

# Bind to the standard environment port provided dynamically by Render
bind = "0.0.0.0:10000"

# Optimize worker configurations for free tier resources
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
loglevel = "info"