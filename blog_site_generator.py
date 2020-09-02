import json
import os
import sys

import dateparser
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

separator = '--------------------'


def process_page(file_path):
    page = {}
    with open(file_path) as f:
        contents = f.read()
        [header, body] = contents.split(separator, 1)
    page['header'] = json.loads(header)
    page['header']['datetime'] = dateparser.parse(page['header']['date'])
    page['header']['slug'] = slugify(page['header']['title'])
    page['body'] = body.strip()
    return page

def load_pages(dir):
    pages = []
    for f in os.listdir(dir):
        file_path = os.path.join(dir, f)
        if f.endswith('.html'):
            page = process_page(file_path)
            pages.append(page)
    pages = sorted(pages, key = lambda i: i['header']['datetime'], reverse=True) 
    return pages

def load_tags(pages):
    tags = []
    for page in pages:
        tags.extend(page['header'].get('tags', []))
    tags = list(set(tags))
    return tags

def make_homepage(site):
    file_path = os.path.join(site['config']['output_dir'], 'index.html')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    template = env.get_template("homepage.html")
    output = template.render(site=site, home=True)
    with open(file_path, 'w') as f:
        f.write(output)

def make_page(page, site):
    file_path = os.path.join(site['config']['output_dir'], page['header']['slug'], 'index.html')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    template = env.get_template("page.html")
    output = template.render(site=site, page=page)
    with open(file_path, 'w') as f:
        f.write(output)


def make_tag_page(tag, site):
    filtered_pages = []
    for page in site['pages']:
        if tag in page['header']['tags']:
            filtered_pages.append(page)
    file_path = os.path.join(site['config']['output_dir'], "tag", tag, 'index.html')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    template = env.get_template("homepage.html")
    output = template.render(site=site, filtered_pages=filtered_pages, tag=tag)
    with open(file_path, 'w') as f:
        f.write(output)


def get_related(site, page):
    related_pages = []
    tags = set(page['header']['tags'])
    for i, each in enumerate(site['pages']):
        if page['header']['slug'] is each['header']['slug']:
            continue
        target_tags = set(each['header']['tags'])
        shared_tags = tags.intersection(target_tags)
        t = {}
        t['score'] = len(shared_tags)
        if t['score'] > 0:
            t['title'] = each['header']['title']
            t['slug'] = each['header']['slug']
            t['datetime'] = each['header']['datetime']
            related_pages.append(t)
    related_pages = sorted(related_pages, key = lambda i: i['score'], reverse=True)[:5]
    return related_pages


if __name__ == "__main__":
    site = {}
    with open(sys.argv[1]) as f:
        site['config'] = json.load(f)
    with open(site['config']['footer_file']) as f:
        site['config']['footer_links']  = json.load(f)
    site['pages'] = load_pages(site['config']['content_dir'])
    site['tags'] = load_tags(site['pages'])
    make_homepage(site)
    for tag in site['tags']:
        make_tag_page(tag, site)
    for page in site['pages']:
        page['related_pages'] = get_related(site, page)
        make_page(page, site)
    


