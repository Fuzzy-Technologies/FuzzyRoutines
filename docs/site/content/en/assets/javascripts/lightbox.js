/*
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
*/
'use strict';

(() => {
  const language = document.documentElement.lang;
  const labels = language.startsWith('ru')
    ? {open: 'Увеличить изображение', close: 'Закрыть изображение', title: 'Просмотр изображения'}
    : language.startsWith('zh')
      ? {open: '放大图片', close: '关闭图片', title: '图片预览'}
      : {open: 'Enlarge image', close: 'Close image', title: 'Image preview'};
  const viewer = document.createElement('dialog');
  // Native modal semantics keep focus inside and the background inert.
  if (typeof viewer.showModal !== 'function') return;
  viewer.id = 'image-viewer';
  viewer.setAttribute('aria-label', labels.title);
  const panel = document.createElement('div');
  panel.className = 'image-viewer-panel';
  const expanded = document.createElement('img');
  const caption = document.createElement('p');
  const close_button = document.createElement('button');
  close_button.type = 'button';
  close_button.dataset.closeViewer = '';
  close_button.setAttribute('aria-label', labels.close);
  close_button.textContent = '×';
  panel.append(close_button, expanded, caption);
  viewer.append(panel);
  document.body.append(viewer);
  let opener = null;
  close_button.addEventListener('click', () => viewer.close());
  viewer.addEventListener('click', event => {
    if (event.target === viewer) viewer.close();
  });
  viewer.addEventListener('close', () => {
    document.documentElement.classList.remove('image-viewer-open');
    if (opener?.isConnected) opener.focus({preventScroll: true});
  });

  for (const image of document.querySelectorAll('.md-content img, main .project-art, main figure img')) {
    const anchor = image.closest('a');
    // Preserve navigation links containing icons or linked project logos.
    if (anchor && !/\.(svg|png|jpe?g|webp|gif)(?:[?#]|$)/i.test(anchor.href)) continue;
    const trigger = anchor || image;
    trigger.classList.add('image-viewer-trigger');
    trigger.setAttribute('aria-haspopup', 'dialog');
    trigger.setAttribute('aria-label', `${labels.open}: ${image.alt}`);
    if (!anchor) {
      trigger.tabIndex = 0;
      trigger.setAttribute('role', 'button');
    }
    const OpenImage = event => {
      event.preventDefault();
      opener = trigger;
      expanded.src = image.currentSrc || image.src;
      expanded.alt = image.alt;
      caption.textContent = image.alt;
      viewer.showModal();
      document.documentElement.classList.add('image-viewer-open');
      close_button.focus();
    };
    trigger.addEventListener('click', OpenImage);
    trigger.addEventListener('keydown', event => {
      if (event.key === ' ' || (!anchor && event.key === 'Enter')) OpenImage(event);
    });
  }
})();
