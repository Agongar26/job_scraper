import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --------------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------------
SENDER = os.environ["EMAIL_SENDER"]
APP_PASSWORD = os.environ["EMAIL_PASSWORD"]
SERPAPI_KEY = os.environ["SERPAPI_KEY"]
RECEIVER = "alejandrogonzalezgarcia540@gmail.com"

KEYWORDS = [
    "desarrollador", "developer", "java", "kotlin", "android",
    "multiplataforma", "it", "soporte", "ciberseguridad",
    "soc", "xdr", "analista", "security"
]

# --------------------------------------------------------
# SERPAPI – GOOGLE JOBS
# --------------------------------------------------------
def search_google_jobs():
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": "developer OR ciberseguridad OR it",
        "location": "Spain",
        "hl": "es",
        "safe": "off",
        "api_key": SERPAPI_KEY
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()
        jobs = data.get("jobs_results", [])
    except Exception as e:
        print("Error Google Jobs:", e)
        return []

    offers = []
    for job in jobs:
        title = job.get("title", "").strip()
        if any(k in title.lower() for k in KEYWORDS):
            offers.append({
                "source": "Google Jobs",
                "title": title,
                "company": job.get("company_name", "No indicada"),
                "location": job.get("location", "No indicada"),
                "link": job.get("job_apply_link", job.get("related_links", [{}])[0].get("link", ""))
            })
    return offers

# --------------------------------------------------------
# SERPAPI – LINKEDIN JOBS
# --------------------------------------------------------
def search_linkedin_jobs():
    url = "https://serpapi.com/search"
    params = {
        "engine": "linkedin_jobs",
        "q": "developer OR ciberseguridad OR IT",
        "location": "Spain",
        "api_key": SERPAPI_KEY
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()
        jobs = data.get("jobs_results", [])
    except Exception as e:
        print("Error LinkedIn Jobs:", e)
        return []

    offers = []
    for job in jobs:
        title = job.get("title", "").strip()
        if any(k in title.lower() for k in KEYWORDS):
            offers.append({
                "source": "LinkedIn",
                "title": title,
                "company": job.get("company_name", "No indicada"),
                "location": job.get("location", "No indicada"),
                "link": job.get("linkedin_job_url", "")
            })
    return offers

# --------------------------------------------------------
# CREAR TABLA HTML
# --------------------------------------------------------
def build_html_table(items):
    if not items:
        return "<p>No se encontraron ofertas hoy.</p>"

    html = """
    <h2>Ofertas encontradas (Google Jobs + LinkedIn)</h2>
    <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse;'>
        <tr style='background:#eee;'>
            <th>Fuente</th><th>Puesto</th><th>Empresa</th><th>Ubicación</th><th>Enlace</th>
        </tr>
    """

    for j in items:
        html += f"""
        <tr>
            <td>{j['source']}</td>
            <td>{j['title']}</td>
            <td>{j['company']}</td>
            <td>{j['location']}</td>
            <td><a href="{j['link']}">Ver oferta</a></td>
        </tr>
        """

    html += "</table>"
    return html

# --------------------------------------------------------
# ENVIAR CORREO
# --------------------------------------------------------
def send_email(html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Ofertas de trabajo – Reporte semanal"
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECEIVER, msg.as_string())

    print("Correo enviado correctamente.")

# --------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# --------------------------------------------------------
def main():
    print("Buscando ofertas...")

    google = search_google_jobs()
    linkedin = search_linkedin_jobs()

    all_jobs = google + linkedin

    print(f"Resultados Google Jobs: {len(google)}")
    print(f"Resultados LinkedIn: {len(linkedin)}")
    print(f"Total ofertas encontradas: {len(all_jobs)}")

    html = build_html_table(all_jobs)
    send_email(html)

if __name__ == "__main__":
    main()
