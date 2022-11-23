# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt
import pandas as pd

def scrape_all():
    #Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    
    news_title, news_p  = mars_news(browser)
        
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_name_url": hemisphere_images(browser),
        "last_modified": dt.datetime.now()
        
    }
    #Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #Convert the browser html to a soup object and thn quit the browser.
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    #Add try/except for errror handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_p

### JPL Space Images Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None    
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

### Mars Facts

def mars_facts():
    #Add try/except for error handling
    try:
        #Use 'read_html' to scrape the facts table into a dataframe.
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    
    except BaseException:
        return None
    
    #Assign columns and set index of dataframe.
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    return df.to_html()

### Mars Hemisphere

def hemisphere_images(browser):
    # Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    hem_images = browser.find_by_css('a.product-item h3')

    # Create a for loop to click through the links and find the sample anchor to return the href
    for index in range(len(hem_images)):
            
        # Find the elements on each loop to avoid a state element exception.
        browser.find_by_css('a.product-item h3')[index].click()
        hemisphere_data = scrape_hempisphere(browser.html)
        hemisphere_data['img_url'] = url + hemisphere_data['img_url']
        hemisphere_image_urls.append(hemisphere_data)
    
        #Finally we navigate back to the main page
        browser.back()

        # Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

def scrape_hempisphere(html_text):
    hemi_soup = soup(html_text, "html.parser")

    try:
        title_element = hemi_soup.find("h2", class_="title").get_text()
        sample_element = hemi_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title_element = None
        sample_element = None
    hemispheres_dict = {
        "title": title_element,
        "img_url": sample_element
    }
    return hemispheres_dict



if __name__ == "__main__":
    # If running as script, prein scrapped data
    print(scrape_all())

