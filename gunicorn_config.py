bind = "0.0.0.0:8000"
workers = 2
pythonpath = "."
accesslog = "-"
errorlog = "-"
wsgi_app = "backend.wsgi:application"
chdir = "/opt/render/project/src/"