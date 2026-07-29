/* Reading aids for long posts: a scroll-progress bar and a fixed section
   outline that tracks where you are.

   This lives in its own file rather than inline in the include. The site's
   default layout runs through _layouts/compress.html, which collapses the
   page onto a single line in production but is skipped in development
   (compress_html.ignore.envs). Inline script survives locally and then
   breaks live, because the first // comment swallows the rest of the file.
   Compression only rewrites HTML, so an external .js is immune. */

(function () {
  function build() {
    var content = document.querySelector('.post-content');
    var outline = document.getElementById('ro-outline');
    var bar = document.getElementById('ro-progress');
    if (!content || !outline) return;

    var titleEl = document.querySelector('.post > h1');
    var pageTitle = titleEl ? titleEl.textContent : '';
    var heads = [].slice.call(content.querySelectorAll('h1[id], h2[id]'))
      /* defensive: the layout already prints the title, so drop a body
         heading that repeats it rather than listing the post twice */
      .filter(function (h) { return h.textContent.trim() !== pageTitle.trim(); });

    if (heads.length < 3) return;

    var list = document.createElement('ul');
    var links = heads.map(function (h) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      if (h.tagName === 'H2') a.className = 'ro-sub';
      li.appendChild(a);
      list.appendChild(li);
      return a;
    });

    var label = document.createElement('h2');
    label.textContent = 'On this page';
    outline.appendChild(label);
    outline.appendChild(list);

    var active = -1;
    var ticking = false;

    function update() {
      ticking = false;

      var doc = document.documentElement;
      var scrolled = doc.scrollTop || document.body.scrollTop;
      var height = (doc.scrollHeight || document.body.scrollHeight) - doc.clientHeight;
      if (bar) bar.style.width = (height > 0 ? (scrolled / height) * 100 : 0) + '%';

      /* current section = last heading whose top has passed the read line */
      var line = 130;
      var i = 0;
      for (var n = 0; n < heads.length; n++) {
        if (heads[n].getBoundingClientRect().top <= line) i = n; else break;
      }
      if (i === active) return;

      if (links[active]) links[active].classList.remove('ro-active');
      links[i].classList.add('ro-active');
      active = i;

      /* keep the active entry visible when the outline itself scrolls */
      var box = outline.getBoundingClientRect();
      var cur = links[i].getBoundingClientRect();
      if (cur.bottom > box.bottom - 8) {
        outline.scrollTop += cur.bottom - box.bottom + 40;
      } else if (cur.top < box.top + 8) {
        outline.scrollTop -= box.top - cur.top + 40;
      }
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
  }

  /* The include sits partway down the post, so headings below it do not
     exist when this parses. Wait for the full document. */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
