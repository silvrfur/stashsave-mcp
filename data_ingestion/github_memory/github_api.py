import requests

GITHUB_API = "https://api.github.com"


def fetch_starred_repos(access_token: str):
    repos = []
    page = 1
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
    }

    while True:
        url = f"{GITHUB_API}/user/starred"
        params = {"per_page": 100, "page": page}

        res = requests.get(url, headers=headers, params=params, timeout=20)
        res.raise_for_status()
        data = res.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos
