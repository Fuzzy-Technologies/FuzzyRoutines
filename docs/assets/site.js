/*
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
*/
'use strict';

// Keep the examples readable without JavaScript or clipboard permission.
const language = document.documentElement.lang;
const labels = language.startsWith('ru')
  ? {copy: 'Скопировать', copied: 'Скопировано', success: 'Скопировано в буфер обмена', fallback: 'Буфер обмена недоступен. Код выделен — скопируйте его средствами устройства.'}
  : language.startsWith('zh')
    ? {copy: '复制', copied: '已复制', success: '已复制到剪贴板', fallback: '剪贴板不可用。代码已选中，请使用设备的复制命令。'}
    : {copy: 'Copy', copied: 'Copied', success: 'Copied to clipboard', fallback: 'Clipboard unavailable. Code selected — use your device’s copy command.'};
const copy_status = document.getElementById('copy-status');
for (const button of document.querySelectorAll('[data-copy-target]')) {
  const target = document.getElementById(button.dataset.copyTarget);
  if (!target || !copy_status) continue;
  button.hidden = false;
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(target.textContent);
      button.textContent = labels.copied;
      copy_status.textContent = labels.success;
      window.setTimeout(() => { button.textContent = labels.copy; }, 2000);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(target);
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = labels.copy;
      copy_status.textContent = labels.fallback;
    }
  });
}
