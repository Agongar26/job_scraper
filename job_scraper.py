import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

SENDER = os.environ.get("EMAIL_SENDER")
APP_PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECEIVER = "alejandrogonzalezgarcia540@gmail.com"
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

KEYWORDS = [
    "desarrollador", "developer", "software", "programador",
    "java", "kotlin", "android", "it", "soporte",
    "ciberseguridad", "seguridad", "soc", "xdr",
    "analista", "security", "backend", "frontend",
    "fullstack", "ingeniero"
]


# --------------------------------------------------------
# SCRAPER: GOOGLE JOBS (Incluye Indeed y muchos más)
# --------------------------------------------------------
def scrape_google_jobs():
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": "developer OR it OR ciberseguridad",
        "location": "Huelva, Spain",
        "api_key": SERPAPI_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    offers = []
    jobs = data.get("jobs_results", [])

    for job in jobs:
        title = job.get("title", "").strip()
        company = job.get("company_name", "Desconocida")
        location = job.get("location", "No indicada")
        link = job.get("job_highlights", [{}])[0].get("link") or job.get("related_links", [{}])[0].get("link", "")

        if any(k in title.lower() for k in KEYWORDS):
            offers.append((title, company, location, link))

    return offers


# --------------------------------------------------------
# SCRAPER: LINKEDIN (via SerpAPI)
# --------------------------------------------------------
def scrape_linkedin():
    url = "https://serpapi.com/search"
    params = {
        "engine": "linkedin_jobs",
        "keywords": "developer it ciberseguridad",
        "location": "Huelva, Spain",
        "api_key": SERPAPI_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    offers = []

    jobs = data.get("jobs_results", [])

    for job in jobs:
        title = job.get("title", "").strip()
        company = job.get("company", {}).get("name", "Desconocida")
        location = job.get("location", "No indicada")
        link = job.get("job_url", "")

        if any(k in title.lower() for k in KEYWORDS):
            offers.append((title, company, location, link))

    return offers


# --------------------------------------------------------
# CREAR TABLA HTML
# --------------------------------------------------------
def build_html_table(data):
    if not data:
        return "<p>No se encontraron ofertas esta semana.</p>"

    table = """
    <h2>Ofertas de empleo (IT / Desarrollo / Ciberseguridad)</h2>
    <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse;'>
        <tr style='background:#f0f0f0;'>
            <th>Puesto</th>
            <th>Empresa</th>
            <th>Ubicación</th>
            <th>Enlace</th>
        </tr>
    """

    for title, company, location, link in data:
        table += f"""
        <tr>
            <td>{title}</td>
            <td>{company}</td>
            <td>{location}</td>
            <td><a href='{link}'>Ver oferta</a></td>
        </tr>
        """

    table += "</table>"
    return table


# --------------------------------------------------------
# ENVIAR EMAIL
# --------------------------------------------------------
def send_email(html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Ofertas de trabajo – Reporte Semanal"
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECEIVER, msg.as_string())

    print("Correo enviado correctamente.")


# --------------------------------------------------------
# PRINCIPAL
# --------------------------------------------------------
def main():
    print("Buscando ofertas...")

    google_jobs = scrape_google_jobs()
    linkedin = scrape_linkedin()

    print(f"Google Jobs: {len(google_jobs)}")
    print(f"LinkedIn Jobs: {len(linkedin)}")

    all_jobs = google_jobs + linkedin
    html = build_html_table(all_jobs)

    send_email(html)


if __name__ == "__main__":
    main()
