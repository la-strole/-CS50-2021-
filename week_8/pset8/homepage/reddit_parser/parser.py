import requests
from bs4 import BeautifulSoup
import json


def get_images_from_reddit(search_name: str):
    """
    Get text and images from reddit/pikabu and save links and text in json file
    :param search_name: http parametrs
    :return: list [(text, link_to_image)]
    """

    # get reddit page
    url = f'https://www.reddit.com/r/Pikabu/top/{search_name}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }

    session = requests.session()
    response = session.get(url, headers=headers)
    assert response.ok

    soup = BeautifulSoup(response.content, 'lxml')

    content_div = soup.find(class_="rpBJOHq2PR60pnwJlUyP0")
    post_containers = content_div.find_all("div", attrs={'data-testid': 'post-container'})

    result = []
    for post_content in post_containers:
        if post_content.find('h3'):
            image_text = post_content.find('h3').text
        else:
            continue
        if post_content.find('img'):
            image = post_content.find('img', attrs={'alt': 'Post image'})
            if image:
                image_link = image.attrs['src']
            else:
                continue
        else:
            continue

        result.append((image_text, image_link))

    return result


if __name__ == "__main__":

    file_link = dict()

    file_link['Cats'] = get_images_from_reddit("?t=day&f=flair_name%3A%22Коты%22")
    file_link['Cutes'] = get_images_from_reddit("?t=day&f=flair_name%3A%22Милота%22")
    file_link['Memes'] = get_images_from_reddit("?t=day&f=flair_name%3A%22Мем%22")
    file_link['Bests'] = get_images_from_reddit('?t=all')
    file_link['Photos'] = get_images_from_reddit('?t=day&f=flair_name%3A%22Фото%22')

    with open("reddit_images.json", "w") as f:
        data = json.dumps(file_link)
        f.write(f"data = `{data}`;")

