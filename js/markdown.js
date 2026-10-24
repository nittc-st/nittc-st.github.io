import markdownit from 'https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/+esm';

// Raw HTML is disabled; markdown-it also rejects unsafe link/image protocols.
const markdown = markdownit({ html: false, linkify: false, breaks: false });

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
