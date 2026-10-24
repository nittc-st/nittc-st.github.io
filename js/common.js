// 共通部品のHTMLを取得し、指定した要素内に表示する関数
async function loadComponent(selecter, path) {
    const response = await fetch(path);

    if (!response.ok) {
        throw new Error(`${response.status}\n${response.statusText}`);
    }

    const html = await response.text();

    document.querySelector(selecter).innerHTML = html;
}

const navbarUrl = new URL("../components/navbar.html", import.meta.url);

loadComponent("#navbar", navbarUrl).then(() => {
    document.querySelectorAll("#navbar a[href]").forEach(a => {
        a.href = new URL(a.getAttribute("href"), new URL("../", import.meta.url));
    });
});

const footerUrl = new URL("../components/footer.html", import.meta.url);

loadComponent("#footer", footerUrl);
