#!/usr/bin/env bash
set -e

ROOT="novitsky-site"

echo "Creating project structure..."
mkdir -p $ROOT/assets

cd $ROOT

echo "Creating index.html..."
cat > index.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Ed Novitsky — Memorial Archive</title>
  <meta name="description" content="Memorial site honoring Edward Ed Novitsky (1929–2020)." />
  <link rel="stylesheet" href="assets/styles.css" />
</head>
<body>

<header class="site-header">
  <div class="container header-row">
    <div class="brand">
      <span class="brand-title">Ed Novitsky</span>
      <span class="brand-subtitle">Memorial Archive</span>
    </div>
    <nav class="nav">
      <a href="biography.html">Biography</a>
      <a href="works.html">Works</a>
      <a href="sources.html">Sources</a>
      <a class="nav-cta" href="archive-signin.html">Sign In</a>
    </nav>
  </div>
</header>

<main>

<section class="hero">
  <div class="container">
    <h1>Preserving recorded history — the right way.</h1>
    <p class="lead">
      This site honors Edward “Ed” Novitsky (1929–2020), a guardian of recorded music history.
    </p>
    <div class="cta-row">
      <a class="btn primary" href="upload.html">Upload</a>
      <a class="btn" href="archive-signin.html">Archive (Sign In)</a>
      <a class="btn ghost" href="#about">About Novitsky</a>
    </div>
  </div>
</section>

<section id="about" class="section">
  <div class="container narrow">
    <h2>About Novitsky</h2>

    <p><strong>Edward “Ed” Novitsky (1929–2020)</strong> devoted his life to accuracy, memory, and responsibility.</p>

    <p>
      He was not a performer or celebrity. He was a guardian of recorded history —
      someone who believed every recording deserved to be preserved correctly.
    </p>

    <p>
      After serving 30 years in the United States Air Force and retiring as a
      Chief Master Sergeant, he brought the same discipline to music documentation.
    </p>

    <blockquote>
      Memory without accuracy is not preservation.
    </blockquote>

    <p>
      He worked quietly and methodically. His legacy lives not in fame, but in trust.
    </p>
  </div>
</section>

<section class="section tinted">
  <div class="container split">
    <div>
      <h2>Archive Access</h2>
      <p>Authorized access to preserved records.</p>
      <a class="btn" href="archive-signin.html">Sign In</a>
    </div>
    <div>
      <h2>Upload</h2>
      <p>Preview-first. Nothing is saved without confirmation.</p>
      <a class="btn primary" href="upload.html">Upload</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container narrow">
    <h2>In Memoriam</h2>
    <p>
      Rest in peace. Ed Novitsky earned lasting honor —
      not by being remembered loudly, but by being remembered correctly.
    </p>
  </div>
</section>

</main>

<footer class="site-footer">
  <div class="container footer-row">
    <p>© <span id="year"></span> Ed Novitsky Memorial Archive</p>
  </div>
</footer>

<script src="assets/site.js"></script>
</body>
</html>
EOF

echo "Creating biography.html..."
cat > biography.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Biography — Ed Novitsky</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<h1>Biography</h1>
<p>Edward “Ed” Novitsky was a music historian, discographer, and recording archivist.</p>
<p>His work focused on accuracy: sessions, dates, personnel, and labels.</p>
<a href="index.html">Back</a>
</body>
</html>
EOF

echo "Creating works.html..."
cat > works.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Works — Ed Novitsky</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<h1>Works</h1>
<ul>
  <li>The Mercury Labels: A Discography (5 volumes)</li>
  <li>The MGM Labels: A Discography (3 volumes)</li>
</ul>
<a href="index.html">Back</a>
</body>
</html>
EOF

echo "Creating sources.html..."
cat > sources.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Sources — Ed Novitsky</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<h1>Sources & Clarifications</h1>
<p>
Edward “Ed” Novitsky (discographer) is not the geneticist Edward Novitski.
</p>
<a href="https://www.newcomerorlando.com/obituaries/edward-novitsky" target="_blank">
Obituary — Newcomer Orlando
</a>
<br><a href="index.html">Back</a>
</body>
</html>
EOF

echo "Creating archive-signin.html..."
cat > archive-signin.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Archive Sign In</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<h1>Archive Access</h1>
<form>
<input type="email" placeholder="Email"><br>
<input type="password" placeholder="Password"><br>
<button>Sign In</button>
</form>
<a href="index.html">Back</a>
</body>
</html>
EOF

echo "Creating upload.html..."
cat > upload.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Upload</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<h1>Upload (Preview First)</h1>
<form>
<input type="file"><br>
<button>Upload for Preview</button>
</form>
<a href="index.html">Back</a>
</body>
</html>
EOF

echo "Creating assets/styles.css..."
cat > assets/styles.css <<'EOF'
body {
  font-family: system-ui, sans-serif;
  background:#0b0f14;
  color:#e8edf5;
  margin:0;
  padding:20px;
}
a { color:#9fb7ff; }
.btn {
  padding:10px 14px;
  border:1px solid #555;
  border-radius:10px;
  display:inline-block;
  margin:6px;
}
.primary { background:#3a6df0; color:white; }
EOF

echo "Creating assets/site.js..."
cat > assets/site.js <<'EOF'
document.getElementById("year").textContent = new Date().getFullYear();
EOF

echo "Site setup complete."
echo "Open $ROOT/index.html in your browser."
