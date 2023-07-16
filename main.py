import re
import shutil

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)


def center_align_text(text):
    terminal_width = shutil.get_terminal_size().columns
    padding_width = (terminal_width - len(text)) // 2
    centered_text = ' ' * padding_width + text
    return centered_text


def fetchAndSaveToFile(url, path):
    r = requests.get(url)
    with open(path, "w") as f:
        f.write(r.text)


def scrape_news(city):
    url = f"https://timesofindia.indiatimes.com/city/{city.lower()}"
    fetchAndSaveToFile(url, "data/times.html")

    with open('data/times.html', 'r') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        results = []
        tags = soup.findAll('figcaption')
        anchor_tags = soup.find_all('a', class_=["undefined", "Hn2z7"])
        if tags:
            for index, tag in enumerate(tags):
                link = get_related_link(tag.text, anchor_tags)
                if link != "N/A":
                    headline = re.sub(r"[^\w\s]", "", tag.text)
                    results.append({
                        'headline': headline,
                        'link': link,
                    })
        return results


def get_related_link(headline, anchor_tags):
    for anchor in anchor_tags:
        if headline.strip().lower() in anchor.text.strip().lower():
            return anchor.get('href')
    return "N/A"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        city = request.form.get('city')
        news = scrape_news(city)
        return render_template('index.html', news=news, city=city)
    else:
        return render_template('index.html', news=[], city='')


if __name__ == '__main__':
    app.run(debug=True)
