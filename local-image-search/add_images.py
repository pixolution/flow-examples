import argparse
import os
import sys
import requests
import base64
import time
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

if (sys.version_info[0] < 3 or sys.version_info[1] < 8):
    sys.exit("Python 3.8 or higher is required")

MAX_DOCS = 5000
SERVER_URL = "http://localhost:8983/solr/my-collection"


def ping():
    try:
        response = requests.get(SERVER_URL+"/admin/ping")
        return response.status_code == 200
    except:
        return False


def init():
    requests.get(SERVER_URL+"/pixolution")


def clear_index():
    print("Clear index...")
    payload = {"delete":{"query":"*:*" }}
    response = requests.post(SERVER_URL+"/update?commit=true&openSearcher=true", json=payload)

def commit():
    requests.get(SERVER_URL+"/update?commit=true&openSearcher=true")

def random_images(count):
    urls = []
    for i in range(0, count):
        urls.append(f"https://picsum.photos/seed/{i}/250.jpg")
    return urls


def index_images(directory):
    image_list=[]
    if directory:
        print(f"Scan directory {directory} ..." )
        image_list = scan_folder(directory)
    else:
        print("Index random web images...")
        image_list = random_images(min(500, MAX_DOCS))
    # Parallelize client to speed up IO-bound tasks (file access, API calls)
    # Server also parallelizes to speed up CPU-bound tasks (image analysis)
    pool = ThreadPoolExecutor(4)
    futures = []
    for i, image_path in enumerate(image_list):
        futures.append(pool.submit(add_doc, id=i, image_path=image_path))
    if not futures:
        print(f"No images found in {directory}. Choose a different folder.")
        return
    print(f"Found {len(futures)} images. Start indexing (this may take a while)...")
    errors=0
    try:
        # Await completion and display progress
        progress = tqdm(as_completed(futures), total=len(futures), unit="images", colour="green", smoothing=0)
        for f in progress:
            if not f.exception() == None:
                # Silently count errors
                errors+=1
                if "document limit" in str(f.exception()).lower():
                    # Reached document limit of Free Plan. Stop further indexing.
                    progress.close()
                    close_threadpool(futures, pool)
                    print(f.exception())
                    return
        # Commit updated index to make it visible
        commit()
        if errors>0:
            print(f"{errors}/{len(futures)} images could not be indexed.")
        print("Click or copy the link to open the search UI in your browser:")
        print("")
        print(f"file://{os.path.dirname(os.path.realpath(__file__))}{os.sep}ui{os.sep}index.html")
        print("")
    except KeyboardInterrupt:
        print("Abort processing...")
        close_threadpool(futures, pool)
        sys.exit()


def scan_folder(rootDir):
    count=0
    valid_images = (".jpg",".jpeg",".gif",".png")
    image_list = []
    if (len(rootDir)>1):
        rootDir = rootDir.rstrip(os.sep)
    for root, dirs, files in os.walk(rootDir):
        for fname in files:
            if not fname.lower().endswith(valid_images):
                continue
            if(count>=MAX_DOCS):
                print(f"Doc limit of {MAX_DOCS} reached. Quit scanning.")
                return image_list
            count+=1
            image_list.append(root + os.sep + fname)
    return image_list


def add_doc(id, image_path):
    doc = [{"id":id,
        "url":image_path,
        "pxl_import": analyze(image_path)
        }]
    response = requests.post(SERVER_URL+"/update", json=doc)
    if not (response.json()['responseHeader']['status'] == 0):
        raise Exception(response.json()['error']['msg'])


def analyze(image_path):
    if image_path.startswith("http"):
        # Got web image - reference via url
        response = requests.get(f"{SERVER_URL}/analyze?input.urls={image_path}")
        return response.json()['outputs']
    else:
        # Got local image - upload
        # scale to thumbnail size - HighRes images slow down IO tremendously
        img = Image.open(image_path)
        img.thumbnail((250, 250))
        # encode as in-memory png
        bytes = BytesIO()
        img.save(bytes, format='PNG')
        base64_image = base64.b64encode(bytes.getvalue()).decode('utf-8')
        payload = {'input.data': base64_image}
        # set empty logParamsList= to avoid logging huge log messages when uploading base64 images as parameters
        response = requests.post(SERVER_URL+"/analyze?logParamsList=", data=payload)
        return response.json()['outputs']


def close_threadpool(futures, pool):
    for future in futures:
        future.cancel()
    pool.shutdown(wait=True)


parser = argparse.ArgumentParser(description='Index images into backend (uses random web images if no path is given)')
parser.add_argument(dest="local_image_path", nargs="?", type=str, help='Scan directory tree and index the contained images (jpg, png, gif).')
args = parser.parse_args()

if not ping():
    print("The server is not up and running.")
    sys.exit()
init()
clear_index()
index_images(args.local_image_path)
