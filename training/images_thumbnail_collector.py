import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import urllib
import time

class_index = 'passport'
url = "https://www.google.com/search?q=face+passport+pictures&client=ubuntu-sn&sca_esv=b4e69a3c06901caf&channel=fs&udm=2&biw=1034&bih=662&ei=LNr6Z8PAPP2J9u8PiIGT6Q8&ved=0ahUKEwjDhuSct9OMAxX9hP0HHYjAJP0Q4dUDCBI&uact=5&oq=face+passport+pictures&gs_lp=EgNpbWciFmZhY2UgcGFzc3BvcnQgcGljdHVyZXNI4yBQ-wxY0hpwAXgAkAEAmAHiAqABpASqAQcwLjEuMC4xuAEDyAEA-AEBmAIAoAIAmAMAiAYBkgcAoAdmsgcAuAcA&sclient=img"
# Configure WebDriver
driver_path = "chromedriver-linux64/chromedriver"  # Replace with the actual path to the downloaded driver
service = Service(driver_path)
# Launch Browser and Open the URL
counter = 0
numOfPics = 1000
driver = uc.Chrome(service=service)

# Create url variable containing the webpage for a Google image search.
driver.get(url)

input("Press Enter to proceed")
img_results = driver.find_elements(By.XPATH, "//img[contains(@class, 'YQ4gaf')]")

image_urls = []
for img in img_results:
    image_urls.append(img.get_attribute('src'))

folder_path = f'locations/{class_index}/' # change your destination path here

for i in range(numOfPics):
    counter += 1
    try:
        urllib.request.urlretrieve(str(image_urls[i]), f"{folder_path}{counter}")
    except Exception as e:
       print(e)

driver.quit()


        
