/* jshint esversion: 6, strict: true */

const input = document.querySelector('input');
const form = input.parentNode;

input.addEventListener('focus', focus);
input.addEventListener('blur', blur);

function focus() {
    'use strict';
    form.setAttribute('style', 'box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2),' +
            '0 0 0 1px rgba(0, 0, 0, 0.08);');
}

function blur() {
    'use strict';
    form.setAttribute('style', 'box-shadow: 0 2px 2px rgba(0, 0, 0, 0.16),' +
            '0 0 0 1px rgba(0, 0, 0, 0.08);');
}
