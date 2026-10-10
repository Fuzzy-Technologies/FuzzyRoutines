/*
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
*/
'use strict';

// Keep the examples readable without JavaScript or clipboard permission.
const copy_status = document.getElementById('copy-status');
for (const button of document.querySelectorAll('[data-copy-target]')) {
  const target = document.getElementById(button.dataset.copyTarget);
  if (!target || !copy_status) continue;
  button.hidden = false;
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(target.textContent);
      button.textContent = 'Copied';
      copy_status.textContent = 'Copied to clipboard';
      window.setTimeout(() => { button.textContent = 'Copy'; }, 2000);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(target);
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = 'Copy';
      copy_status.textContent = 'Clipboard unavailable. Code selected — use your device’s copy command.';
    }
  });
}
