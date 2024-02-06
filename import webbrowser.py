#BACIU PETRU-RARES

from unittest import result

# Extrage informatii din documente de tip HTML si XML 
from bs4 import BeautifulSoup

# Utilizat pentru a trimite solicitari catre servere web 
import requests

import configparser # Modul pentru gestionarea configurarii

import argparse  # Importam modulul argparse pentru a procesa argumentele de linie de comanda

"""Modulul time ofera functionalitati legate de masurare a timpului."""
import time
"""Modulul functools furnizeaza functionalitati pentru lucrul cu functii si obiecte invocabile."""
import functools
"""Modulul smtplib ofera functionalitati pentru trimiterea de e-mailuri folosind protocolul SMTP."""
import smtplib
"""Modulul email.mime.text ofera clase pentru manipularea continutului text in cadrul mesajelor MIME."""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time

        if kwargs.get('log', False):
            print(f'Timpul necesar pentru {func.__name__}: {elapsed_time} secunde')
        return result
    
    return wrapper

url= "https://www.olx.ro/"

def send_email(to_address, subject, body):
    """
    Trimite un e-mail utilizand SMTP.

    :param to_address: Adresa destinatarului
    :param subject: Subiectul e-mailului
    :param body: Continutul e-mailului
    """
    # Citirea configurarii pentru e-mail din fisierul config.ini
    email_config = configparser.ConfigParser()
    email_config.read('config.ini')
    smtp_server = email_config['Email']['smtp_server']
    smtp_port = int(email_config['Email']['smtp_port'])
    smtp_username = email_config['Email']['smtp_username']
    smtp_password = email_config['Email']['smtp_password']
    from_address = email_config['Email']['from_address']

    # Crearea obiectului MIMEText
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address

    # Trimiterea e-mailului prin intermediul serverului SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_address, to_address, msg.as_string())

url = "https://www.olx.ro/"

@timing_decorator
def get_title_and_description(url, log=False):
    """
    Realizeaza web scraping pentru a obtine titlul si descrierea meta a unei pagini.

    :param url: URL-ul paginii web
    :param log: Un parametru boolean pentru a specifica daca sa se genereze log-uri
    :return: Tuplu continand titlul si descrierea meta
    """
    try:
        if log:
            print(f"Accesare URL: {url}")

        # Descarca continutul paginii web
        response = requests.get(url)
        response.raise_for_status()  # Arunca o exceptie pentru erori HTTP

        # Foloseste BeautifulSoup pentru a analiza HTML-ul
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extrage titlul paginii si descrierea meta
        title = soup.title.text if soup.title else "Titlu indisponibil"
        description_meta = soup.find('meta', attrs={'name': 'description'})
        description = description_meta.get('content') if description_meta else "Descriere indisponibila"

        return title, description
    except requests.exceptions.RequestException as e:
        if log:
            print(f"Eroare la accesarea URL-ului: {e}")
        return None, None

@timing_decorator
def get_olx_results(url, keywords, log=False):
    """
    Realizeaza web scraping pe OLX.ro si returneaza o lista de dictionare cu titluri si preturi.

    :param url: URL-ul OLX.ro
    :param keywords: Cuvintele cheie pentru cautare
    :param log: Un parametru boolean pentru a specifica daca sa se genereze log-uri
    :return: Lista de dictionare cu titluri si preturi
    """
    try:
        if log:
            print(f"Cautare OLX.ro cu cuvintele cheie: {keywords}")

        # Construieste URL-ul de cautare pe OLX.ro
        search_url = f"{url}q-{'+'.join(keywords.split())}/"

        # Descarca continutul paginii de rezultate de cautare
        response = requests.get(search_url)
        html_content = response.text

        # Foloseste BeautifulSoup pentru a analiza HTML-ul
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extrage titlurile si preturile anunturilor
        titles = [title.text.strip() for title in soup.find_all('a', class_='marginright5 link')]
        prices = [price.text.strip() for price in soup.find_all('p', class_='price')]

        # Construieste o lista de dictionare cu titluri si preturi
        results = [{"Title": title, "Price": price} for title, price in zip(titles, prices)]

        return results
    except requests.exceptions.RequestException as e:
        if log:
            print(f"Eroare la cautarea OLX.ro: {e}")
        return None

if __name__ == "__main__":
    # Configurarea argumentelor de linie de comanda
    parser = argparse.ArgumentParser(description="Script pentru verificarea preturilor pe OLX.ro")
    parser.add_argument("-log", action="store_true", help="Activeaza afisarea log-urilor")

    # Parsarea argumentelor
    args = parser.parse_args()

    # Citirea configurarii din fisierul config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    olx_url = config['OLX']['url']
    keywords = config['OLX']['keywords']

    # Obtine si printeaza titlul si descrierea meta
    title, description = get_title_and_description(olx_url, log=args.log)
    print(f"Titlu pagina OLX: {title}")
    print(f"Descriere OLX: {description}")

    # Obtine rezultatele configurarii din fisierul config.ini
    results = get_olx_results(olx_url, keywords, log=args.log)
    if results is not None:
        sorted_results = sorted(results, key=lambda x: float(x['Price'].replace("Lei", "").replace(",", "")))

        # Afiseaza titlurile si preturile ordonate
        print("Anunturile OLX.ro pentru keywords: 'iphone 15 pro', ordonate dupa pret:")
        for result in sorted_results:
            print(f"Titlu: {result['Title']}, Pret: {result['Price']}")


# Functia pentru trimiterea de e-mail
def send_email(subject, body, recipient):
    """
    Trimite un e-mail utilizand protocolul SMTP.

    :param to_address: Adresa destinatarului.
    :param subject: Subiectul e-mailului.
    :param body: Continutul e-mailului.
    """

    email_config = config['Email']
    smtp_server = email_config['smtp_server']
    smtp_port = int(email_config['smtp_port'])
    smtp_username = email_config['smtp_username']
    smtp_password = email_config['smtp_password']

    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient, message.as_string())

# Functia pentru verificarea scaderii pretului
def check_price_drop(url, keywords, threshold, recipient, log=False):
    """
    Verifica daca pretul produsului a scazut sub o anumita valoare si trimite un e-mail in acest caz.

    :param url: URL-ul OLX.ro.
    :param keywords: Cuvintele cheie pentru cautare.
    :param threshold: Valoarea minima a pretului acceptata.
    :param recipient: Adresa destinatarului notificarii prin e-mail.
    :param log: Un parametru boolean pentru a specifica daca sa se genereze log-uri.
    :return: Lista de dictionare cu titluri si preturi.
    """

    results = get_olx_results(url, keywords, log=log)

    if results is not None:
        lowest_price = min(float(result['Price'].replace("Lei", "").replace(",", "")) for result in results)

        if lowest_price < threshold:
            subject = "Notificare OLX - Pret scazut"
            body = f"Pretul minim gasit ({lowest_price} Lei) a scazut sub valoarea X ({threshold} Lei)."
            
            send_email(subject, body, recipient)
            print("Notificare e-mail trimisa!")

    return results

# Configurarea argumentelor de linie de comanda
parser = argparse.ArgumentParser(description="Script pentru verificarea preturilor pe OLX.ro")
parser.add_argument("-log", action="store_true", help="Activeaza afisarea log-urilor")

# Parsarea argumentelor
args = parser.parse_args()

# Citirea configurarii din fisierul config.ini
config = configparser.ConfigParser()
config.read('config.ini')
olx_url = config['OLX']['url']
keywords = config['OLX']['keywords']

# Obtine si printeaza titlul si descrierea meta
title, description = get_title_and_description(olx_url, log=args.log)
print(f"Titlu pagina OLX: {title}")
print(f"Descriere OLX: {description}")

# Obtine rezultatele configurarii din fisierul config.ini
results = get_olx_results(olx_url, keywords, log=args.log)
if results is not None:
    sorted_results = sorted(results, key=lambda x: float(x['Price'].replace("Lei", "").replace(",", "")))

    # Afiseaza titlurile si preturile ordonate
    print("Anunturile OLX.ro pentru keywords: 'iphone 15 pro', ordonate dupa pret:")
    for result in sorted_results:
        print(f"Titlu: {result['Title']}, Pret: {result['Price']}")

# Verifica daca pretul a scazut sub o anumita valoare si trimite email daca da
check_price_drop(olx_url, keywords, 1000, 'destinatar@example.com', log=args.log)