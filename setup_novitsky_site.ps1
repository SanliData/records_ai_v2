$Root = "novitsky-site"

Write-Host "Creating project structure..."
New-Item -ItemType Directory -Force -Path $Root | Out-Null
New-Item -ItemType Directory -Force -Path "$Root\assets" | Out-Null

Set-Location $Root

Write-Host "Creating index.html..."
@"
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Ed Novitsky — Memorial Archive</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<h1>About Ed Novitsky</h1>
<p>
Edward “Ed” Novitsky (1929–2020) devoted his life to accuracy, memory, and responsibility.
A guardian of recorded music history.
</p>

<p><strong>Rest in peace.</strong> He earned lasting honor through discipline and integrity.</p>

<hr>

<a href="upload.html">Upload</a> |
<a href="archive-signin.html">Archive (Sign In)</a>
</body>
</html>
"@ | Set-Content index.html -Encoding UTF8

Write-Host "Creating biography.html..."
@"
<!doctype html>
<html><body>
<h1>Biography</h1>
<p>Ed Novitsky was a music historian and discographer.</p>
<a href="index.html">Back</a>
</body></html>
"@ | Set-Content biography.html -Encoding UTF8

Write-Host "Creating works.html..."
@"
<!doctype html>
<html><body>
<h1>Works</h1>
<ul>
<li>The Mercury Labels: A Discography (5 volumes)</li>
<li>The MGM Labels: A Discography (3 volumes)</li>
</ul>
<a href="index.html">Back</a>
</body></html>
"@ | Set-Content works.html -Encoding UTF8

Write-Host "Creating sources.html..."
@"
<!doctype html>
<html><body>
<h1>Sources</h1>
<a href="https://www.newcomerorlando.com/obituaries/edward-novitsky">Obituary</a>
</body></html>
"@ | Set-Content sources.html -Encoding UTF8

Write-Host "Creating archive-signin.html..."
@"
<!doctype html>
<html><body>
<h1>Archive Sign In</h1>
<form>
<input placeholder='Email'><br>
<input type='password' placeholder='Password'><br>
<button>Sign In</button>
</form>
</body></html>
"@ | Set-Content archive-signin.html -Encoding UTF8

Write-Host "Creating upload.html..."
@"
<!doctype html>
<html><body>
<h1>Upload</h1>
<input type='file'><br>
<button>Upload</button>
</body></html>
"@ | Set-Content upload.html -Encoding UTF8

Write-Host "Creating styles.css..."
@"
body {
  font-family: system-ui;
  background: #0b0f14;
  color: #e8edf5;
  padding: 20px;
}
a { color: #9fb7ff; }
"@ | Set-Content assets\styles.css -Encoding UTF8

Write-Host "Setup complete."
Write-Host "Open novitsky-site\index.html"
