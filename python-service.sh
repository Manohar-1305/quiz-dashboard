[Unit]
Description=Quiz Dashboard Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/app/quiz-dashboard
ExecStart=/root/app/quiz-dashboard/venv/bin/python /root/app/quiz-dashboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
