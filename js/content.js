import { addOutline } from './outline.js';

const container = document.querySelector('[data-content-type]');
const type = container.dataset.contentType;
const pageTitle = document.title;
const contentUrl = new URL(`../content/${type}/`, import.meta.url);

// 指定したタグ・クラス・テキストでHTML要素を作成する関数
function element(tag, className, text) {
    const node = document.createElement(tag);
    node.className = className;

    if (text !== undefined) {
        node.textContent = text;
    }

    return node;
}

// コンテンツの日付とタグを表示する要素を作成する関数
function metadata(article) {
    const node = element('div', 'd-flex flex-wrap align-items-center gap-2 mb-3');

    if (article.date) {
        const date = element('time', 'text-body-secondary', article.date);
        date.dateTime = article.date;
        node.append(date);
    }
    for (const tag of article.tags) {
        node.append(element('span', 'badge text-bg-secondary', tag));
    }

    return node;
}

// 指定したURLからJSONまたはテキストを取得する関数
async function fetchContent(url, json = false) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${url}`);
    }

    return json ? response.json() : response.text();
}

// コンテンツの一覧をカード形式で表示する関数
function showList(articles) {
    container.replaceChildren();

    if (!articles.length) {
        container.append(
            element('p', 'text-body-secondary', '公開されているコンテンツはありません。')
        );
        return;
    }

    const list = element('div', 'row g-3');

    for (const article of articles) {
        const column = element('div', 'col-12 col-md-6');
        const card = element('article', 'card h-100');
        const body = element('div', 'card-body');
        const heading = element('h2', 'h5 card-title');
        const link = element('a', 'text-body-emphasis', article.title);

        const url = new URL(location.href);
        url.search = '';
        url.hash = '';
        url.searchParams.set('slug', article.slug);
        link.href = url;

        heading.append(link);
        body.append(heading, metadata(article));

        if (article.description) {
            body.append(element('p', 'card-text', article.description));
        }

        card.append(body);
        column.append(card);
        list.append(column);
    }

    container.append(list);
}

// URLのslugに応じて一覧またはMarkdown本文を取得・表示する関数
async function showContent() {
    const slug = new URL(location.href).searchParams.get('slug');
    document.querySelector('#page-heading').hidden = slug !== null;

    try {
        const articles = await fetchContent(new URL('index.json', contentUrl), true);

        if (slug === null) {
            showList(articles);
            return;
        }

        const article = articles.find(item => item.slug === slug);

        if (!article) {
            container.replaceChildren(
                element('h1', 'h3 page-heading', 'コンテンツが見つかりません。')
            );
            return;
        }

        const markdownUrl = new URL(
            `${encodeURIComponent(article.slug)}.md`,
            contentUrl
        );
        const [source, { renderMarkdown }] = await Promise.all([
            fetchContent(markdownUrl),
            import('./markdown.js'),
        ]);

        const body = element('div', 'markdown-body');
        body.innerHTML = renderMarkdown(source, markdownUrl);

        const detail = element('article', '');
        detail.append(
            element('h1', 'article-title mb-3', article.title),
            metadata(article),
            body
        );

        container.replaceChildren(detail);
        addOutline(detail);
        document.title = `${article.title} | ${pageTitle}`;
    } catch (error) {
        console.error('コンテンツの読み込みに失敗しました。', error);

        const message = element(
            'p',
            'alert alert-danger',
            '読み込みに失敗しました。時間をおいて再度お試しください。'
        );
        message.setAttribute('role', 'alert');
        container.replaceChildren(message);
    } finally {
        container.setAttribute('aria-busy', 'false');
    }
}

showContent();
