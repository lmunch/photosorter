# please source me

if [ ! -d venv3 ]; then
    python3 -m venv venv3
    venv3/bin/pip install --upgrade pip
    venv3/bin/pip install -r requirements.txt
fi

source venv3/bin/activate
