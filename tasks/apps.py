# file: tasks/apps.py

import os
from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Mencegah scheduler berjalan ganda karena fitur auto-reload bawaan Django
        if os.environ.get('RUN_MAIN') == 'true':
            from apscheduler.schedulers.background import BackgroundScheduler
            from tasks.jobs import periksa_dan_kirim_pengingat

            scheduler = BackgroundScheduler()
            
            # Atur mesin untuk menjalankan fungsi setiap 1 menit
            scheduler.add_job(periksa_dan_kirim_pengingat, 'interval', minutes=1)
            scheduler.start()
            print("⏰ Mesin APScheduler EIO Master telah aktif!")