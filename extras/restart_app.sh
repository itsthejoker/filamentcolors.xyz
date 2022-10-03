echo "Restarting app..."
sudo service gunicorn restart && sudo service nginx restart
