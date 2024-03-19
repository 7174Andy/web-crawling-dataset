from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
import time
import keyboard
import os
import shutil

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument('--ignore-certificate-errors-spki-list')

driver = webdriver.Chrome(executable_path="C:\ChromeDesktop\chromedriver-win64\chromedriver.exe", options=options)

def get_products_links(wd, delay, max_products, url):
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
            if len(links) % 36 == 0:
                wd.execute_script("window.scrollTo(0, document.body.scrollHeight - 100);")
                time.sleep(2)
                wd.find_element(By.CLASS_NAME, "js-load-more").click()
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
        colors = wd.find_elements(By.CLASS_NAME, "product-input-label")
        
        name = names[0].get_attribute("product-name")
        color = colors[0].text
        products_names.append(f"{name} {color}")
    
    return products_names


def get_images_from_url(wd, links, delay, download_path, products):
    """Download the images from the given links

    Args:
        wd (webdriver): The webdriver to be used
        links (list): list of links to download the images
        delay (int): delay between each download
        download_path (str): directory to save the images
        products (list): name of the products
    """
    
    # setup necessary directories to store different poses
    setup_path(directory=download_path)
    
    time.sleep(3)
    
    product_count = 0
    
    for link, product in zip(links, products):
        time.sleep(delay)
        
        wd.get(link)
        
        # Specific pieces in the source URL of the image
        just_garment_url = "5BDESCRIPTIVESTILLLIFE"
        
        fronot_pose_url = "call=url[file:/product/main]"
        
        product_count += 1
        print(f"Downloading images for {product} {product_count}/{len(products)} in {link}...")
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
                    if (just_garment_url in url):
                        path = os.path.join(download_path, "garments")
                        file_path = f"{path}/{product} garment.jpeg"
                    elif (fronot_pose_url in url):
                        path = os.path.join(download_path, "front")
                        file_path = f"{path}/{product} front.jpeg"
                    else:
                        path = os.path.join(download_path, "random")
                        file_path = f"{path}/{product} {i}.jpeg"
                    with open(file_path, "wb") as f:
                        image.save(f, "jpeg")
                    
                except Exception as e:
                    print("FAILED - ", e)
                print(f"Images for {product} successfully Downloaded {i}/{len(elements)}")
                i += 1
        print("-----------------------------------------------")

def handling_accept_cookies(wd, url):
    """Automatically clicks on the accept cookies button

    Args:
        wd (webdriver): The webdriver to be used
        url (str): The url of the website
    """
    wd.get(url)
    element = wd.find_element_by_id("onetrust-accept-btn-handler")
    if element:
        element.click()
        time.sleep(3)
        keyboard.press_and_release('esc')

def setup_path(directory):
    try:
        os.mkdir(f"{directory}/garments")
        os.mkdir(f"{directory}/front")
        os.mkdir(f"{directory}/back")
        os.mkdir(f"{directory}/random")
        print("Directories created successfully")
        print("-----------------------------------------------")
    except FileExistsError as e:
        print("FAILED - ", e)

# TODO: get the tabs necessary for this dataset from H&M shopping mall website
def get_subgroups(wd, homepage):
    pass    

def clear():
    folder = "./imgs/"
    for dir in os.listdir(folder):
        path = os.path.join(folder, dir)
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        os.rmdir(path)

def main():
    clear()
    time.sleep(2)
    url = "https://www2.hm.com/en_us/men/new-arrivals/clothes.html"
    links = get_products_links(wd=driver, delay=5, max_products=3, url=url)
    products = get_product_names(wd=driver, links=links)
    time.sleep(5)
    print("-----------------------------------------------")
    print(f"{len(products)} products found")
    print("-----------------------------------------------")
    print(links)
    print("-----------------------------------------------")
        
    get_images_from_url(wd=driver, links=links, delay=5, download_path="./imgs/", products=products)

    driver.quit()
    
    print("`Comaplete!")
    

if __name__ == "__main__":
    main()