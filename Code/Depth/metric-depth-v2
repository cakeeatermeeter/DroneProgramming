import torch
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from transformers import pipeline
from io import BytesIO

# Modell laden
device = 0 if torch.cuda.is_available() else -1

estimator = pipeline(
    task="depth-estimation",
    model="Intel/zoedepth-nyu-kitti",
    device=device,
)

# Bild laden
image = Image.open("original.jpg").convert("RGB")

# Tiefe berechnen
result = estimator(image)

# Numerische Tiefenwerte verwenden
predicted_depth = result["predicted_depth"]

if isinstance(predicted_depth, torch.Tensor):
    depth = predicted_depth.squeeze().detach().cpu().numpy()
else:
    depth = np.asarray(predicted_depth)

depth = depth.astype(np.float32)

print("Min. Tiefenwert:", np.nanmin(depth))
print("Max. Tiefenwert:", np.nanmax(depth))

# Tiefenkarte erstellen
fig, ax = plt.subplots(figsize=(10, 6))

im = ax.imshow(
    depth,
    cmap="inferno"
)

# Metrische Farbskala hinzufügen
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Tiefe (m)")

ax.axis("off")

# In Speicherpuffer schreiben
buffer = BytesIO()

fig.savefig(
    buffer,
    format="png",
    dpi=300,
    bbox_inches="tight"
)

buffer.seek(0)

# PIL-Bild erzeugen
depth_image = Image.open(buffer).copy()

# Speichern
Dateipfad = "tiefenkarte_mit_skala.png"
depth_image.save(Dateipfad)

# Ressourcen freigeben
plt.close(fig)
buffer.close()

print("Tiefenkarte erfolgreich gespeichert!")
