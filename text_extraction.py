import pytesseract
from PIL import Image
import re
import csv

def extract_text(image_path):
    """Extract all text from receipt image"""
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return ""

def parse_receipt(text):
    """Simplified parser that works for both Walmart and Trader Joe's"""
    items = []
    for line in text.split('\n'):
        line = line.strip()
        # Match lines ending with price (digits.digits)
        if match := re.search(r'^(.*?)(\d+\.\d{2})\s*[A-Z]?$', line):
            item = match.group(1).strip()
            price = float(match.group(2))
            
            # Skip totals/taxes/payment lines
            if not any(word in item.lower() for word in ['total', 'tax', 'subtotal', 'change', 'debit', 'cash', 'CASH', 'CHANGE', 'TOTAL']):
                items.append((item, price))
    return items

def detect_store(text):
    """Simple store detection"""
    if "trader joe" in text.lower():
        return "Trader Joe's"
    elif "walmart" in text.lower() or "wal*mart" in text.lower():
        return "Walmart"
    return "Unknown"

def main():
    # Process all receipt images
    all_receipts = []
    for img_file in ['0.jpg', '1.jpg', '2.jpg', '3.jpg']:
        text = extract_text(img_file)
        store = detect_store(text)
        items = parse_receipt(text)
        all_receipts.append((store, items))
        print(f"Found {len(items)} items from {store} in {img_file}")

    # Write to CSV
    with open('shopping_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Store', 'Item', 'Price'])
        
        for store, items in all_receipts:
            for item, price in items:
                writer.writerow([store, item, f"${price:.2f}"])
            
            # Add store total
            total = sum(price for _, price in items)
            writer.writerow([store, 'TOTAL', f"${total:.2f}"])
            writer.writerow([])  # Empty row between stores

    print("Done! Saved to shopping_summary.csv")

if __name__ == "__main__":
    main()