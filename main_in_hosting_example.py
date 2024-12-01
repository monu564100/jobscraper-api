import os
import sys
from app import create_app

# Menambahkan path aplikasi ke sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Membuat aplikasi Flask
app = create_app()

# Mod_wsgi membutuhkan aplikasi yang akan dipanggil `application`
# Jadi kita pastikan nama aplikasi adalah 'application'
application = app
