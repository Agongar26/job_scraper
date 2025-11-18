import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

SENDER = os.environ.get("EMAIL_SENDER")
APP_PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECEIVER = "alejandrogonzalezgarcia540@gmail.com"

KEYWORDS = [
    "Desarrollador", "Developer", "Software", "Programador",
    "Java", "Kotlin", "Android", "IT", "Soporte",
    "Ciberseguridad", "Seguridad", "SOC", "XDR",
    "Analista", "Security", "Backend", "Frontend",
    "Fullstack", "Ingeniero"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


# --------------------------------------------------------
# SCRAPER INDEED (2025)
# --------------------------------------------------------
def scrape_indeed():
    url = "https://es.indeed.com/jobs?q=developer+it+ciberseguridad&l=Huelva"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    offers = []
    jobs = soup.select("ul.jobsearch-ResultsList li")

    for job in jobs:
        title = job.select_one(".jobTitle span")
        if not title:
            continue

        company = job.select_one(".companyName")
        location = job.select_one(".companyLocation")
        link = job.select_one(".jobTitle a")

        job_title = title.text.strip()
        job_company = company.text.strip() if company else "No especificada"
        job_location = location.text.strip() if location else "No indicada"
        job_link = "https://es.indeed.com" + link["href"] if link else ""

        if any(k.lower() in job_title.lower() for k in KEYWORDS):
            offers.append((job_title, job_company, job_location, job_link))

    return offers


# --------------------------------------------------------
# SCRAPER TECNOEMPLEO (2025)
# --------------------------------------------------------
def scrape_tecnoempleo():
    url = "https://www.tecnoempleo.com/ofertas-trabajo-huelva"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    offers = []
    jobs = soup.select("article.box_offer")

    for job in jobs:
        title = job.select_one(".title_offer a")
        company = job.select_one(".name")
        location = job.select_one(".localidad")
        link = job.select_one(".title_offer a")

        if not title:
            continue

        job_title = title.text.strip()
        job_company = company.text.strip() if company else "No especificada"
        job_location = location.text.strip() if location else "No indicada"
        job_link = "https://www.tecnoempleo.com" + link["href"] if link else ""

        if any(k.lower() in job_title.lower() for k in KEYWORDS):
            offers.append((job_title, job_company, job_location, job_link))

    return offers


# --------------------------------------------------------
# SCRAPER LINKEDIN HTML (NO RSS)
# --------------------------------------------------------
def scrape_linkedin():
    url = "https://www.linkedin.com/jobs/search/?keywords=developer%20it%20ciberseguridad&location=Huelva"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    offers = []
    jobs = soup.select("li")

    for job in jobs:
        title = job.select_one("h3")
        link = job.select_one("a.base-card__full-link")
        company = job.select_one("h4")
        location = job.select_one(".job-search-card__location")

        if not title or not link:
            continue

        job_title = title.text.strip()
        job_company = company.text.strip() if company else "No especificada"
        job_location = location.text.strip() if location else "No indicada"
        job_link = link.get("href")

        if any(k.lower() in job_title.lower() for k in KEYWORDS):
            offers.append((job_title, job_company, job_location, job_link))

    return offers


# --------------------------------------------------------
# HTML TABLE
# --------------------------------------------------------
def build_html_table(data):
    if not data:
        return "<p>No se encontraron ofertas esta semana.</p>"

    table = """
    <h2>Ofertas de empleo actualizadas (IT / Desarrollo / Ciberseguridad)</h2>
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
# SEND EMAIL
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
# MAIN
# --------------------------------------------------------
def main():
    indeed = scrape_indeed()
    tecno = scrape_tecnoempleo()
    linkedin = scrape_linkedin()

    print("Indeed:", len(indeed))
    print("TecnoEmpleo:", len(tecno))
    print("LinkedIn:", len(linkedin))

    all_jobs = indeed + tecno + linkedin
    html = build_html_table(all_jobs)

    send_email(html)


if __name__ == "__main__":
    main()
