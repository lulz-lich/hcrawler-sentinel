# Local Test Site

Create `index.html`:

```html
<!doctype html>
<html>
  <head>
    <title>Home</title>
    <meta name="description" content="Local test page">
  </head>
  <body>
    <h1>Home</h1>
    <a href="/contact.html">Contact</a>
  </body>
</html>
```

Create `contact.html`:

```html
<!doctype html>
<html>
  <head><title>Contact</title></head>
  <body>
    <h1>Contact</h1>
    <p>contact@example.com</p>
    <p>+55 11 99999-9999</p>
    <p>192.168.0.1</p>
    <script>const api_key = "demo-not-real";</script>
  </body>
</html>
```

Run:

```bash
python3 -m http.server 8000
hcrawler crawl http://localhost:8000 --profile portfolio --audit --emails --phones --ipv4s --plugin seo --plugin privacy --plugin accessibility --sentinel-summary -o report.html -f html
```
