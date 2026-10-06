async function loadComponent(selecter, path) {
    const response = await fetch(path);

    if (!response.ok) {
        throw new Error(`${response.status}\n${response.statusText}`);
    }

    const html = await response.text();

    document.querySelector(selecter).innerHTML = html;
}

const navbarUrl = new URL("../components/navbar.html", import.meta.url);

loadComponent("#navbar", navbarUrl);