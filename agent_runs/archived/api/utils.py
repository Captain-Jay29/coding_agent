from urllib.parse import urljoin

def build_url(base_url, path):
    return urljoin(base_url, path)
