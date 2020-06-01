def check(url):
    if url == "abcde":
        return True

child_links = ["abcde","abcdef"]
child_links = [url   for url in child_links if not check(url)]

print(child_links)