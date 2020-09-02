import json
import sys

from jinja2 import Environment, FileSystemLoader

import blog_site_generator
from podcast_to_dict import podcast_to_dict

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

separator = '--------------------'

def get_pages(podcast):
    pages = []
    for episode in podcast['episodes']:
        page = {}
        page['header'] = {}
        page['header']['datetime'] = episode['pubDate_dt']
        page['header']['itunes:episode'] = episode['itunes:episode']
        page['header']['tags'] = []
        page['header']['title'] = episode['title']
        page['header']['slug'] = episode['slug']
        page['header']['enclosure_url'] = episode['enclosure']['url']
        page['body'] = episode['description']
        pages.append(page)
    return pages


if __name__ == "__main__":
    site = {}
    with open(sys.argv[1]) as f:
        site['config'] = json.load(f)
    with open(site['config']['footer_file']) as f:
        site['config']['footer_links']  = json.load(f)
    podcast = podcast_to_dict(site['config']['rss_url'])
    site['config']['description'] = podcast['description']
    site['config']['cover_art'] = podcast['itunes:image']
    site['config']['title'] = podcast['title']
    site['pages'] = get_pages(podcast)
    blog_site_generator.make_homepage(site)
    for page in site['pages']:
        blog_site_generator.make_page(page, site)
