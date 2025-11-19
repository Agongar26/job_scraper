import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
import random
from email.mime.text import MIMEText

# --------------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------------
SENDER = os.environ["EMAIL_SENDER"]
APP_PASSWORD = os.environ["EMAIL_PASSWORD"]
SERPAPI_KEY = os.environ["SERPAPI_KEY"]
RECEIVER = "alejandrogonzalezgarcia540@gmail.com"

# -------------------------------------------
# NUEVAS PALABRAS CLAVE PARA OFERTAS JUNIOR
# -------------------------------------------
KEYWORDS = [
    "junior", "jr", "entry level", "assistant",
    "desarrollador", "developer", "java", "kotlin", "android",
    "multiplataforma", "it", "soporte", "ciberseguridad",
    "soc", "xdr", "analista", "security", "becario", "practicas"
]

# --------------------------------------------------------
# SERPAPI – GOOGLE JOBS
# --------------------------------------------------------
def search_google_jobs():
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": "junior OR entry level OR developer junior OR it junior OR ciberseguridad junior",
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
        title = job.get("title", "").strip().lower()
        if any(k in title for k in KEYWORDS):
            offers.append({
                "source": "Google Jobs",
                "title": job.get("title", "").strip(),
                "company": job.get("company_name", "No indicada"),
                "location": job.get("location", "No indicada"),
                "salary": job.get("salary", "No especificado"),
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
        "q": "junior OR entry level OR developer junior OR it junior OR ciberseguridad junior",
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
        title = job.get("title", "").strip().lower()
        if any(k in title for k in KEYWORDS):
            offers.append({
                "source": "LinkedIn",
                "title": job.get("title", "").strip(),
                "company": job.get("company_name", "No indicada"),
                "location": job.get("location", "No indicada"),
                "salary": job.get("salary", "No especificado"),
                "link": job.get("linkedin_job_url", "")
            })
    return offers

# --------------------------------------------------------
# SCRAPER – INDEED
# --------------------------------------------------------
def scrape_indeed():
    url = "https://es.indeed.com/jobs?q=junior+developer+it+ciberseguridad&l=Huelva"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    offers = []

    for job in soup.select("div.job_seen_beacon"):
        title_elem = job.select_one("h2 span")
        if not title_elem:
            continue

        title = title_elem.text.strip().lower()
        if not any(k in title for k in KEYWORDS):
            continue

        company_elem = job.select_one(".companyName")
        location_elem = job.select_one(".companyLocation")
        salary_elem = job.select_one(".salary-snippet")

        offers.append({
            "source": "Indeed",
            "title": title_elem.text.strip(),
            "company": company_elem.text.strip() if company_elem else "No indicada",
            "location": location_elem.text.strip() if location_elem else "No indicada",
            "salary": salary_elem.text.strip() if salary_elem else "No especificado",
            "link": "https://es.indeed.com" + job.select_one("a")["href"]
        })
    return offers

# --------------------------------------------------------
# SCRAPER – TECNOEMPLEO
# --------------------------------------------------------
def scrape_tecnoempleo():
    url = "https://www.tecnoempleo.com/busqueda-empleo.php?pr=Huelva&te=remoto"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    offers = []

    for job in soup.select(".oferta"):
        title = job.select_one(".titulo_oferta").text.strip().lower()
        if not any(k in title for k in KEYWORDS):
            continue

        company = job.select_one(".empresa_oferta").text.strip()
        salary_elem = job.select_one(".salario")
        link = "https://www.tecnoempleo.com" + job.select_one("a")["href"]

        offers.append({
            "source": "TecnoEmpleo",
            "title": job.select_one(".titulo_oferta").text.strip(),
            "company": company,
            "location": "Huelva/Remoto",
            "salary": salary_elem.text.strip() if salary_elem else "No especificado",
            "link": link
        })
    return offers

# --------------------------------------------------------
# CREAR TABLA HTML
# --------------------------------------------------------
def build_html_table(items):
    if not items:
        return "<p>No se encontraron ofertas junior hoy.</p>"

    html = """
    <h2>Ofertas JUNIOR (Google Jobs + LinkedIn + Indeed + TecnoEmpleo)</h2>
    <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse;'>
        <tr style='background:#eee;'>
            <th>Fuente</th>
            <th>Puesto</th>
            <th>Empresa</th>
            <th>Ubicación</th>
            <th>Salario</th>
            <th>Enlace</th>
        </tr>
    """

    for j in items:
        html += f"""
        <tr>
            <td>{j['source']}</td>
            <td>{j['title']}</td>
            <td>{j['company']}</td>
            <td>{j['location']}</td>
            <td>{j['salary']}</td>
            <td><a href="{j['link']}" target="_blank">Ver oferta</a></td>
        </tr>
        """

    html += "</table>"
    return html

# --------------------------------------------------------
# ENVIAR CORREO
# --------------------------------------------------------
def send_email(html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Ofertas de trabajo JUNIOR – Reporte"
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
    print("Buscando ofertas JUNIOR...")

    google = search_google_jobs()
    linkedin = search_linkedin_jobs()
    indeed = scrape_indeed()
    tecno = scrape_tecnoempleo()

    all_jobs = google + linkedin + indeed + tecno

    print(f"Resultados Google Jobs: {len(google)}")
    print(f"Resultados LinkedIn: {len(linkedin)}")
    print(f"Resultados Indeed: {len(indeed)}")
    print(f"Resultados TecnoEmpleo: {len(tecno)}")
    print(f"Total ofertas encontradas: {len(all_jobs)}")

    html = build_html_table(all_jobs)
    send_email(html)

if __name__ == "__main__":
    main()
