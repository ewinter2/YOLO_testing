from ultralytics import YOLO

def detect_objects(image_path):
    # Load model (will auto-download)
    model = YOLO('yolov8n.pt')
    
    # Run detection
    results = model(image_path)
    
    # Print results
    print("\nDetected objects:")
    for result in results:
        for box in result.boxes:
            obj_name = result.names[box.cls[0].item()]
            conf = box.conf[0].item()
            coords = box.xyxy[0].tolist()
            print(f"- {obj_name} ({conf:.2f}): {coords}")
    
    # Show image with boxes
    results[0].show()

if __name__ == "__main__":
    detect_objects("objects.jpg")