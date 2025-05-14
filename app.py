from flask import Flask, Response
import requests, os, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Configuration via variables d'environnement
SONDE_IP = os.getenv("SONDE_IP", "192.168.1.123")
VALEUR_SEC = float(os.getenv("VALEUR_SEC", "835"))
VALEUR_HUMIDE = float(os.getenv("VALEUR_HUMIDE", "420"))
PORT = int(os.getenv("PORT", "8080"))

# Prometheus metric
humidite_metric = Gauge("humidite_sonde", "Taux d'humidité du sol (%)")
lecture_success = Gauge("humidite_sonde_status", "Statut de la dernière lecture (1=ok, 0=échec)")

# Lecture de la sonde et mise à jour de la métrique
def lire_sonde():
    try:
        url = f"http://{SONDE_IP}/read"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        analog = r.json().get("analogValue")

        if analog is None:
            raise ValueError("Valeur manquante")

        humidite = round((VALEUR_SEC - analog) / (VALEUR_SEC - VALEUR_HUMIDE) * 100, 2)
        humidite = max(0, min(humidite, 100))

        humidite_metric.set(humidite)
        lecture_success.set(1)
        print(f"[{datetime.datetime.now()}] Lecture : {humidite} %")

    except Exception as e:
        print(f"Erreur lecture sonde : {e}")
        lecture_success.set(0)

# Endpoint Prometheus
@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# Scheduler toutes les heures
scheduler = BackgroundScheduler()
scheduler.add_job(lire_sonde, 'interval', minutes=1)
scheduler.start()

# Lecture initiale au démarrage
lire_sonde()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
