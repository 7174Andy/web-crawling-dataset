from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
import time
import keyboard

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(executable_path="C:\ChromeDesktop\chromedriver-win64\chromedriver.exe", options=options)

def get_products_links(wd, delay, max_products, url ):
    """Get the links for the products from the website

    Args:
        wd (Webdriver): The webdriver to be used
        delay (int): The delay between each scroll
        max_products (int): The maximum number of products to be scraped
    
    Returns:
        list: A list of links of the products
    """
    
    # Open the website (assume that the website contains the products)
    wd.get(url)
    handling_accept_cookies(wd, url)
    
    
    links = []
    
    while len(links) < max_products:
        time.sleep(delay)
        elements = wd.find_elements(By.CLASS_NAME, "item-heading")
        for element in elements:
            links.append(element.find_elements(By.TAG_NAME, "a")[0].get_attribute("href"))
            if len(links) >= max_products:
                break
    return links


def get_product_names(wd, links):
    """Gets the name of each product in the given links

    Args:
        wd (Webdriver): The webdriver to be used
        links (list): List of links to analyze

    Returns:
        list: list of product names
    """
    products_names = []
    for link in links:
        time.sleep(2)
        wd.get(link)
        names = wd.find_elements(By.TAG_NAME, "hm-product-name")
        name = names[0].get_attribute("product-name")
        products_names.append(name)
    
    return products_names
    

# TODO: Find a way to download a specific image (just the images with the garment and the specific poses)
def get_images_from_url(wd, links, delay, download_path, products):
    for link, product in zip(links, products):
        time.sleep(delay)
        wd.get(link)
        i = 1
        elements = wd.find_elements(By.CLASS_NAME, "pdp-image")
        for element in elements:
            children = element.find_elements_by_tag_name("img")
            for image in children:
                url = image.get_attribute("src")
                try:
                    image_content = requests.get(url).content
                    image_file = io.BytesIO(image_content)
                    image = Image.open(image_file).convert("RGB")
                    file_path = f"{download_path}{product} {i}.jpeg"
                    with open(file_path, "wb") as f:
                        image.save(f, "jpeg")
                    print("Success")
                    
                except Exception as e:
                    print("FAILED - ", e)
                i += 1

def handling_accept_cookies(wd, url):
    wd.get(url)
    element = wd.find_element_by_id("onetrust-accept-btn-handler")
    if element:
        element.click()
        time.sleep(3)
        keyboard.press_and_release('esc')

def main():
    url = "https://www2.hm.com/en_us/men/new-arrivals/view-all.html"
    links = get_products_links(wd=driver, delay=5, max_products=20, url=url)
    products = get_product_names(wd=driver, links=links)
    print(f"Done! Got {len(products)} products:")
    time.sleep(5)
    print(products)
    print(links)
    get_images_from_url(wd=driver, links=links, delay=5, download_path="./imgs/", products=products)

    driver.quit()

if __name__ == "__main__":
    main()