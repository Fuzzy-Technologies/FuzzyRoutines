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
  assert.ok(file === root || file.startsWith(root + path.sep), 'Asset path escapes the permitted root');
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!fs.existsSync(file)) return route.fulfill({status: 404, body: relative});
  return route.fulfill({headers: {'access-control-allow-origin': '*'}, contentType: mimeTypes[path.extname(file)] || 'application/octet-stream', body: fs.readFileSync(file)});
}

async function InspectImageViewer(page, selector, screenshot) {
  const image = page.locator(selector).first();
  const trigger = image.locator('xpath=ancestor-or-self::*[@aria-haspopup="dialog"][1]');
  const viewer = page.locator('#image-viewer');
  const initialUrl = page.url();
  const source = await image.getAttribute('src');
  assert.ok(await trigger.evaluate(element => element.tabIndex >= 0), 'Image viewer is keyboard accessible');
  await trigger.focus();
  await page.keyboard.press('Enter');
  await viewer.waitFor({state: 'visible'});
  assert.equal(page.url(), initialUrl, 'Enlarging an image keeps the current document');
  assert.equal(await viewer.locator('img').getAttribute('src'), new URL(source, initialUrl).href);
  await viewer.locator('img').evaluate(async image => {await image.decode();});
  assert.equal(await viewer.locator('img').getAttribute('alt'), await image.getAttribute('alt'));
  assert.ok(await viewer.getAttribute('aria-label'), 'Viewer has an accessible name');
  assert.ok(await viewer.locator('[data-close-viewer]').getAttribute('aria-label'), 'Close control has an accessible name');
  await page.screenshot({path: path.join(outputRoot, screenshot), animations: 'disabled'});
  await page.keyboard.press('Escape');
  await viewer.waitFor({state: 'hidden'});
  assert.ok(await trigger.evaluate(element => document.activeElement === element), 'Escape restores focus to the image');
  await trigger.click();
  await viewer.locator('[data-close-viewer]').click();
  await viewer.waitFor({state: 'hidden'});
  assert.ok(await trigger.evaluate(element => document.activeElement === element), 'Close control restores focus');
  await trigger.click();
  await page.mouse.click(2, 2);
  await viewer.waitFor({state: 'hidden'});
  assert.ok(await trigger.evaluate(element => document.activeElement === element), 'Backdrop restores focus');
  assert.equal(page.url(), initialUrl, 'Closing the viewer keeps the current document');
  return {keyboard: true, sameDocument: true, close: ['Escape', 'button', 'backdrop'], focusRestored: true, screenshot};
}

async function InspectTypography(page) {
  const result = await page.evaluate(() => ({
    textFont: getComputedStyle(document.body).fontFamily,
    firaLoaded: [...document.fonts].some(font => font.family.replaceAll('"', '') === 'Fira Code' && font.status === 'loaded'),
    backgrounds: [document.documentElement, document.body].map(element => getComputedStyle(element).backgroundColor),
    mathFonts: [...document.querySelectorAll('mjx-math')].map(element => getComputedStyle(element).fontFamily),
    mathRenderers: [...document.querySelectorAll('mjx-container')].map(element => ({jax: element.getAttribute('jax'), svg: !!element.querySelector('svg')})),
  }));
  assert.match(result.textFont, /Fira Code/, 'Corporate font is applied');
  assert.equal(result.firaLoaded, true, 'Corporate font is loaded from local assets');
  assert.ok(result.backgrounds.includes('rgb(7, 9, 13)'), 'Corporate dark background is applied');
  for (const renderer of result.mathRenderers) {
    assert.equal(renderer.jax, 'SVG', 'Mathematics uses the corporate SVG renderer');
    assert.equal(renderer.svg, true, 'Mathematical glyphs render as vectors');
  }
  for (const font of result.mathFonts) assert.match(font, /MJX/, 'Mathematics retains MathJax glyph fonts');
  return result;
}

async function InspectLanding(context, viewport, evidence) {
  const page = await context.newPage();
  await page.setViewportSize(viewport);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('requestfailed', request => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
  // Exercise both browser permission outcomes without depending on host permissions.
  await page.addInitScript(() => {
    window.copiedText = null;
    window.denyClipboard = false;
    Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
      async writeText(value) {
        if (window.denyClipboard) throw new DOMException('Permission denied', 'NotAllowedError');
        window.copiedText = value;
      },
    }});
  });
  const url = `${origin}/FuzzyRoutines/`;
  const response = await page.goto(url, {waitUntil: 'networkidle', timeout: 30000});
  assert.equal(response.status(), 200, url);
  await page.evaluate(() => document.fonts.ready);
  const result = await page.evaluate(() => ({
    title: document.title,
    overflow: document.documentElement.scrollWidth > innerWidth + 1,
    brokenImages: [...document.images].filter(image => image.getAttribute('src') && (!image.complete || !image.naturalWidth)).map(image => image.src),
    emptyAlternatives: [...document.images].filter(image => image.getAttribute('src') && !image.alt.trim()).map(image => image.src),
    headings: [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(element => ({text: element.textContent.trim(), size: parseFloat(getComputedStyle(element).fontSize)})),
  }));
  result.typography = await InspectTypography(page);
  assert.equal(result.overflow, false, `${url}: page-level overflow`);
  assert.deepEqual(result.brokenImages, [], url);
  assert.deepEqual(result.emptyAlternatives, [], url);
  assert.ok(result.headings.length > 0, 'Landing page has headings');
  for (const heading of result.headings) {
    assert.ok(!/[.\u3002]\s*$/.test(heading.text), `Heading ends with a full stop: ${heading.text}`);
    assert.ok(heading.size <= 40, `Oversized heading: ${heading.text} (${heading.size}px)`);
  }
  assert.ok((await page.locator('#quickstart-output').innerText()).trim(), 'Quick start displays its expected output');
  const status = page.locator('#copy-status');
  assert.ok(await status.getAttribute('aria-live') || await status.getAttribute('role') === 'status', 'Clipboard feedback is announced');
  result.clipboard = [];
  for (const target of ['install-command', 'quickstart-code']) {
    const button = page.locator(`button.copy-button[data-copy-target="${target}"]`);
    const source = await page.locator(`#${target}`).textContent();
    assert.equal(await button.count(), 1, `${target}: accessible native button`);
    assert.ok(await button.evaluate(element => !element.disabled && element.tabIndex >= 0), `${target}: keyboard focusable`);
    await button.focus();
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => window.copiedText !== null);
    assert.equal(await page.evaluate(() => window.copiedText), source.trim(), `${target}: copied code`);
    assert.match(await button.innerText(), /copied/i, `${target}: success feedback`);
    result.clipboard.push({target, success: true, keyboard: true});
    await page.evaluate(() => {window.copiedText = null;});
  }
  await page.evaluate(() => {window.denyClipboard = true;});
  const priorStatus = await status.textContent();
  await page.locator('button.copy-button[data-copy-target="quickstart-code"]').click();
  await page.waitForFunction(previous => document.querySelector('#copy-status').textContent.trim() && document.querySelector('#copy-status').textContent !== previous, priorStatus);
  assert.equal(await page.evaluate(() => window.getSelection().toString()), (await page.locator('#quickstart-code').textContent()).trim(), 'Denied clipboard selects the code for manual copy');
  assert.equal(await page.evaluate(() => window.copiedText), null, 'Denied clipboard does not claim a write');
  result.clipboardFallback = {selected: true, status: (await status.textContent()).trim()};
  result.imageViewers = [];
  for (const [name, selector] of [['banner', 'main .project-art'], ['figure', 'main figure img']]) {
    result.imageViewers.push(await InspectImageViewer(page, selector, `landing-${name}-viewer-${viewport.width}.png`));
  }
  result.overflowAfterInteraction = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
  await page.evaluate(() => {window.getSelection().removeAllRanges(); document.activeElement.blur(); window.scrollTo({top: 0, behavior: 'instant'});});
  const screenshot = `landing-${viewport.width}.png`;
  await page.screenshot({path: path.join(outputRoot, screenshot), fullPage: true, animations: 'disabled'});
  evidence.pages.push({locale: 'en', route: '/', viewport, ...result, errors, screenshot});
  assert.equal(result.overflowAfterInteraction, false, `${url}: overflow after interaction`);
  assert.deepEqual(errors, [], url);
  await page.close();
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
      await InspectLanding(context, viewport, evidence);
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
          brokenImages: [...document.images].filter(image => image.getAttribute('src') && (!image.complete || !image.naturalWidth)).map(image => image.src),
          emptyAlternatives: [...document.images].filter(image => image.getAttribute('src') && !image.alt.trim()).map(image => image.src),
          mathBlocks: document.querySelectorAll('.arithmatex').length,
          renderedMath: document.querySelectorAll('mjx-container').length,
          mathErrors: [...document.querySelectorAll('mjx-merror,[data-mjx-error]')].map(element => element.textContent),
          languages: [...document.querySelectorAll('a[hreflang]')].map(link => ({language: link.hreflang, path: new URL(link.href).pathname})),
        }));
        result.typography = await InspectTypography(page);
        if (pageRoute === 'guides/universal-fuzzy-scale') {
          result.imageViewer = await InspectImageViewer(page, '.md-content img', `${locale}-universal-scale-viewer-${viewport.width}.png`);
          const query = page.locator('input[data-md-component="search-query"]');
          if (!await query.isVisible()) await page.locator('label[for="__search"]:visible').first().click();
          await query.focus();
          await page.waitForFunction(() => {
            const translations = JSON.parse(document.getElementById('__config').textContent).translations;
            return document.querySelector('.md-search-result__meta').textContent.trim() === translations['search.result.placeholder'];
          });
          // Material observes keyup; fill() alone only emits an input event.
          await query.pressSequentially('UniversalFuzzyScale');
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
