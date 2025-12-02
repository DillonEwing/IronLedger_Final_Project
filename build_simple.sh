set -e
pip install --upgrade pip
pip install -r requirements.txt
cd ironledger
python manage.py collectstatic --no-input --clear
python manage.py migrate --no-input
