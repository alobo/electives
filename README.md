# Easy Elective Picker
I'm not lazy, promise. Just frustrated with scheduling conflicts stopping me from taking electives I actually care about.

## How It Works
The web scraper (`scraper/parse.py`) pulls in data from the UW calendar and UWFlow or each course and compiles a csv. This csv is then handed off to [dc.js](https://dc-js.github.io/dc.js/) which does all the heavy lifting and fancy charting.

### Caching
I aggressively cache HTTP responses using [requests_cache](https://pypi.python.org/pypi/requests-cache). If you're going to run this, please be polite and keep that enabled.

## Works Cited
- [http://stackoverflow.com/a/20172877/1263256](http://stackoverflow.com/a/20172877/1263256)
- [https://dc-js.github.io/dc.js/docs/stock.html](https://dc-js.github.io/dc.js/docs/stock.html)
