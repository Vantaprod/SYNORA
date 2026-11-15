import os
model_dir = "models/downloaded/MeanVC2"
for root, dirs, files in os.walk(model_dir):
    for file in files:
        print(os.path.join(root, file))
