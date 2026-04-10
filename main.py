import requests
import os
from urllib.parse import urlparse
import threading

file_types = {
    "videos": (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"),
    "images": (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"),
    "documents": (".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"),
    "audio": (".mp3", ".wav", ".aac", ".flac", ".ogg"),
    "compressed": (".zip", ".rar", ".7z", ".tar", ".gz"),
    "code": (".py", ".java", ".cpp", ".c", ".js", ".html", ".css", ".json")
}

lock = threading.Lock()


def get_file_type(file_name):
    file_type = "others"
    for folder_name, extensions in file_types.items():
        if file_name.lower().endswith(extensions):
            file_type = folder_name
            break
    return file_type


def download_file(url, base_folder="downloads"):
    try:
        file_name = url.split("/")[-1] or "file"
        file_type = get_file_type(file_name)

        folder_path = os.path.join(base_folder, file_type)
        os.makedirs(folder_path, exist_ok=True)

        name, ext = os.path.splitext(file_name)

        with lock:  # Prevent duplicate name collision
            file_path = os.path.join(folder_path, file_name)
            i = 1
            while os.path.exists(file_path):
                file_name = f"{name}({i}){ext}"
                file_path = os.path.join(folder_path, file_name)
                i += 1

        print(f"📥 Downloading: {file_name}")

        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Saved: {file_name} → {file_type}")

    except Exception as e:
        print(f"❌ Failed: {url} | {e}")


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ["http", "https"] and parsed.netloc != ""


def main():
    print("\n========== FILE DOWNLOADER & ORGANIZER ==========\n")

    urls = input("Enter URLs (comma separated): ").split(",")

    valid_urls = []
    invalid_urls = []
    threads = []

    for url in urls:
        url = url.strip()

        if not is_valid_url(url):
            invalid_urls.append(url)
            continue

        valid_urls.append(url)

        t = threading.Thread(target=download_file, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n========== SUMMARY ==========")
    print(f"✔ Valid URLs: {len(valid_urls)}")
    print(f"❌ Invalid URLs: {len(invalid_urls)}")

    if invalid_urls:
        print("\nInvalid URLs:")
        for bad_url in invalid_urls:
            print(f"❌ {bad_url}")

    print("\n🎉 All downloads completed!\n")


if __name__ == "__main__":
    main()