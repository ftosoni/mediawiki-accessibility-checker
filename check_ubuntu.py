import urllib.request
import re

req = urllib.request.Request('http://archive.ubuntu.com/ubuntu/pool/main/a/at-spi2-core/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
debs = re.findall(r'href="([^"]+\.deb)"', html)
print("\n".join(debs))
