# How to Add a New Blog Post

## Step 1 — Copy the template

```bash
cp posts/_template.html posts/your-post-slug.html
```

Use a short, hyphenated slug that describes the post.
Examples: `cuda-memory-management.html`, `yolo-custom-training.html`

---

## Step 2 — Edit the new post file

Open `posts/your-post-slug.html` and update:

| Field | Where | What to change |
|---|---|---|
| Page title | `<title>` tag | `POST TITLE — Sudhanshu` |
| Date | `.post-date` span | e.g. `April 2026` |
| Tag | `.post-tag` span | `inference` / `infrastructure` / `deployment` / `training` / `research` / `tools` |
| Read time | `.read-time` span | estimate from word count ÷ 200 |
| Post title | `<h1>` | your full title |
| Description | `.post-description` | 1-2 sentence hook |
| Body | `.post-body` div | your content |

### Available HTML elements in the body:

```html
<!-- Paragraph -->
<p>Your text here. Use <code>inline code</code> for short snippets.</p>

<!-- Section heading -->
<h2>Section Title</h2>
<h3>Sub-section</h3>

<!-- Code block (multi-line) -->
<pre><code>your_code = goes_here()
print("result")</code></pre>

<!-- Callout / quote -->
<blockquote>
  A memorable insight or key lesson from this section.
</blockquote>

<!-- Bullet list -->
<ul>
  <li>First point</li>
  <li>Second point</li>
</ul>

<!-- Numbered list -->
<ol>
  <li>First step</li>
  <li>Second step</li>
</ol>
```

---

## Step 3 — Add a card to the homepage

Open `index.html` and find the `<div class="post-list">` section.
Add your new post card at the **top** of the list (newest first):

```html
<a href="posts/your-post-slug.html" class="post-card">
  <div class="post-meta">
    <span class="post-date">April 2026</span>
    <span class="post-tag">inference</span>
  </div>
  <h3 class="post-title">Your Post Title Here</h3>
  <p class="post-excerpt">
    A 2-3 sentence teaser that makes someone want to read the full post.
    Be specific about what they'll learn.
  </p>
  <span class="read-time">X min read</span>
</a>
```

---

## Step 4 — Deploy (push to GitHub)

```bash
git add .
git commit -m "add: post on your-topic"
git push
```

GitHub Pages will update within ~30 seconds.

---

# Hosting on GitHub Pages (one-time setup)

## 1. Create a GitHub repository

Go to github.com and create a new repo named:
```
Justsubh01.github.io
```
This is your free personal site URL. Replace `Justsubh01` with your actual GitHub username.

## 2. Initialize and push your blog

```bash
cd /home/cv-gpu-2/sudhanshu_workspace/my_blogs

git init
git add .
git commit -m "initial: launch blog"
git branch -M main
git remote add origin https://github.com/Justsubh01/Justsubh01.github.io.git
git push -u origin main
```

## 3. Enable GitHub Pages

1. Go to your repo on GitHub
2. Click **Settings** → **Pages** (left sidebar)
3. Under **Source**, select `main` branch, `/ (root)` folder
4. Click **Save**

Your blog will be live at `https://Justsubh01.github.io` within a few minutes.

## 4. Update personal details

Before pushing, update these placeholders in `index.html` and all post files:

- `sudhanshufromearth@gmail.com` → your actual email
- `Justsubh01` in social links → your GitHub/LinkedIn/Twitter handles
- Social link URLs → your actual profile URLs

---

# File Structure Reference

```
my_blogs/
├── index.html              ← homepage (edit to add post cards)
├── style.css               ← all styling (rarely needs editing)
├── ADDING_POSTS.md         ← this file
└── posts/
    ├── _template.html      ← copy this for every new post
    ├── tensorrt-optimization-guide.html
    ├── triton-serving-at-scale.html
    └── multi-gpu-kubernetes.html
```
