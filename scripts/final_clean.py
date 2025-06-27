import json
import time
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# instead of manually making thousands of google map links, we first search for the name + address in google maps. We then combine the following approaches -
# if the url has a /maps/place in it, that means that we did indeed actually find a place that matched. this is the easy option
# if not, and we have a /maps/search/, we first let it load fully incase it turns into a /place/ (happens occasionaly when google works it out)
# then, if all else fails, we literally just pick the first place that google offers up. accuracy is about 90ish plus which is good enough. 

def fix_search_urls():
    with open(r'output\output_final_fixed.json', 'r', encoding="utf-8") as file:
        data = json.load(file)

    options = Options()
    options.add_argument('--headless')  # Run in background
    driver = webdriver.Chrome(options=options)
    
    failed_indices = []
    fixed_count = 0
    
    for key, museum in data.items():
        url = museum['maps_url']
        
        if '/maps/search' in url:
            print(f"Checking key {key}: {museum['name']}")
            
            # Open the URL
            driver.get(url)
            time.sleep(5)  # Wait 5 seconds
            
            current_url = driver.current_url
            
            if '/maps/place' in current_url:
                data[key]['maps_url'] = current_url
                print(f"  ✓ Fixed: {key}")
                fixed_count += 1
            else:
                failed_indices.append(key)
                print(f"  ✗ Failed: {key}")
    
    driver.quit()
    
    with open(r'output\output_final_fixed.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"\nResults:")
    print(f"Fixed: {fixed_count}")
    print(f"Failed indices: {failed_indices}")

fix_search_urls()