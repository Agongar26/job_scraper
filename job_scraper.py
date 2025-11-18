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
    "developer", "desarrollador", "programador", "software",
    "java", "kotlin", "android",
    "it", "soporte",
    "ciberseguridad", "cybersecurity", "soc",
    "security", "analista", "ingeniero",
    "backend", "frontend", "fullstack"
]

LOCATIONS = [
    "Huelva, Spain",
    "Andalucía, Spain",
    "Spain"
]

SEARCH_QUERIES = [
    "developer",
    "programador",
    "cybersecurity",
    "it jobs",
    "python developer",
    "java developer"
]


def serpapi_request(engine, query, location):
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": engine,
            "q": query if engine == "google_jobs" else None,
            "keywords": query if engine == "linkedin_jobs" else None,
            "location": location,
            "api_key": SERPAPI_KEY
        }
        params = {k: v for k, v in params.items() if v is not None}

        r = requests.get(url, params=params)
        data = r.json()

        return data
    except Exception as e:
        print(f"Error SerpAPI: {e}")
        return {}


def parse_google_jobs(data):
    offers = []
    jobs = data.get("jobs_results", [])

    for job in jobs:
        title = job.get("title", "")
        if not any(k in title.lower() for k in KEYWORDS):
            continue

        offers.append((
            title,
            job.get("company_name", "Desconocida"),
            job.get("location", "No indicada"),
            job.get("related_links", [{}])[0].get("link", "")
        ))

    return offers


def parse_linkedin_jobs(data):
    offers = []
    jobs = data.get("jobs_results", [])

    for job in jobs:
        title = job.get("title", "")
        if not any(k in title.lower() for k in KEYWORDS):
            continue

        offers.append((
            title,
            job.get("company", {}).get("name", "Desconocida"),
            job.get("location", "No indicada"),
            job.get("job_url", "")
        ))

    return offers


def scrape_jobs():
    all_offers = set()

    for loc in LOCATIONS:
        for q in SEARCH_QUERIES:

            # Google Jobs
            data = serpapi_request("google_jobs", q, loc)
            google_offers = parse_google_jobs(data)
            for o in google_offers:
                all_offers.add(o)

            # LinkedIn Jobs
            data = serpapi_request("linkedin_jobs", q, loc)
            linkedin_offers = parse_linkedin_jobs(data)
            for o in linkedin_offers:
                all_offers.add(o)

    return list(all_offers)


def build_html_table(data):
    if not data:
        return "<p>No se encontraron ofertas esta semana.</p>"

    table = """
    <h2>Ofertas encontradas (IT / Desarrollo / Ciberseguridad)</h2>
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


def main():
    print("Buscando ofertas (Google + LinkedIn)...")

    offers = scrape_jobs()
    print(f"Total ofertas encontradas: {len(offers)}")

    html = build_html_table(offers)
    send_email(html)


if __name__ == "__main__":
    main()
