python Setup.py
gunicorn -w 4 -b 0.0.0.0:3000 openk:app
