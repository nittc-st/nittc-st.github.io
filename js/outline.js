// 記事の見出しに重複しないIDを付け、階層付きアウトラインを作成する関数
export function addOutline(article) {
    const headings = [...article.querySelectorAll('h1, h2, h3, h4, h5, h6')];
    const usedIds = new Set();
    for (const heading of headings) {
        const base = heading.textContent.trim().normalize('NFC').toLowerCase()
            .replace(/\s+/g, '-').replace(/[^\p{L}\p{N}_-]/gu, '') || 'section';
        let id = base;
        let suffix = 2;
        while (usedIds.has(id) || document.getElementById(id)) id = `${base}-${suffix++}`;
        heading.id = id;
        heading.tabIndex = -1;
        usedIds.add(id);
    }
    if (!article.querySelector('.markdown-body :is(h1, h2, h3, h4, h5, h6)')) return;

    const layout = document.createElement('div');
    layout.className = 'row g-4';
    const sidebar = document.createElement('aside');
    sidebar.className = 'col-lg-3 content-outline';
    const panel = document.createElement('div');
    panel.className = 'content-outline-panel border rounded p-3 bg-body';

    const label = document.createElement('p');
    label.className = 'fw-bold mb-2 d-none d-lg-block';
    label.textContent = 'アウトライン';
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'btn btn-outline-secondary w-100 text-start d-lg-none';
    toggle.textContent = 'アウトライン ▾';
    toggle.setAttribute('data-bs-toggle', 'collapse');
    toggle.setAttribute('data-bs-target', '#article-outline');
    toggle.setAttribute('aria-controls', 'article-outline');
    toggle.setAttribute('aria-expanded', 'false');

    const collapse = document.createElement('div');
    collapse.id = 'article-outline';
    collapse.className = 'collapse d-lg-block';
    const nav = document.createElement('nav');
    nav.id = 'article-outline-links';
    nav.className = 'nav-pills';
    nav.setAttribute('aria-label', '記事のアウトライン');
    const list = document.createElement('ul');
    list.className = 'list-unstyled mb-0';
    const stack = [];
    for (const heading of headings) {
        const level = Number(heading.tagName.slice(1));
        while (stack.length && stack.at(-1).level >= level) stack.pop();
        let parentList = list;
        if (stack.length) {
            const parent = stack.at(-1);
            if (!parent.children) {
                parent.children = document.createElement('ul');
                parent.children.className = 'list-unstyled ms-3';
                parent.item.append(parent.children);
            }
            parentList = parent.children;
        }
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.className = 'nav-link py-1 px-2';
        link.href = `#${encodeURIComponent(heading.id)}`;
        link.textContent = heading.textContent;
        item.append(link);
        parentList.append(item);
        stack.push({ level, item });
    }
    nav.append(list);
    collapse.append(nav);
    panel.append(label, toggle, collapse);
    sidebar.append(panel);
    const column = document.createElement('div');
    column.className = 'col-lg-9 content-article';
    layout.append(sidebar, column);
    article.replaceWith(layout);
    column.append(article);

    const links = [...nav.querySelectorAll('a')];
    let current = -1;
    let scheduled = false;

    // 画面上部を通過した最後の見出しを現在位置として強調する関数
    const markCurrent = () => {
        scheduled = false;
        let selected = 0;
        for (let index = 0; index < headings.length; index++) {
            if (headings[index].getBoundingClientRect().top <= innerHeight / 4) selected = index;
            else break;
        }
        if (selected === current) return;
        links[current]?.classList.remove('active');
        links[current]?.removeAttribute('aria-current');
        links[selected].classList.add('active');
        links[selected].setAttribute('aria-current', 'location');
        current = selected;
    };

    // スクロール・画面サイズ変更時の現在位置更新を描画単位にまとめる関数
    const scheduleUpdate = () => {
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(markCurrent);
    };
    addEventListener('scroll', scheduleUpdate, { passive: true });
    addEventListener('resize', scheduleUpdate);
    markCurrent();

    // アウトラインのリンク選択時にスマホ用メニューを閉じる関数
    nav.addEventListener('click', event => {
        if (event.target.closest('a') && !matchMedia('(min-width: 992px)').matches) {
            bootstrap.Collapse.getOrCreateInstance(collapse, { toggle: false }).hide();
        }
    });

    // 非同期で描画した本文でもURLのフラグメント位置に移動する。
    try {
        const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
        if (target && article.contains(target)) target.scrollIntoView();
    } catch {
        // 不正なパーセントエンコードのフラグメントは無視する。
    }
}
