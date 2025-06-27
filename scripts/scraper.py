from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import json

def get_css_selectors():
    """Returns a dictionary of CSS selectors for easier maintenance"""
    return {
        'REVIEW_CARD_SELECTOR': "div.jJc9Ad",  # The main container for a single review
        'REVIEW_TEXT_SELECTOR': "span.wiI7pd",  # The element containing the review text
        'RATING_SELECTOR': "span.kvMYJc",  # The element containing the star rating (as an aria-label)
        'TIME_AGO_SELECTOR': "span.rsqaWe",    # The element containing how long ago the review was posted
        'MORE_BUTTON_SELECTOR': "button.w8nwRe",  # The "See more" button for long reviews
        'SCROLLABLE_PANEL_SELECTOR': "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde"  # The panel that needs to be scrolled
    }

def scrape_maps_reviews(url, output_filename):
    """
    Automates scraping Google Maps reviews by scrolling and extracting data as it loads.

    This version extracts the review text, the star rating, and how long ago the
    review was posted (e.g., "8 months ago").

    Args:
        url (str): The Google Maps URL of the place to scrape reviews from.
        output_filename (str): The name of the JSON file to save the data to.
    """
    print("--- Starting Simplified Google Maps Review Scraper (with Timestamps) ---")
    print(f"Target URL: {url}")

    selectors = get_css_selectors()
    REVIEW_CARD_SELECTOR = selectors['REVIEW_CARD_SELECTOR']
    REVIEW_TEXT_SELECTOR = selectors['REVIEW_TEXT_SELECTOR']
    RATING_SELECTOR = selectors['RATING_SELECTOR']
    TIME_AGO_SELECTOR = selectors['TIME_AGO_SELECTOR']
    MORE_BUTTON_SELECTOR = selectors['MORE_BUTTON_SELECTOR']
    SCROLLABLE_PANEL_SELECTOR = selectors['SCROLLABLE_PANEL_SELECTOR']

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # comment this out if this shit is screwing up somewhere and you wanna see what its doing (very likely eventually!)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
   
    # Wait for the main page to load, especially the reviews button
    time.sleep(5)

    try:
        # Click the "Reviews" tab/button to navigate to the reviews section
        reviews_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Reviews']")
        reviews_button.click()
        print("Successfully clicked the 'Reviews' button.")
        # Wait for the reviews panel to load
        time.sleep(4)
    except NoSuchElementException:
        print("ERROR: Could not find the 'Reviews' button. The page structure might have changed.")
        driver.quit()
        return []

    try:
        # Find the scrollable reviews panel
        scrollable_div = driver.find_element(By.CSS_SELECTOR, SCROLLABLE_PANEL_SELECTOR)
        print("Found the scrollable review panel.")
    except NoSuchElementException:
        print("ERROR: Could not find the scrollable review panel. The script cannot proceed.")
        driver.quit()
        return []
       
    # --- Main Scraping Logic: Scroll, find new reviews, scrape, repeat ---
    review_data = []
    processed_review_elements = set() # Use the web element's ID to track processed reviews
    stagnant_scroll_attempts = 0

    while stagnant_scroll_attempts < 5: # Break if we scroll 5 times with no new reviews
        # Scroll to the bottom of the panel
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)  # Wait for new reviews to load

        # Find all currently loaded review card elements
        current_review_cards = driver.find_elements(By.CSS_SELECTOR, REVIEW_CARD_SELECTOR)
       
        new_reviews_found = False
        for card in current_review_cards:
            # The `id` attribute of a web element is a unique identifier for it in the current session.
            if card.id not in processed_review_elements:
                new_reviews_found = True
                processed_review_elements.add(card.id)
               
                # Scrape the data from this new card
                review_info = {}
               
                try:
                    # Click the 'More' button if it exists within the card to expand text
                    more_button = card.find_element(By.CSS_SELECTOR, MORE_BUTTON_SELECTOR)
                    more_button.click()
                    time.sleep(0.5) # Wait for text to expand
                except NoSuchElementException:
                    pass # No 'More' button, continue

                # Extract the review text
                try:
                    review_text = card.find_element(By.CSS_SELECTOR, REVIEW_TEXT_SELECTOR).text
                    review_info['text'] = review_text.strip()
                except NoSuchElementException:
                    review_info['text'] = "N/A"

                # Extract the rating
                try:
                    rating_element = card.find_element(By.CSS_SELECTOR, RATING_SELECTOR)
                    review_info['rating'] = rating_element.get_attribute('aria-label')
                except NoSuchElementException:
                    review_info['rating'] = "N/A"

                # Extract how long ago the review was posted
                try:
                    time_ago_element = card.find_element(By.CSS_SELECTOR, TIME_AGO_SELECTOR)
                    review_info['time_ago'] = time_ago_element.text.strip()
                except NoSuchElementException:
                    review_info['time_ago'] = "N/A"

                review_data.append(review_info)
       
        # Check if we should stop scrolling
        if new_reviews_found:
            stagnant_scroll_attempts = 0 # Reset counter if we found new reviews
            print(f"Scraped {len(review_data)} reviews so far...")
        else:
            stagnant_scroll_attempts += 1
            print(f"No new reviews found on this scroll. Stagnant attempts: {stagnant_scroll_attempts}/5")

    print(f"\nFinished scraping. Total unique reviews extracted: {len(review_data)}")

    #truth be told this is an abomination and should never have seen the light of day. but it works. 

    # --- Save the Extracted Data ---
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, indent=4, ensure_ascii=False)
        print(f"Review data saved successfully to '{output_filename}'")
    except Exception as e:
        print(f"ERROR: Could not save data to '{output_filename}'. Error: {e}")
       
    # --- Clean Up ---
    print("Closing WebDriver...")
    driver.quit()
    print("--- Scraping Process Finished ---")
   
    return review_data