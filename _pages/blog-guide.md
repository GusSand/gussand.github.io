---
layout: page
title: "Blog Post Guide"
permalink: /blog-guide/
---

# How to Write a Blog Post

This guide provides instructions on how to create and publish blog posts on this website.

## Step 1: Create a new Markdown file in the `_posts` directory

Create a new file in the `_posts` directory with the following naming convention:
```
YYYY-MM-DD-title-of-your-post.md
```

For example:
```
2023-04-07-machine-learning-security.md
```

**Important**: 
- The filename format is critical. Jekyll requires this exact date format followed by the title, separated by hyphens.
- Do NOT include special characters like `@` in the filename, as this can prevent Jekyll from properly processing the post.
- The date in the filename should match the date in the front matter (see next step).

## Step 2: Add the YAML front matter

At the top of your file, include this front matter:

```yaml
---
title: 'Your Blog Post Title'
date: YYYY-MM-DD
permalink: /posts/YYYY/MM/your-post-name/
tags:
  - tag1
  - tag2
  - tag3
---
```

For example:
```yaml
---
title: 'Securing Machine Learning Applications'
date: 2025-04-07
permalink: /posts/2025/04/securing-ml-applications/
tags:
  - machine learning
  - security
  - research
---
```

## Step 3: Write your blog post content

Below the front matter, write your blog content using Markdown:

### Basic Markdown formatting

```markdown
## Heading Level 2

### Heading Level 3

**Bold text**

*Italic text*

[Link text](https://example.com)

![Image alt text](/path/to/image.jpg)

> This is a blockquote

- Bullet point
- Another bullet point

1. Numbered item
2. Another numbered item
```

### Code blocks

You can include code snippets using triple backticks with the language specified:

````markdown
```python
def hello_world():
    print("Hello, world!")
```
````

### Math equations

You can include LaTeX math equations using MathJax:

```markdown
When $a \ne 0$, there are two solutions to $ax^2 + bx + c = 0$ and they are
$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}$$
```

## Step 4: Preview your post locally

Before publishing, you can preview your post locally by running:

```bash
bundle exec jekyll serve
```

Then visit `http://localhost:4000` in your browser.

## Step 5: Publish your post

Once you're satisfied with your post, commit it to the repository:

```bash
git add _posts/YYYY-MM-DD-your-post-title.md
git commit -m "Add new blog post: Your Post Title"
git push
```

## Example Blog Post

Here's a complete example of what a blog post file might look like:

```markdown
---
title: 'Securing Machine Learning Applications'
date: 2025-04-07
permalink: /posts/2025/04/securing-ml-applications/
tags:
  - machine learning
  - security
  - research
---

In this post, I'll discuss some of the key challenges in securing machine learning applications and some approaches I've been working on.

## The Problem

Machine learning models are vulnerable to various types of attacks, including:

1. Adversarial examples
2. Data poisoning
3. Model inversion

## Potential Solutions

Here are some approaches I've been researching:

### Adversarial Training

Adversarial training involves...

### Differential Privacy

Differential privacy provides...

## Conclusion

Securing machine learning systems remains an important challenge in the field...
```

## Where Your Posts Will Appear

When you publish a blog post following these instructions:

1. It will automatically appear on the blog page at `/archives/` in reverse chronological order (newest first).
2. Recent posts will also appear on the homepage in the "Recent Blog Posts" section.
3. The post will be accessible directly via its permalink (as specified in the front matter).

**Note**: If your post doesn't appear, check that:
- The filename follows the exact format `YYYY-MM-DD-title.md` without special characters
- The front matter has a valid date in `YYYY-MM-DD` format
- You've committed and pushed the file to the repository 