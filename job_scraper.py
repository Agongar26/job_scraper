import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import xml.etree.ElementTree as ET

# --------------------------------------------------------
# CONFIGURACIÓN DEL CORREO (desde secretos de GitHub)
# --------------------------------------------------------
SENDER = os.environ.get("EMAIL_SENDER")
APP_PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECEIVER = "alejandrogonzalezgarcia540@gmail.com"

KEYWORDS = [
    "Desarrollador", "Developer", "Java", "Kotlin", "Android",
    "Multiplataforma", "IT", "Soporte", "Ciberseguridad",
    "SOC", "XDR", "Analista", "Security"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


# --------------------------------------------------------
# SCRAPER: INDEED
# --------------------------------------------------------
def scrape_indeed():
    url = "https://es.indeed.com/jobs?q=developer+it+ciberseguridad&l=Huelva"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    offers = []

    for job in soup.select("div.job_seen_beacon"):
        title = job.select_one("h2 span")
        company = job.select_one(".companyName")
        link = job.select_one("a")
        location = job.select_one(".companyLocation")

        if not title:
            continue

        job_title = title.text.strip()
        job_company = company.text.strip() if company else "No especificada"
        job_link = "https://es.indeed.com" + link["href"] if link else ""
        job_location = location.text if location else "No indicada"

        if any(k.lower() in job_title.lower() for k in KEYWORDS):
            offers.append(("Indeed", job_title, job_company, job_location, job_link))

    return offers


# --------------------------------------------------------
# SCRAPER: TECNOEMPLEO
# --------------------------------------------------------
def scrape_tecnoempleo():
    url = "https://www.tecnoempleo.com/busqueda-empleo.php?pr=Huelva&te=remoto"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    offers = []

    for job in soup.select(".oferta"):
        title = job.select_one(".titulo_oferta").text.strip()
        company = job.select_one(".empresa_oferta").text.strip()
        link = "https://www.tecnoempleo.com" + job.select_one("a")["href"]

        if any(k.lower() in title.lower() for k in KEYWORDS):
            offers.append(("Tecnoempleo", title, company, "Huelva/Remoto", link))

    return offers


# --------------------------------------------------------
# SCRAPER: LINKEDIN (LEGAL – vía RSS)
# --------------------------------------------------------
def scrape_linkedin_rss():
    url = "https://www.linkedin.com/jobs-guest/jobs/rss/?keywords=developer%20ciberseguridad&location=Huelva"
    r = requests.get(url, headers=HEADERS)

    offers = []
    try:
        root = ET.fromstring(r.text)

        for item in root.findall(".//item"):
            title = item.find("title").text or "Sin título"
            link = item.find("link").text or ""
            description = item.find("description").text or ""
            location = "Huelva"

            if any(k.lower() in title.lower() for k in KEYWORDS):
                offers.append(("LinkedIn", title, "Desconocida", location, link))

    except Exception as e:
        print("Error leyendo RSS de LinkedIn:", e)

    return offers


# --------------------------------------------------------
# CREAR TABLA HTML
# --------------------------------------------------------
def build_html_table(data):
    if not data:
        return "<p>No se encontraron ofertas esta semana.</p>"

    table = """
    <h2>Ofertas de empleo (Indeed / TecnoEmpleo / LinkedIn)</h2>
    <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse;'>
        <tr style='background:#f0f0f0;'>
            <th>Fuente</th>
            <th>Puesto</th>
            <th>Empresa</th>
            <th>Ubicación</th>
            <th>Enlace</th>
        </tr>
    """

    for source, title, company, location, link in data:
        table += f"""
        <tr>
            <td>{source}</td>
            <td>{title}</td>
            <td>{company}</td>
            <td>{location}</td>
            <td><a href='{link}'>Ver oferta</a></td>
        </tr>
        """

    table += "</table>"
    return table


# --------------------------------------------------------
# ENVIAR CORREO
# --------------------------------------------------------
def send_email(html):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Ofertas de trabajo – Lunes 08:00 AM"
        msg["From"] = SENDER
        msg["To"] = RECEIVER
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, APP_PASSWORD)
            server.sendmail(SENDER, RECEIVER, msg.as_string())

        print("Correo enviado correctamente ✅")

    except Exception as e:
        print("Error enviando correo:", e)
        raise


# --------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# --------------------------------------------------------
def main():
    indeed = scrape_indeed()
    tecnoempleo = scrape_tecnoempleo()
    linkedin = scrape_linkedin_rss()

    print("Indeed:", len(indeed))
    print("Tecnoempleo:", len(tecnoempleo))
    print("LinkedIn:", len(linkedin))

    all_jobs = indeed + tecnoempleo + linkedin
    html = build_html_table(all_jobs)
    send_email(html)


if __name__ == "__main__":
    main()
