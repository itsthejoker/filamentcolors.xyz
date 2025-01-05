from filamentcolors.bluesky import parse_urls, parse_hashtags, parse_mentions


def test_parse_single_url():
    text = "This is a test of the http://example.com URL parser."
    assert parse_urls(text) == [{"start": 22, "end": 40, "url": "http://example.com"}]


def test_parse_multiple_urls():
    text = "This is a test of the http://example.com URL parser and the http://example.org URL parser."
    assert parse_urls(text) == [
        {"start": 22, "end": 40, "url": "http://example.com"},
        {"start": 60, "end": 78, "url": "http://example.org"},
    ]


def test_parse_single_mention():
    text = "Hey @example.xyz, how are you?"
    assert parse_mentions(text) == [{"start": 4, "end": 16, "handle": "example.xyz"}]


def test_parse_multiple_mentions():
    text = "Hey @example.xyz, how are you? I'm @another.xyz."
    assert parse_mentions(text) == [
        {"start": 4, "end": 16, "handle": "example.xyz"},
        {"start": 35, "end": 47, "handle": "another.xyz"},
    ]


def test_single_tag():
    text = "This is a #test."
    assert parse_hashtags(text) == [{"start": 10, "end": 15, "tag": "test"}]


def test_multiple_tags():
    text = "This is a #test of the #hashtag parser."
    assert parse_hashtags(text) == [
        {"start": 10, "end": 15, "tag": "test"},
        {"start": 23, "end": 31, "tag": "hashtag"},
    ]
