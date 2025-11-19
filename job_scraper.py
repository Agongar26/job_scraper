import os
import requests
import time
import random
from bs4 import BeautifulSoup
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

# --------------------------------------------------------
# PALABRAS CLAVE (JUNIOR)
# --------------------------------------------------------
KEYWORDS = [
    "junior", "jr", "entry level", "assistant", "becario", "practicas",
    "desarrollador", "developer", "java", "kotlin", "android",
    "multiplataforma", "it", "soporte", "ciberseguridad",
    "soc", "xdr", "analista", "security"
]

# --------------------------------------------------------
# USER AGENTS ROTATIVOS (anti-bloqueo)
# --------------------------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
        "Referer": "https://www.google.com/"
    }

# --------------------------------------------------------
# REQUEST ANTIBLOQUEO
# --------------------------------------------------------
def safe_request(url):
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=get_headers(), timeout=15)
            if resp.status_code == 200:
                time.sleep(random.uniform(1, 2.5))  # Anti-ban
                return resp
        except:
            pass
        time.sleep(random.uniform(2, 4))

    return None

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
        "api_key": SERPAPI_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        data = r.json()
        jobs = data.get("jobs_results", [])
    except Exception as e:
        print("Error Google Jobs:", e)
        return []

    offers = []
    for job in jobs:
        title = job.get("title", "").lower()

        if any(k in title for k in KEYWORDS):
            offers.append({
                "source": "Google Jobs",
                "title": job.get("title", ""),
                "company": job.get("company_name", "No indicada"),
                "location": job.get("location", "No indicada"),
                "salary": job.get("salary", "No especificado"),
                "link": job.get("job_apply_link", "")
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
        r = requests.get(url, params=params, timeout=20)
        data = r.json()
        jobs = data.get("jobs_results", [])
    except Exception as e:
        print("Error LinkedIn Jobs:", e)
        return []

    offers = []
    for job in jobs:
        title = job.get("title", "").lower()
        if any(k in title for k in KEYWORDS):
            offers.append({
                "source": "LinkedIn",
                "title": job.get("title", ""),
                "company": job.get("company_name", "No indicada"),
                "location": job.get("location", "No indicada"),
                "salary": job.get("salary", "No especificado"),
                "link": job.get("linkedin_job_url", "")
            })
    return offers

# --------------------------------------------------------
# SCRAPER INDEED (con anti-bloqueo)
# --------------------------------------------------------
def scrape_indeed():
    url = "https://es.indeed.com/jobs?q=junior+developer+it+ciberseguridad&l=Huelva"

    r = safe_request(url)
    if not r:
        print("Indeed bloqueó el acceso.")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    offers = []

    for job in soup.select(".job_seen_beacon"):
        title_elem = job.select_one("h2 span")
        if not title_elem:
            continue

        title = title_elem.text.lower()
        if not any(k in title for k in KEYWORDS):
            continue

        company = job.select_one(".companyName")
        location = job.select_one(".companyLocation")
        salary = job.select_one(".salary-snippet")
        link_elem = job.select_one("a")

        offers.append({
            "source": "Indeed",
            "title": title_elem.text.strip(),
            "company": company.text.strip() if company else "No indicada",
            "location": location.text.strip() if location else "No indicada",
            "salary": salary.text.strip() if salary else "No especificado",
            "link": "https://es.indeed.com" + link_elem["href"] if link_elem else ""
        })

    return offers

# --------------------------------------------------------
# SCRAPER TECNOEMPLEO (con anti-bloqueo)
# --------------------------------------------------------
def scrape_tecnoempleo():
    url = "https://www.tecnoempleo.com/busqueda-empleo.php?pr=Huelva&te=remoto"

    r = safe_request(url)
    if not r:
        print("TecnoEmpleo bloqueó el acceso.")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    offers = []

    for job in soup.select(".oferta"):
        title = job.select_one(".titulo_oferta").text.lower()
        if not any(k in title for k in KEYWORDS):
            continue

        company = job.select_one(".empresa_oferta").text.strip()
        salary_elem = job.select_one(".salario")
        link = "https://www.tecnoempleo.com" + job.select_one("a")["href"]

        offers.append({
            "source": "TecnoEmpleo",
            "title": job.select_one(".titulo_oferta").text.strip(),
            "company": company,
            "location": "Huelva / Remoto",
            "salary": salary_elem.text.strip() if salary_elem else "No especificado",
            "link": link
        })

    return offers

# --------------------------------------------------------
# TABLA HTML
# --------------------------------------------------------
def build_html_table(items):
    if not items:
        return "<p>No se encontraron ofertas junior hoy.</p>"

    html = """
    <h2>Ofertas JUNIOR encontradas</h2>
    <table border='1' cellpadding='6' cellspacing='0'>
        <tr style='background:#eee'>
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
# ENVIAR EMAIL
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
# MAIN
# --------------------------------------------------------
def main():
    print("Buscando ofertas JUNIOR con anti-bloqueo...")

    google = search_google_jobs()
    linkedin = search_linkedin_jobs()
    indeed = scrape_indeed()
    tecno = scrape_tecnoempleo()

    all_jobs = google + linkedin + indeed + tecno

    print("Google:", len(google))
    print("LinkedIn:", len(linkedin))
    print("Indeed:", len(indeed))
    print("TecnoEmpleo:", len(tecno))
    print("TOTAL:", len(all_jobs))

    html = build_html_table(all_jobs)
    send_email(html)


if __name__ == "__main__":
    main()
