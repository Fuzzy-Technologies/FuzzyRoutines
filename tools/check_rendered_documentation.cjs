/*
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
*/

// Browser evidence for the existing built preview; no human approval is inferred.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const dependencyRoot = path.resolve('_build/browser-dependencies/node_modules');
const { chromium } = require(path.join(dependencyRoot, 'playwright'));
const previewRoot = path.resolve(process.argv[2] || '_build/pages/review');
const outputRoot = path.resolve(process.argv[3] || '_build/browser-review');
const origin = 'http://documentation.test';
const locales = ['en', 'ru', 'zh-CN'];
const routes = ['guides/universal-fuzzy-scale', 'quick-start', 'contracts/compatibility', 'migration/1.0.3-to-2.0.0'];
const mimeTypes = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json', '.woff': 'font/woff', '.woff2': 'font/woff2'};

async function ServeFile(route, root, relative) {
  let file = path.resolve(root, '.' + relative);
  assert.ok(file.startsWith(root + path.sep), 'Asset path escapes the permitted root');
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!fs.existsSync(file)) return route.fulfill({status: 404, body: relative});
  return route.fulfill({headers: {'access-control-allow-origin': '*'}, contentType: mimeTypes[path.extname(file)] || 'application/octet-stream', body: fs.readFileSync(file)});
}

async function Main() {
  fs.mkdirSync(outputRoot, {recursive: true});
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext();
  const evidence = {sourceRevision: process.env.GITHUB_SHA || null, browser: browser.version(), offlineRepositoryMetadata: true, pages: [], figures: [], errors: []};
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin === origin) return ServeFile(route, previewRoot, decodeURIComponent(url.pathname).replace(/^\/FuzzyRoutines\//, '/'));
    if (url.href.startsWith('https://cdn.jsdelivr.net/npm/mathjax@3.2.2/')) {
      return ServeFile(route, path.join(dependencyRoot, 'mathjax'), decodeURIComponent(url.pathname).replace('/npm/mathjax@3.2.2', ''));
    }
    // Use installed system fonts, including Noto CJK, without CDN requests.
    if (url.hostname === 'fonts.googleapis.com') return route.fulfill({contentType: 'text/css', body: ''});
    // Repository badges are optional metadata, unavailable in this offline review.
    // Return a real HTTP error instead of a failed transport or invented release.
    if (url.origin === 'https://api.github.com' &&
        ['/repos/Fuzzy-Technologies/FuzzyRoutines', '/repos/Fuzzy-Technologies/FuzzyRoutines/releases/latest'].includes(url.pathname)) {
      return route.fulfill({status: 503, headers: {'access-control-allow-origin': '*'}, contentType: 'application/json', body: '{"message":"Repository metadata unavailable in offline browser review"}'});
    }
    return route.abort('blockedbyclient');
  });
  try {
    for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
      for (const locale of locales) for (const pageRoute of routes) {
        const page = await context.newPage();
        await page.setViewportSize(viewport);
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        page.on('requestfailed', request => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
        const url = `${origin}/FuzzyRoutines/api/latest/${locale}/${pageRoute}/`;
        const response = await page.goto(url, {waitUntil: 'networkidle', timeout: 30000});
        assert.equal(response.status(), 200, url);
        await page.waitForFunction(() => window.MathJax?.startup?.document, null, {timeout: 15000});
        await page.evaluate(async () => {await window.MathJax.startup.promise; await document.fonts.ready;});
        const result = await page.evaluate(() => ({
          title: document.title,
          overflow: document.documentElement.scrollWidth > innerWidth + 1,
          brokenImages: [...document.images].filter(image => !image.complete || !image.naturalWidth).map(image => image.src),
          emptyAlternatives: [...document.images].filter(image => !image.alt.trim()).map(image => image.src),
          mathBlocks: document.querySelectorAll('.arithmatex').length,
          renderedMath: document.querySelectorAll('mjx-container').length,
          mathErrors: [...document.querySelectorAll('mjx-merror,[data-mjx-error]')].map(element => element.textContent),
          languages: [...document.querySelectorAll('a[hreflang]')].map(link => ({language: link.hreflang, path: new URL(link.href).pathname})),
        }));
        if (pageRoute === 'guides/universal-fuzzy-scale') {
          const query = page.locator('input[data-md-component="search-query"]');
          if (!await query.isVisible()) await page.locator('label[for="__search"]:visible').first().click();
          await query.fill('UniversalFuzzyScale');
          const searchResults = page.locator('[data-md-component="search-result"] a.md-search-result__link');
          await searchResults.first().waitFor({state: 'visible', timeout: 15000});
          result.search = {query: 'UniversalFuzzyScale', results: await searchResults.count(), firstLink: await searchResults.first().getAttribute('href')};
          await page.screenshot({path: path.join(outputRoot, `${locale}-search-${viewport.width}.png`), fullPage: false, animations: 'disabled'});
          if (viewport.width < 960 && await page.locator('#__search').isChecked()) {
            await page.locator('label.md-search__icon[for="__search"]').click();
          } else {
            await page.keyboard.press('Escape');
          }
          await page.waitForFunction(() => !document.querySelector('#__search').checked);
        }
        const screenshot = `${locale}-${pageRoute.replaceAll('/', '-')}-${viewport.width}.png`;
        const pixels = await page.screenshot({path: path.join(outputRoot, screenshot), fullPage: true, animations: 'disabled'});
        result.screenshotWidth = pixels.readUInt32BE(16);
        result.overflowAfterInteraction = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
        evidence.pages.push({locale, route: pageRoute, viewport, ...result, errors, screenshot});
        assert.deepEqual(errors, [], url);
        assert.equal(result.screenshotWidth, viewport.width, `${url}: screenshot width after interaction`);
        assert.equal(result.overflowAfterInteraction, false, `${url}: overflow after interaction`);
        assert.equal(result.overflow, false, `${url}: page-level overflow`);
        assert.deepEqual(result.brokenImages, [], url);
        assert.deepEqual(result.emptyAlternatives, [], url);
        assert.deepEqual(result.mathErrors, [], url);
        assert.equal(result.renderedMath, result.mathBlocks, `${url}: unrendered mathematics`);
        for (const target of locales) assert.ok(result.languages.some(link => link.language === target && link.path === `/FuzzyRoutines/api/latest/${target}/${pageRoute}/`), `${url}: language route ${target}`);
        await page.close();
      }
      // Include every actual scientific asset as a reviewable responsive image.
      const figures = fs.readdirSync(path.join(previewRoot, 'api/latest/en/assets/figures')).filter(name => name.endsWith('.svg')).sort();
      assert.ok(figures.length >= 11, 'Expected complete scientific figure set');
      for (const figure of figures) {
        const page = await context.newPage();
        await page.setViewportSize(viewport);
        await page.setContent(`<html><body style="margin:0;background:#101827"><img alt="${figure}" style="display:block;width:100%;height:auto" src="${origin}/FuzzyRoutines/api/latest/en/assets/figures/${figure}"></body></html>`, {waitUntil: 'networkidle'});
        assert.ok(await page.locator('img').evaluate(image => image.complete && image.naturalWidth > 0), figure);
        const screenshot = `figure-${figure}-${viewport.width}.png`;
        await page.screenshot({path: path.join(outputRoot, screenshot), fullPage: true, animations: 'disabled'});
        evidence.figures.push({figure, viewport, screenshot});
        await page.close();
      }
    }
  } catch (error) {
    evidence.errors.push(error.message);
    throw error;
  } finally {
    fs.writeFileSync(path.join(outputRoot, 'report.json'), JSON.stringify(evidence, null, 2) + '\n');
    await browser.close();
  }
  console.log(`Rendered documentation: ${evidence.pages.length} pages, ${evidence.figures.length} figure views; PASS`);
}

Main().catch(error => {console.error(error); process.exitCode = 1;});
