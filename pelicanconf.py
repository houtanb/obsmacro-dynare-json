#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

LOAD_CONTENT_CACHE = False
DELETE_OUTPUT_DIRECTORY = False

DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = ' %B %-d, %Y'

LOCALE = 'en_US.utf8'

AUTHOR = 'Macroeconomic Observatory'
SITENAME = 'Macroeconomic Observatory'
# HIDE_SITENAME = True
SITEURL = ''

BANNER_SUBTITLE = \
    'Providing free and state-of-the-art tools for macroeconomic analysis.'

DISPLAY_CATEGORY_IN_BREADCRUMBS = True

SHOW_ARTICLE_AUTHOR = True
DISPLAY_ARTICLE_INFO_ON_INDEX = True
DISPLAY_TAGS_INLINE = True

DIRECT_TEMPLATES = (
    'archives',
    'authors',
    'categories',
    'index',
    'search',
    'tags',
    )

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
# FEED_ALL_ATOM = 'feeds/all.atom.xml'
# TAG_FEED_ATOM = 'feeds/tag-%s.atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_ALL_RSS = 'feeds/all.rss.xml'
TAG_FEED_RSS = 'feeds/%s.rss.xml'
RSS_FEED_SUMMARY_ONLY = False

# Blogroll
LINKS = (
    ('Dynare', 'http://www.dynare.org/'),
    ('DB.nomics', 'https://db.nomics.world/'),
    ('R-bloggers', 'http://www.r-bloggers.com/'),
    )

# Social widget
SOCIAL = (
    ('Gitlab', 'https://git.nomics.world/macro'),
    ('Twitter', 'https://twitter.com/obsmacro'),
    )

DEFAULT_PAGINATION = 5

TWITTER_USERNAME = 'obsmacro'
TWITTER_WIDGET_ID = '573544104640049152'

ARTICLE_URL = 'article/{date:%Y}-{date:%m}/{slug}/'
ARTICLE_SAVE_AS = 'article/{date:%Y}-{date:%m}/{slug}/index.html'
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'

TAGS_URL = 'tags.html'

TAG_CLOUD_MAX_ITEMS = 15

RELATED_POSTS_MAX = 4

HIDE_SIDEBAR = True
DISPLAY_BREADCRUMBS = True
MATH_JAX = {'responsive': 'True'}

# Plugins.
PLUGIN_PATHS = ['./plugins']
PLUGINS = [
    # 'feed_summary',
    # 'liquid_tags.img',
    # 'liquid_tags.notebook',
    # 'liquid_tags.video',
    # 'liquid_tags.youtube',
    'pelican-cite',
    'related_posts',
    'render_math',
    'rmd_reader',
    'simple_footnotes',
    'tipue_search',
    ]

MENUITEMS = (
    ('About', '/about.html'),
    )
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = True

# Themes
THEME = "./theme"

MARKUP = 'md'

PYGMENTS_STYLE = 'trac'
TYPOGRIFY = True

STATIC_PATHS = [
    'images',
    'notebooks',
    'figure']
# SITELOGO = 'images/obsmacro.svg'
# SITELOGO_SIZE = 180

RMD_READER_RENAME_PLOT = 'directory'
RMD_READER_KNITR_OPTS_CHUNK = {'fig.path': 'figure/'}

LOAD_CONTENT_CACHE = False
PUBLICATIONS_SRC = 'content/biblio.bib'

SHARIFF = True
SHARIFF_LANG = 'en'
SHARIFF_THEME = 'white'
SHARIFF_SERVICES = '[&quot;twitter&quot;]'
# SHARIFF_BACKEND_URL =

# License
CC_LICENSE = "CC-BY-SA"

# Uncomment following line if you want document-relative URLs when developing.
# RELATIVE_URLS = True

# Piwik configuration
PIWIK_URL = 'analytics.nomics.world'
PIWIK_SITE_ID = 3
