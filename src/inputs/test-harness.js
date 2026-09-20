// Test-harness runtime.
(function () {
    'use strict';

    const noteTypeEls = Array.from(document.querySelectorAll('template[data-note-type]'));
    const testcaseEls = Array.from(document.querySelectorAll('template[data-testcase]'));
    const cardEl = document.getElementById('test-harness-card');

    const noteTypeNames = uniqueInOrder(noteTypeEls.map(el => el.dataset.noteType));
    const testcaseNames = testcaseEls.map(el => el.dataset.testcase);
    const sides = ['front', 'back'];

    function uniqueInOrder(values) {
        return values.filter((value, index) => values.indexOf(value) === index);
    }

    const params = new URLSearchParams(location.hash.replace(/^#/, ''));
    const noteType = pick(params.get('noteType'), noteTypeNames);
    // Start on the front side by default
    const side = sides.indexOf(params.get('side')) !== -1 ? params.get('side') : 'front';
    const testcaseName = pick(params.get('testcase'), testcaseNames);

    function pick(requested, available) {
        return available.indexOf(requested) !== -1 ? requested : available[0];
    }

    // Fill the glossary slot inside the selected note-type template from the
    // selected test case template, then clone the result into cardEl. Note
    // that this will cause the card script (glossary-logic.js) to execute.
    const selectedNoteType = noteTypeEls.find(el => el.dataset.noteType === noteType && el.dataset.side === side);
    const selectedTestcase = testcaseEls.find(el => el.dataset.testcase === testcaseName);
    if (selectedNoteType) {
        const glossaryEl = selectedTestcase && selectedNoteType.content.querySelector('#glossary-input');
        if (glossaryEl) {
            glossaryEl.appendChild(selectedTestcase.content.cloneNode(true));
        }
        cardEl.appendChild(selectedNoteType.content.cloneNode(true));
    }

    // Changing any control reloads the page rather than re-running initialize().
    // initialize() ends with addEventListener('keydown', ...) and never removes
    // it, so calling it a second time would stack handlers. A reload also resets
    // the definitionIndex/definitions globals.
    function reloadWith(nextNoteType, nextSide, nextTestcase) {
        location.hash = 'noteType=' + encodeURIComponent(nextNoteType) +
            '&side=' + encodeURIComponent(nextSide) +
            '&testcase=' + encodeURIComponent(nextTestcase);
        location.reload();
    }

    const noteTypeSelect = document.getElementById('test-harness-note-type');
    const testcaseSelect = document.getElementById('test-harness-testcase');
    const flipButton = document.getElementById('test-harness-flip');

    fillSelect(noteTypeSelect, noteTypeNames, noteType);
    fillSelect(testcaseSelect, testcaseNames, testcaseName);
    updateFlipButton();

    function fillSelect(select, names, selected) {
        if (!select) {
            return;
        }
        for (const name of names) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            option.selected = name === selected;
            select.appendChild(option);
        }
    }

    function updateFlipButton() {
        if (flipButton) {
            flipButton.textContent = side === 'front' ? 'Flip to back' : 'Flip to front';
        }
    }

    function flip() {
        const nextSide = side === 'front' ? 'back' : 'front';
        reloadWith(noteType, nextSide, testcaseSelect ? testcaseSelect.value : testcaseName);
    }

    if (noteTypeSelect) {
        noteTypeSelect.addEventListener('change', () => reloadWith(noteTypeSelect.value, side, testcaseSelect.value));
    }
    if (testcaseSelect) {
        testcaseSelect.addEventListener('change', () => reloadWith(noteType, side, testcaseSelect.value));
    }
    if (flipButton) {
        flipButton.addEventListener('click', flip);
    }

    // Space flips the card. Ignored while a form control has focus to preserve
    // dropdown keypress handling.
    document.addEventListener('keydown', event => {
        if (event.key !== ' ' && event.code !== 'Space') {
            return;
        }
        const active = document.activeElement;
        const isFormControl = active && /^(SELECT|BUTTON|INPUT|TEXTAREA)$/.test(active.tagName);
        if (isFormControl) {
            return;
        }
        event.preventDefault();
        flip();
    });

    // Surface errors in a banner
    window.addEventListener('error', event => {
        const status = document.getElementById('test-harness-status');
        if (status) {
            status.textContent = 'Error: ' + (event.message || String(event.error));
            status.hidden = false;
        }
    });

    //# sourceURL=src/inputs/test-harness.js
})();
