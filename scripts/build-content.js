import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import { parse } from 'yaml';

const projectRoot = fileURLToPath(new URL('../', import.meta.url));
const types = ['blog', 'document'];

// Front Matterのメタデータを検証し、形式を統一する関数
function normalizeMetadata(data) {
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
        throw new Error('Front Matterはマッピング形式で指定してください。');
    }

    if (typeof data.title !== 'string' || !data.title.trim()) {
        throw new Error('titleには空でない文字列が必要です。');
    }

    if (data.description !== undefined && typeof data.description !== 'string') {
        throw new Error('descriptionは文字列で指定してください。');
    }

    if (data.draft !== undefined && typeof data.draft !== 'boolean') {
        throw new Error('draftはtrueまたはfalseで指定してください。');
    }

    if (
        data.tags !== undefined
        && (
            !Array.isArray(data.tags)
            || data.tags.some(tag => typeof tag !== 'string' || !tag.trim())
        )
    ) {
        throw new Error('tagsは空でない文字列の配列で指定してください。');
    }

    if (data.date !== undefined) {
        if (
            typeof data.date !== 'string'
            || !/^\d{4}-\d{2}-\d{2}$/.test(data.date)
            || !Number.isFinite(Date.parse(data.date))
            || new Date(data.date).toISOString().slice(0, 10) !== data.date
        ) {
            throw new Error('dateは実在する日付をYYYY-MM-DD形式で指定してください。');
        }
    }

    return {
        title: data.title.trim(),
        description: data.description?.trim() ?? '',
        date: data.date ?? null,
        tags: [...new Set((data.tags ?? []).map(tag => tag.trim()))],
        draft: data.draft ?? false,
    };
}

// ディレクトリを走査し、公開対象の記事と添付ファイルを収集する関数
async function collectContent(directory, relative = '') {
    const articles = [];
    const assets = [];

    for (const entry of await readdir(path.join(directory, relative), {
        withFileTypes: true,
    })) {
        if (entry.name.startsWith('.')) {
            continue;
        }

        const filename = path.join(relative, entry.name);

        if (entry.isSymbolicLink()) {
            throw new Error(`${filename}: シンボリックリンクは使用できません。`);
        }

        if (entry.isDirectory()) {
            const nested = await collectContent(directory, filename);
            articles.push(...nested.articles);
            assets.push(...nested.assets);
        } else if (entry.isFile() && /\.md$/i.test(entry.name)) {
            try {
                if (relative) {
                    throw new Error('Markdownはコンテンツ種別ディレクトリの直下に配置してください。');
                }

                const slug = entry.name.slice(0, -3);

                if (!/^[\p{L}\p{N}_-]+$/u.test(slug)) {
                    throw new Error('ファイル名には文字・数字・ハイフン・アンダースコアを使用してください。');
                }

                const source = await readFile(path.join(directory, filename), 'utf8');

                if (!/^---\r?\n/.test(source)) {
                    throw new Error('先頭に---で始まるYAML Front Matterが必要です。');
                }

                if (
                    !source
                        .split(/\r?\n/)
                        .slice(1)
                        .some(line => /^---[ \t]*$/.test(line))
                ) {
                    throw new Error('Front Matterを閉じる---行が必要です。');
                }

                const parsed = matter(source, {
                    engines: {
                        yaml: text => parse(text),
                    },
                });
                const { draft, ...metadata } = normalizeMetadata(parsed.data);

                if (!draft) {
                    articles.push({ slug, ...metadata, body: parsed.content });
                }
            } catch (error) {
                throw new Error(
                    `${path.join(directory, filename)}: ${error.message}`,
                    { cause: error }
                );
            }
        } else if (entry.isFile() && entry.name !== 'index.json') {
            assets.push(filename);
        }
    }

    return { articles, assets };
}

// 静的ファイル・公開用Markdown・一覧JSONをdistに生成する関数
export async function buildContent(root = projectRoot) {
    // Validate all metadata before replacing the previous generated output.
    const collections = new Map();

    for (const type of types) {
        const collection = await collectContent(path.join(root, 'content', type));
        const slugs = new Set();

        for (const article of collection.articles) {
            if (slugs.has(article.slug)) {
                throw new Error(`${type}: slugが重複しています: ${article.slug}`);
            }

            slugs.add(article.slug);
        }

        collection.articles.sort((a, b) =>
            (b.date ?? '').localeCompare(a.date ?? '')
            || a.slug.localeCompare(b.slug, 'en')
        );
        collections.set(type, collection);
    }

    const dist = path.join(root, 'dist');
    await rm(dist, { recursive: true, force: true });
    await mkdir(dist, { recursive: true });

    // Copy only website directories, never repository metadata, tooling or raw content.
    for (const name of [
        'index.html',
        'style.css',
        'src',
        'js',
        'css',
        'components',
        'img',
    ]) {
        try {
            await cp(path.join(root, name), path.join(dist, name), { recursive: true });
        } catch (error) {
            if (error.code !== 'ENOENT') {
                throw error;
            }

            if (name === 'index.html' || name === 'style.css') {
                throw error;
            }
        }
    }

    await writeFile(path.join(dist, '.nojekyll'), '');

    for (const [type, { articles, assets }] of collections) {
        const output = path.join(dist, 'content', type);
        await mkdir(output, { recursive: true });

        for (const asset of assets) {
            await mkdir(path.dirname(path.join(output, asset)), { recursive: true });
            await cp(path.join(root, 'content', type, asset), path.join(output, asset));
        }

        for (const article of articles) {
            await writeFile(path.join(output, `${article.slug}.md`), article.body);
        }

        const index = articles.map(({ body, ...metadata }) => metadata);
        await writeFile(
            path.join(output, 'index.json'),
            `${JSON.stringify(index, null, 2)}\n`
        );
        console.log(`${type}: ${index.length}件を生成しました。`);
    }
}

if (
    process.argv[1]
    && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
    buildContent().catch(error => {
        console.error(error.message);
        process.exitCode = 1;
    });
}
