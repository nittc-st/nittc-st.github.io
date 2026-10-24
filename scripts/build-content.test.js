import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { buildContent } from './build-content.js';

// テスト用の一時的なサイト構成を作成し、終了時の削除を登録する関数
async function fixture(t) {
    const root = await mkdtemp(path.join(os.tmpdir(), 'site-content-'));
    t.after(() => rm(root, { recursive: true, force: true }));

    for (const directory of [
        'content/blog',
        'content/document',
        'img',
        'components',
        'src',
        'js',
        'css',
    ]) {
        await mkdir(path.join(root, directory), { recursive: true });
    }

    await writeFile(path.join(root, 'index.html'), '<h1>Existing site</h1>');
    await writeFile(path.join(root, 'css/common.css'), 'body {}');
    await writeFile(path.join(root, 'img/logo.svg'), '<svg/>');

    return root;
}

test('generates sorted metadata, stripped Markdown, assets, and no drafts or build sources', async t => {
    const root = await fixture(t);
    const blog = path.join(root, 'content/blog');

    await writeFile(
        path.join(blog, 'old.md'),
        '---\ntitle: 古い記事\ndate: 2025-01-01\n---\n古い本文'
    );
    await writeFile(
        path.join(blog, 'new.md'),
        '---\ntitle: "新しい: 記事"\ndescription: >-\n  YAMLの概要\ndate: 2026-10-24\ntags: [Git, Git, " 初心者 "]\n---\n## 本文\n![画像](assets/test.svg)'
    );
    await writeFile(
        path.join(blog, 'undated.md'),
        '---\ntitle: 日付なし\n---\n本文'
    );
    await writeFile(
        path.join(blog, 'draft.md'),
        '---\ntitle: 下書き\ndraft: true\n---\n非公開本文'
    );

    await mkdir(path.join(blog, 'assets'));
    await writeFile(path.join(blog, 'assets/test.svg'), '<svg/>');
    await writeFile(path.join(blog, 'index.json'), '手動で書いた古いJSON');
    await writeFile(path.join(root, 'package.json'), '{}');

    await buildContent(root);

    const output = path.join(root, 'dist');
    const index = JSON.parse(await readFile(path.join(output, 'content/blog/index.json')));

    assert.deepEqual(
        index.map(article => article.slug),
        ['new', 'old', 'undated']
    );
    assert.deepEqual(index[0], {
        slug: 'new',
        title: '新しい: 記事',
        description: 'YAMLの概要',
        date: '2026-10-24',
        tags: ['Git', '初心者'],
    });
    assert.equal(index[2].date, null);
    assert.equal(
        await readFile(path.join(output, 'content/blog/new.md'), 'utf8'),
        '## 本文\n![画像](assets/test.svg)'
    );
    assert.equal(
        await readFile(path.join(output, 'content/blog/assets/test.svg'), 'utf8'),
        '<svg/>'
    );
    assert.equal(
        await readFile(path.join(output, 'img/logo.svg'), 'utf8'),
        '<svg/>'
    );
    assert.deepEqual(
        JSON.parse(await readFile(path.join(output, 'content/document/index.json'))),
        []
    );
    assert.ok(!(await readdir(path.join(output, 'content/blog'))).includes('draft.md'));
    assert.ok(!(await readdir(output)).includes('package.json'));
    assert.ok(!(await readdir(output)).includes('style.css'));
    assert.equal(await readFile(path.join(output, 'css/common.css'), 'utf8'), 'body {}');

    // A formerly public post must disappear on the next build when marked draft.
    await writeFile(
        path.join(blog, 'new.md'),
        '---\ntitle: 非公開に変更\ndraft: true\n---\n本文'
    );
    await buildContent(root);
    assert.ok(!(await readdir(path.join(output, 'content/blog'))).includes('new.md'));
});

test('publishes the 404 page and game HTML without game sources or tooling', async t => {
    const root = await fixture(t);
    const game = path.join(root, 'games/404-runner');
    await mkdir(game, { recursive: true });
    await writeFile(path.join(root, '404.html'), '<h1>404</h1>');
    await writeFile(path.join(game, 'game.html'), '<canvas></canvas>');
    await writeFile(path.join(game, 'main.py'), 'import pyxel');
    await writeFile(path.join(game, 'build_web.py'), 'import subprocess');

    await buildContent(root);

    assert.equal(await readFile(path.join(root, 'dist/404.html'), 'utf8'), '<h1>404</h1>');
    assert.equal(
        await readFile(path.join(root, 'dist/games/404-runner/game.html'), 'utf8'),
        '<canvas></canvas>'
    );
    assert.deepEqual(await readdir(path.join(root, 'dist/games/404-runner')), ['game.html']);
});

test('invalid metadata fails with the filename before replacing dist', async t => {
    const root = await fixture(t);
    await mkdir(path.join(root, 'dist'));
    await writeFile(path.join(root, 'dist/previous.txt'), 'previous');

    const cases = [
        'description: タイトルなし',
        'title: 123',
        'title: 記事\ndate: 2026-02-30',
        'title: 記事\ntags: Git',
        'title: 記事\ndraft: "false"',
        'title: 記事\ndescription: []',
        'title: 記事\ntitle: 重複キー',
    ];

    for (const metadata of cases) {
        await writeFile(
            path.join(root, 'content/blog/invalid.md'),
            `---\n${metadata}\n---\n本文`
        );
        await assert.rejects(buildContent(root), /invalid\.md:/);
    }

    await writeFile(
        path.join(root, 'content/blog/invalid.md'),
        '---javascript\n({title: "YAML以外"})\n---\n本文'
    );
    await assert.rejects(buildContent(root), /YAML Front Matter/);

    await writeFile(
        path.join(root, 'content/blog/invalid.md'),
        '---\ntitle: 閉じ忘れ\n'
    );
    await assert.rejects(buildContent(root), /閉じる---/);

    assert.equal(
        await readFile(path.join(root, 'dist/previous.txt'), 'utf8'),
        'previous'
    );
});
