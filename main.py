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
    chrome_options = webdriver.ChromeOptions()
    # Comentamos la opción headless para ver el navegador
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

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

def find_next_button(soup):
    """Busca el botón de siguiente página y retorna su URL"""
    print("\nDEBUG: Buscando botón siguiente...")
    
    # Método 1: Buscar por nav y aria-label
    pagination_nav = soup.find("nav", {"aria-label": "Paginación de los resultados de búsqueda"})
    if pagination_nav:
        print("DEBUG: Encontrado contenedor de paginación")
        
        # Imprimir todos los botones y enlaces encontrados
        all_buttons = pagination_nav.find_all(["button", "a"])        
        # Intentar diferentes métodos para encontrar el botón siguiente
        next_button = (
            pagination_nav.find("a", {"aria-label": "Siguiente"}) or
            pagination_nav.find("button", {"aria-label": "Siguiente"}) or
            pagination_nav.find("a", string="Siguiente") or
            pagination_nav.find("button", string="Siguiente")
        )
        
        if next_button:
            if 'href' in next_button.attrs:
                next_url = "https://www.airbnb.com" + next_button['href']
                print(f"DEBUG: URL siguiente encontrada: {next_url}")
                return next_url
            else:
                print("DEBUG: Botón encontrado pero sin atributo href")
                print("DEBUG: Atributos del botón:", next_button.attrs)
    else:
        print("DEBUG: No se encontró el contenedor de paginación principal")
        # Buscar cualquier elemento de navegación
        all_navs = soup.find_all("nav")
        print(f"DEBUG: Navegaciones encontradas: {len(all_navs)}")
        for nav in all_navs:
            print(f"DEBUG: Nav con clases: {nav.get('class')}, aria-label: {nav.get('aria-label')}")
    
    return None

def fetch_airbnb_data(base_url):
    """Obtiene los datos de todas las páginas de búsqueda de Airbnb"""
    all_listing_urls = []
    driver = configure_driver()
    
    try:
        print("\n=== FASE 1: ANÁLISIS INICIAL ===")
        print("→ Accediendo a la página principal...")
        driver.get(base_url)
        time.sleep(5)
        
        print("→ Buscando número total de alojamientos...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        total_listings = get_total_listings(soup)
        
        if total_listings:
            total_pages = calculate_total_pages(total_listings)
            print(f"✓ Encontrados {total_listings} alojamientos")
            print(f"✓ Se procesarán {total_pages} páginas")
        else:
            print("! No se pudo determinar el número total. Usando 4 páginas por defecto")
            total_pages = 4
        
        print("\n=== FASE 2: RECOLECCIÓN DE URLS ===")
        for page in range(total_pages):
            print(f"\n--- Página {page + 1} de {total_pages} ---")
            current_url = f"{base_url}&items_offset={page * 18}"
            
            print("→ Cargando página...")
            driver.get(current_url)
            time.sleep(5)

            print("→ Haciendo scroll para cargar todos los elementos...")
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            items = soup.find_all("div", {"data-testid": "card-container"})
            
            if not items:
                print("! No se encontraron alojamientos en esta página")
                break
            
            new_urls = 0
            for item in items:
                url = get_listing_url(item)
                if url and url not in all_listing_urls:
                    all_listing_urls.append(url)
                    new_urls += 1
            
            print(f"✓ Encontrados {len(items)} alojamientos")
            print(f"✓ Nuevas URLs añadidas: {new_urls}")
            print(f"✓ Total acumulado: {len(all_listing_urls)}")
            
        print(f"\n=== RESUMEN FINAL ===")
        print(f"✓ Total de URLs únicas recolectadas: {len(all_listing_urls)}")
        
        return all_listing_urls, driver
        
    except Exception as e:
        print("\n!!! ERROR !!!")
        print(f"→ {str(e)}")
        return [], driver

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

def get_total_listings(soup):
    """Obtiene el número total de alojamientos disponibles"""
    try:
        # Buscar por la clase específica que encontramos
        total_element = soup.find("span", {"class": "a8jt5op"})
        if total_element:
            # Extraer el número usando regex
            number = re.search(r'(\d+)\s+alojamientos?', total_element.text)
            if number:
                total = int(number.group(1))
                print(f"DEBUG: Total de alojamientos encontrados: {total}")
                return total
            
        # Método alternativo: buscar en el h1
        h1_element = soup.find("h1", {"class": "hpipapi"})
        if h1_element:
            number = re.search(r'(\d+)\s+alojamientos?', h1_element.text)
            if number:
                total = int(number.group(1))
                print(f"DEBUG: Total de alojamientos encontrados (h1): {total}")
                return total
                
        print("No se pudo encontrar el número de alojamientos")
        return None
        
    except Exception as e:
        print(f"Error al obtener total de alojamientos: {e}")
        return None

def calculate_total_pages(total_listings, listings_per_page=18):
    """Calcula el número total de páginas necesarias"""
    return -(-total_listings // listings_per_page)  # Redondeo hacia arriba

if __name__ == "__main__":
    search_url = "https://www.airbnb.com.ar/s/Microcentro/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2025-02-01&monthly_length=3&monthly_end_date=2025-05-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&checkin=2025-01-16&checkout=2025-01-19&adults=2&source=structured_search_input_header&search_type=user_map_move&query=Microcentro&place_id=ChIJoZjYMB7LvJUR-lIvu29mQ6w&search_mode=regular_search&price_filter_num_nights=3&ne_lat=-34.593555291120474&ne_lng=-58.371582208467714&sw_lat=-34.617006214929525&sw_lng=-58.39181891193829&zoom=15.175922923838742&zoom_level=15.175922923838742&search_by_map=true"

    print("Iniciando scraping de Airbnb...")
    listing_urls, driver = fetch_airbnb_data(search_url)

    try:
        if listing_urls:
            print(f"\nEncontrados {len(listing_urls)} URLs totales para procesar")
            
            all_listings_data = []
            for i, url in enumerate(listing_urls, 1):
                print(f"\nProcesando listado {i}/{len(listing_urls)}")
                listing_data = scrape_listing(url)
                if listing_data:
                    listing_data['link'] = url
                    all_listings_data.append(listing_data)
                    print(f"Listado {i} procesado exitosamente")
                else:
                    print(f"Error al procesar listado {i}")
                
                # Pausa entre listados para evitar bloqueos
                time.sleep(2)
            
            print(f"\nProcesados {len(all_listings_data)} listados exitosamente")
            save_to_csv(all_listings_data)
            
    except Exception as e:
        print(f"Error en el proceso: {e}")
    finally:
        if driver:
            driver.quit()