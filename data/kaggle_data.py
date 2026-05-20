import kagglehub

path = kagglehub.dataset_download(
    "ismailpromus/skin-diseases-image-dataset"
)

print("Dataset downloaded to:", path)


