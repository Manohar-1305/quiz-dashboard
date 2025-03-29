[Unit]
Description=flask app
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/quiz-dashboard
Environment="PATH=/root/quiz-dashboard/venv/bin"
ExecStart=/root/quiz-dashboard/venv/bin/python3 /root/quiz-dashboard/app.py

[Install]
WantedBy=multi-user.target

