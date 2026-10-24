import markdownit from 'https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/+esm';
import hljs from 'https://cdn.jsdelivr.net/npm/highlight.js@11.12.0/lib/common/+esm';
import http from 'https://cdn.jsdelivr.net/npm/highlight.js@11.12.0/lib/languages/http/+esm';

hljs.registerLanguage('http', http);

// 対応する言語のコードを色分けし、未指定・未対応の場合は通常表示に戻す関数
function highlightCode(source, language) {
    if (!language || !hljs.getLanguage(language)) {
        return '';
    }

    try {
        return hljs.highlight(source, {
            language,
            ignoreIllegals: true,
        }).value;
    } catch {
        // 空文字を返すとmarkdown-itが元のコードをHTMLエスケープする。
        return '';
    }
}

// Raw HTML is disabled; markdown-it also rejects unsafe link/image protocols.
const markdown = markdownit({
    html: false,
    linkify: false,
    breaks: false,
    langPrefix: 'hljs language-',
    highlight: highlightCode,
});

for (const [rule, attribute] of [
    ['link_open', 'href'],
    ['image', 'src'],
]) {
    const original = markdown.renderer.rules[rule];

    markdown.renderer.rules[rule] = (tokens, index, options, environment, renderer) => {
        const token = tokens[index];
        const value = token.attrGet(attribute);

        if (value && !value.startsWith('#')) {
            const url = new URL(value, environment.markdownUrl);

            // Markdown files in either collection open in the shared viewer.
            const contentRoot = new URL('../content/', import.meta.url);

            if (
                attribute === 'href'
                && url.origin === contentRoot.origin
                && url.pathname.startsWith(contentRoot.pathname)
            ) {
                const match = url.pathname
                    .slice(contentRoot.pathname.length)
                    .match(/^(blog|document)\/([^/]+)\.md$/);

                if (match) {
                    const page = new URL(`../src/${match[1]}.html`, import.meta.url);
                    page.searchParams.set('slug', decodeURIComponent(match[2]));
                    page.hash = url.hash;
                    token.attrSet(attribute, page.href);
                } else {
                    token.attrSet(attribute, url.href);
                }
            } else {
                token.attrSet(attribute, url.href);
            }
        }

        return original
            ? original(tokens, index, options, environment, renderer)
            : renderer.renderToken(tokens, index, options);
    };
}

// Markdown本文を相対リンクの基準URLを指定してHTMLに変換する関数
export function renderMarkdown(source, markdownUrl) {
    return markdown.render(source, { markdownUrl });
}
