import pytesseract
from PIL import Image
import re
import csv
from collections import defaultdict
import os

def extract_text_from_image(image_path):
    """Extract text from an image using Tesseract OCR"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def parse_walmart_receipt(text):
    """Specialized parser for Walmart receipts"""
    items = []
    lines = text.split('\n')
    
    for line in lines:
        # Match item patterns like: "BANANAS 000000004011KF 0.41lb 1lb/0.49 0.20N"
        item_match = re.search(r'^([A-Z][A-Z0-9\s\/\-\.\&]+)\s+([0-9]+\.[0-9]{2})\s*[A-Z]?$', line.strip())
        if item_match:
            item_name = re.sub(r'\s+[0-9A-Z]{10,}.*$', '', item_match.group(1)).strip()
            amount = float(item_match.group(2))
            
            # Skip common false positives
            if not any(word in item_name.lower() for word in ['subtotal', 'total', 'tax', 'change', 'debit', 'cash']):
                items.append((item_name, amount))
    
    return items

def parse_traderjoes_receipt(text):
    """Specialized parser for Trader Joe's receipts"""
    items = []
    lines = text.split('\n')
    
    for line in lines:
        # Match item patterns like: "R-CARROTS SHREDDED 10 OZ 1.29"
        item_match = re.search(r'^([A-Z][A-Za-z0-9\s\/\-\.\&]+)\s+([0-9]+\.[0-9]{2})$', line.strip())
        if item_match:
            item_name = item_match.group(1).strip()
            amount = float(item_match.group(2))
            items.append((item_name, amount))
    
    return items

def parse_receipt(text):
    """Determine receipt type and parse accordingly"""
    if "Walmart" in text or "WAL*MART" in text:
        return "Walmart", parse_walmart_receipt(text)
    elif "TRADER JOE'S" in text or "TRADER JOE'S" in text:
        return "Trader Joe's", parse_traderjoes_receipt(text)
    else:
        return "Unknown", []

def generate_shopping_summary(receipts):
    """Generate a shopping summary with totals per store"""
    summary = defaultdict(list)
    
    for store, items in receipts:
        for item_name, amount in items:
            summary[store].append((item_name, amount))
    
    return summary

def write_to_csv(summary, output_file):
    """Write the shopping summary to a CSV file"""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Store', 'Item', 'Amount'])
        
        for store, items in summary.items():
            total = 0
            for item_name, amount in items:
                writer.writerow([store, item_name, f"${amount:.2f}"])
                total += amount
            
            # Write the total row
            writer.writerow(["", "Total", f"${total:.2f}"])

def main():
    # List of receipt images to process
    receipt_images = ['0.jpg', '1.jpg', '2.jpg', '3.jpg']
    receipts = []
    
    # Process each receipt
    for image in receipt_images:
        if not os.path.exists(image):
            print(f"Warning: File {image} not found. Skipping.")
            continue
            
        text = extract_text_from_image(image)
        store_name, items = parse_receipt(text)
        print(f"Found {len(items)} items from {store_name}")
        receipts.append((store_name, items))
    
    # Generate summary and write to CSV
    summary = generate_shopping_summary(receipts)
    write_to_csv(summary, 'shopping_summary.csv')
    print("Shopping summary generated successfully as shopping_summary.csv")

if __name__ == "__main__":
    main()