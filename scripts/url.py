
import json


# just some bullshittery with cleaning up duplicates

with open(r"output\output_with_maps_urls.json","r",encoding="utf-8") as file:
    data = json.load(file)

arr = []


duplicates = {}

for key, museums in data.items():
    url = museums['maps_url']
    if url not in arr:
        arr.append(url)
    else:
        if url not in duplicates:
            # Find the original key
            original_key = None
            for k, v in data.items():
                if v['maps_url'] == url and k != key:
                    original_key = k
                    break
            duplicates[url] = [original_key, key]
        else:
            duplicates[url].append(key)

for url, keys in duplicates.items():
    print(f"Duplicate URL")
    print(f"Keys: {keys}")
    print()


def clean_and_resequence_json():
    # Load the original JSON
    with open(r'output\output_final_fixed.json', 'r', encoding="utf-8") as file:
        data = json.load(file)
    
    # Create new dictionary with sequential keys and remove maps_status
    cleaned_data = {}
    
    for i, (old_key, museum) in enumerate(data.items(), 1):
        
        # Add to new dictionary with sequential key
        cleaned_data[str(i)] = museum
    
    # Save to output_final.json
    with open('output_final.json', 'w', encoding='utf-8') as file:
        json.dump(cleaned_data, file, indent=4, ensure_ascii=False)
    
    print(f"Cleaned and resequenced {len(cleaned_data)} museums")
    print("Saved to output_final.json")
    print("- Removed 'maps_status' fields")
    print("- Resequenced keys from 1 to", len(cleaned_data))

# Run the function
clean_and_resequence_json()