
import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from transformers import pipeline

# Modell laden
device = 0 if torch.cuda.is_available() else -1

estimator = pipeline(
    task="depth-estimation",
    model="Intel/zoedepth-nyu-kitti",
    device=device,
)

# Bild laden
image = Image.open("dog.jpg").convert("RGB")

# Metrische Tiefe schätzen
result = estimator(image)
depth = np.array(result["depth"], dtype=np.float32)

print("Min. Tiefenwert:", np.nanmin(depth))
print("Max. Tiefenwert:", np.nanmax(depth))


# Tiefenkarte mit OpenCV anzeigen
import cv2
import numpy as np

# Werte auf 0 bis 255 normalisieren
depth_display = cv2.normalize(
    depth, None, 0, 255, cv2.NORM_MINMAX
).astype(np.uint8)

# Farbige Tiefenkarte erstellen
depth_color = cv2.applyColorMap(
    depth_display, cv2.COLORMAP_INFERNO
)

# Originalbild und Tiefenkarte anzeigen
original = cv2.cvtColor(
    np.array(image), cv2.COLOR_RGB2BGR
) if "image" in globals() else None

cv2.imshow("Tiefenkarte", depth_color)

if original is not None:
    cv2.imshow("Originalbild", original)

cv2.waitKey(0)
cv2.destroyAllWindows()