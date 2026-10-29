
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


# Flugrichtung aus der ZoeDepth-Tiefenkarte ableiten
# Hinweis: result["depth"] ist hier nur ein Darstellungsbild,
# daher sind die folgenden Werte RELATIV, nicht in Metern.

h, w = depth.shape

# Zentralen Bildbereich untersuchen
y1, y2 = int(h * 0.25), int(h * 0.80)
x1, x2 = int(w * 0.10), int(w * 0.90)

roi = depth[y1:y2, x1:x2]
sectors = np.array_split(roi, 3, axis=1)

names = ["LINKS", "MITTE", "RECHTS"]
scores = {}

for name, sector in zip(names, sectors):
    # Bei ZoeDepth: niedrigere Werte entsprechen typischerweise
    # näheren Objekten, sofern die Werte echte Tiefen darstellen.
    scores[name] = float(np.percentile(sector, 15))

# Vorsichtige relative Entscheidung:
# Der Bereich mit dem höchsten Tiefenwert erscheint weiter entfernt.
best_direction = max(scores, key=scores.get)

if scores["MITTE"] == max(scores.values()):
    decision = "VORWAERTS? (nur relative Schaetzung)"
else:
    decision = best_direction + " (nur relative Schaetzung)"

print("Bereichswerte:", scores)
print("Vorlaeufige Entscheidung:", decision)

# Bereiche im Bild markieren
overlay = cv2.cvtColor(depth_display, cv2.COLOR_GRAY2BGR)

for i, name in enumerate(names):
    x_start = int(x1 + i * (x2 - x1) / 3)
    x_end = int(x1 + (i + 1) * (x2 - x1) / 3)

    cv2.rectangle(
        overlay, (x_start, y1), (x_end, y2),
        (255, 255, 255), 2
    )
    cv2.putText(
        overlay, name, (x_start + 5, y1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
    )

cv2.putText(
    overlay, decision, (10, h - 15),
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
)

cv2.imshow("Bereiche und Richtungsentscheidung", overlay)
cv2.waitKey(0)
cv2.destroyAllWindows()
