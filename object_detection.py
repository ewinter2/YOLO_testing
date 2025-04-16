import os
import torch
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

def detect_objects(image_path):
    # Load the pretrained YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    
    # Load and process the image
    img = Image.open(image_path)
    results = model(img)
    
    # Extract predictions
    predictions = results.pandas().xyxy[0]
    
    # Print results
    print("\nPredicted objects and their locations:")
    for _, pred in predictions.iterrows():
        print(f"- {pred['name']}: Confidence {pred['confidence']:.2f}, "
              f"Location (xmin, ymin, xmax, ymax): "
              f"({pred['xmin']:.0f}, {pred['ymin']:.0f}, {pred['xmax']:.0f}, {pred['ymax']:.0f})")
    
    # Draw bounding boxes on the image
    draw = ImageDraw.Draw(img)
    for _, pred in predictions.iterrows():
        draw.rectangle([(pred['xmin'], pred['ymin']), 
                        (pred['xmax'], pred['ymax'])], 
                       outline="red", width=2)
        draw.text((pred['xmin'], pred['ymin']), 
                  f"{pred['name']} {pred['confidence']:.2f}", 
                  fill="red")
    
    # Display the image with bounding boxes
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    
    return predictions

if __name__ == "__main__":
    print("Object Detection using YOLOv5")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "objects.jpg")
    
    # Note: Since we can't know the actual objects in the image,
    # we'll only display the predicted objects
    print(f"\nProcessing image: {image_path}")
    detected_objects = detect_objects(image_path)
    
    # Print summary of detected objects
    print("\nSummary of detected objects:")
    object_counts = detected_objects['name'].value_counts()
    for obj, count in object_counts.items():
        print(f"- {obj}: {count} detected")
