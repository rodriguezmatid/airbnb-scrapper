from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import os
import re
import csv

def configure_driver():
    """Configura y retorna el driver de Selenium"""
    options = webdriver.ChromeOptions()
    # Comentar headless para ver la interacción
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

def save_debug_sections(soup, debug_dir="debug_sections"):
    """Guarda diferentes secciones del HTML en archivos separados"""
    # Crear directorio si no existe
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
        
    sections = {
        "full_page": soup,
        "title": soup.find("div", {"data-section-id": "TITLE_DEFAULT"}),
        # "rating": soup.find("div", {"class": "a8jhwcl"}),
        "host": soup.find("div", {"class": "s1m4e316"}),
        "reviews": soup.find("div", {"data-section-id": "REVIEWS_DEFAULT"}),
        "price": soup.find("div", {"data-section-id": "BOOK_IT_SIDEBAR"}),
        "amenities": soup.find("div", {"data-section-id": "AMENITIES_DEFAULT"}),
        "description": soup.find("div", {"data-section-id": "DESCRIPTION_DEFAULT"}),
        "capacity": soup.find("div", {"class": "o1kjrihn"})
    }
    
    # Guardar cada sección en un archivo separado
    for name, section in sections.items():
        if section:
            filename = os.path.join(debug_dir, f"{name}.html")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(section.prettify())
            print(f"Guardado {filename}")

def scrape_listing(url):
    """Analiza un listado específico de Airbnb"""
    driver = configure_driver()
    try:
        print(f"\nAnalizando listado: {url}")
        driver.get(url)
        time.sleep(5)  # Esperar a que cargue la página
        
        # Intentar cerrar el modal si existe
        try:
            print("Buscando modal para cerrar...")
            close_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Close']"))
            )
            print("Modal encontrado, cerrándolo...")
            close_button.click()
            print("Modal cerrado")
            time.sleep(1)
        except:
            print("No se encontró modal para cerrar o ya estaba cerrado")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        save_debug_sections(soup)
        
        # Extraer información
        listing_data = {
            **extract_rating_info(soup),
            **extract_capacity_info(soup),
            **extract_years_as_host(soup),
            **extract_price_info(soup, driver)
        }
        
        return listing_data
        
    except Exception as e:
        print(f"Error al analizar el listado: {e}")
        return None
    finally:
        driver.quit()



def extract_rating_info(soup):
    """Extrae información de rating y reviews"""
    reviews_section = soup.find("div", {"data-section-id": "REVIEWS_DEFAULT"})
    if not reviews_section:
        print("No se encontró la sección de reviews")
        return {
            "reviews": "0",
            "rating": "0"
        }
    
    info = {
        "reviews": "0",
        "rating": "0"
    }
    
    try:
        # Buscar el título que contiene el rating y reviews
        rating_title = reviews_section.find("h2")
        if rating_title:
            # Extraer rating (ejemplo: "5.0 · 3 reviews")
            rating_match = re.search(r'(\d+\.\d+)', rating_title.text)
            if rating_match:
                info["rating"] = rating_match.group(1)
            
            # Extraer número de reviews
            reviews_match = re.search(r'(\d+)\s+reviews?', rating_title.text)
            if reviews_match:
                info["reviews"] = reviews_match.group(1)
    
    except Exception as e:
        print(f"Error al extraer rating/reviews: {e}")
    
    print("\nInformación de rating:")
    print(f"Rating: {info['rating']}")
    print(f"Reviews: {info['reviews']}")
    
    return info

def extract_capacity_info(soup):
    """Extrae información sobre la capacidad del alojamiento"""
    capacity_section = soup.find("div", {"class": "o1kjrihn"})
    if not capacity_section:
        print("No se encontró la sección de capacidad")
        return {
            "guests": "No disponible",
            "bedrooms": "No disponible",
            "beds": "No disponible",
            "baths": "No disponible"
        }
    
    # Buscar todos los li que contienen la información
    items = capacity_section.find_all("li", {"class": "l7n4lsf"})
    capacity = {
        "guests": "No disponible",
        "bedrooms": "No disponible",
        "beds": "No disponible",
        "baths": "No disponible"
    }
    
    for item in items:
        # Limpiar el texto eliminando los puntos y espacios extra
        text = item.get_text(separator=' ', strip=True).lower()
        text = text.replace('·', '').strip()
        
        if "guest" in text:
            capacity["guests"] = text.split()[0]
        elif "bedroom" in text:
            capacity["bedrooms"] = text.split()[0]
        elif "bed" in text and "bedroom" not in text:  # Para evitar contar "bedroom" como "bed"
            capacity["beds"] = text.split()[0]
        elif "bath" in text:
            capacity["baths"] = text.split()[0]
    
    print("\nInformación de capacidad:")
    for key, value in capacity.items():
        print(f"{key}: {value}")
    
    return capacity

def extract_years_as_host(soup):
    """Extrae información sobre los años como host"""
    host_section = soup.find("div", {"class": "s1m4e316"})
    if not host_section:
        print("No se encontró la sección de host")
        return {
            "years_hosting": "0"
        }
    
    # Buscar el span específico que contiene los años como host
    years = host_section.find("span", {"data-testid": "Years hosting-stat-heading"})
    years_hosting = years.text.strip() if years else "0"
    
    info = {
        "years_hosting": years_hosting
    }
    
    print("\nInformación de host:")
    print(f"Años como host: {info['years_hosting']}")
    
    return info

def extract_price_info(soup, driver):
    """Extrae información de precios del listado"""
    prices = {
        "price_original": "0",
        "price_discount": "0",
        "nights": "0",
        "total_nights": "0",
        "special_offer": "0",
        "cleaning_fee": "0",
        "service_fee": "0",
        "total": "0"
    }
    
    try:
        # Buscar el contenedor de precios
        price_section = soup.find("div", {"data-section-id": "BOOK_IT_SIDEBAR"})
        if price_section:
            # Obtener precio por noche
            price_display = price_section.find("div", {"class": "_1jo4hgw"})
            if price_display:
                discount_price = price_display.find("span", {"class": "_11jcbg2"})
                if discount_price:
                    prices["price_discount"] = re.search(r'\$(\d+)', discount_price.text).group(1)
                
                original_price = price_display.find("span", {"class": "_1aejdbt"})
                if original_price:
                    prices["price_original"] = re.search(r'\$(\d+)', original_price.text).group(1)
                elif prices["price_discount"] != "0":
                    prices["price_original"] = prices["price_discount"]

            # Buscar el desglose de precios
            price_breakdown = price_section.find_all("div", {"class": "_14omvfj"})
            if price_breakdown:
                for item in price_breakdown:
                    text = item.get_text().lower()
                    amount_span = item.find("span", {"class": ["_1k4xcdh", "_1rc8xn5"]})
                    if amount_span:
                        amount_text = amount_span.text.strip()
                        is_negative = "-" in amount_text or amount_span.get("class") == ["_1rc8xn5"]
                        amount = re.search(r'\$(\d+)', amount_text).group(1)
                        amount = f"-{amount}" if is_negative else amount
                    else:
                        amount = "0"
                    
                    if "nights" in text:
                        prices["nights"] = re.search(r'x\s*(\d+)\s*nights?', text).group(1)
                        prices["total_nights"] = amount
                    elif "special offer" in text:
                        prices["special_offer"] = f"-{amount.replace('-', '')}"
                    elif "cleaning fee" in text:
                        prices["cleaning_fee"] = amount
                    elif "service fee" in text:
                        prices["service_fee"] = amount

            # Buscar precio total
            total_text = price_section.find("div", {"class": "_1vk118j"})
            if not total_text:  # Si no lo encuentra con la primera clase, intentar con otra
                total_text = price_section.find("div", {"class": "_182z7aq1"})
            
            if total_text:
                total_match = re.search(r'\$(\d+)', total_text.text)
                if total_match:
                    prices["total"] = total_match.group(1)
                else:
                    # Buscar en elementos hijos si no encuentra directamente
                    total_span = total_text.find("span", {"class": "_j1kt73"})
                    if total_span:
                        total_match = re.search(r'\$(\d+)', total_span.text)
                        if total_match:
                            prices["total"] = total_match.group(1)

    except Exception as e:
        print(f"Error al extraer precios: {e}")
    
    print("\nInformación de precios encontrada:")
    for key, value in prices.items():
        print(f"{key}: {value}")
    
    return prices

def get_listing_url(item):
    """Extrae el enlace del listado"""
    link_element = item.find("a", recursive=False)
    if link_element and 'href' in link_element.attrs:
        return "https://www.airbnb.com" + link_element['href']
    return None

def parse_listings(soup):
    """Procesa todos los listados encontrados en la página"""
    listing_urls = []
    items = soup.find_all("div", {"data-testid": "card-container"})
    print(f"Encontrados {len(items)} listados para procesar")
    
    for item in items:
        try:
            link = get_listing_url(item)
            if link:
                listing_urls.append(link)
        except Exception as e:
            print(f"Error extrayendo URL: {e}")
            continue
    
    return listing_urls

def fetch_airbnb_data(url):
    """Obtiene los datos de la página de búsqueda de Airbnb"""
    driver = configure_driver()
    try:
        print(f"Accediendo a URL de búsqueda: {url}")
        driver.get(url)
        time.sleep(5)

        # Hacer scroll para cargar más resultados
        for i in range(3):
            print(f"Scroll {i+1}/3...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        return soup, driver
    except Exception as e:
        print(f"Error al obtener datos de búsqueda: {e}")
        driver.quit()
        return None, None

def save_to_csv(listings_data, filename="airbnb_data.csv"):
    """Guarda los datos de los listados en un archivo CSV"""
    if not listings_data:
        print("No hay datos para guardar")
        return False
        
    # Definir las columnas en el orden deseado
    fieldnames = [
        'id', 'title', 'link', 'rating', 'reviews', 
        'guests', 'bedrooms', 'beds', 'baths', 
        'years_hosting', 'price_original', 'price_discount',
        'nights', 'total_nights', 'special_offer',
        'cleaning_fee', 'service_fee', 'total'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, listing in enumerate(listings_data, 1):
                # Crear una nueva fila con el ID y asegurarse de que todos los campos existan
                row = {
                    'id': i,
                    'link': listing.get('link', 'N/A'),
                    'rating': listing.get('rating', '0'),
                    'reviews': listing.get('reviews', '0'),
                    'guests': listing.get('guests', '0'),
                    'bedrooms': listing.get('bedrooms', '0'),
                    'beds': listing.get('beds', '0'),
                    'baths': listing.get('baths', '0'),
                    'years_hosting': listing.get('years_hosting', '0'),
                    'price_original': listing.get('price_original', '0'),
                    'price_discount': listing.get('price_discount', '0'),
                    'nights': listing.get('nights', '0'),
                    'total_nights': listing.get('total_nights', '0'),
                    'special_offer': listing.get('special_offer', '0'),
                    'cleaning_fee': listing.get('cleaning_fee', '0'),
                    'service_fee': listing.get('service_fee', '0'),
                    'total': listing.get('total', '0')
                }
                writer.writerow(row)
        
        print(f"\nDatos guardados exitosamente en {filename}")
        return True
        
    except Exception as e:
        print(f"Error al guardar el CSV: {e}")
        return False

if __name__ == "__main__":
    # URL de búsqueda
    search_url = "https://www.airbnb.com.ar/s/Puerto-Madero--Buenos-Aires/homes?place_id=ChIJiQPXwtk0o5URj2cW455eew4&refinement_paths%5B%5D=%2Fhomes&checkin=2025-01-08&checkout=2025-01-12&date_picker_type=calendar&adults=1&search_type=user_map_move&query=Puerto%20Madero%2C%20Buenos%20Aires&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2025-01-01&monthly_length=3&monthly_end_date=2025-04-01&search_mode=regular_search&price_filter_input_type=0&price_filter_num_nights=4&channel=EXPLORE&ne_lat=-34.61036890486259&ne_lng=-58.35453103477175&sw_lat=-34.621341000508245&sw_lng=-58.36400048371502&zoom=16.27154484177234&zoom_level=16.27154484177234&search_by_map=true"

    print("Iniciando scraping de Airbnb...")
    soup, driver = fetch_airbnb_data(search_url)

    try:
        if soup:
            listing_urls = parse_listings(soup)
            print(f"\nEncontrados {len(listing_urls)} URLs para procesar")
            
            all_listings_data = []
            for i, url in enumerate(listing_urls, 1):
                print(f"\nProcesando listado {i}/{len(listing_urls)}")
                listing_data = scrape_listing(url)
                if listing_data:
                    listing_data['link'] = url  # Agregar el URL al diccionario de datos
                    all_listings_data.append(listing_data)
                    print(f"Listado {i} procesado exitosamente")
                else:
                    print(f"Error al procesar listado {i}")
            
            print(f"\nProcesados {len(all_listings_data)} listados exitosamente")
            
            # Guardar los datos en CSV
            save_to_csv(all_listings_data)
            
    except Exception as e:
        print(f"Error en el proceso: {e}")
    finally:
        if driver:
            driver.quit()