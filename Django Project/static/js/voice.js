/**
 * voice.js — Web Speech API voice-to-text
 * Supports: English, isiZulu, Sesotho, Afrikaans
 * Fills #description-field with transcribed text.
 */
(function () {
  'use strict';

  const LANGUAGES = [
    { code: 'en-ZA', label: 'English' },
    { code: 'zu-ZA', label: 'isiZulu' },
    { code: 'st-ZA', label: 'Sesotho' },
    { code: 'af-ZA', label: 'Afrikaans' },
  ];

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  function init() {
    const voiceBtn = document.getElementById('voice-btn');
    const voiceIcon = document.getElementById('voice-icon');
    const voiceLabel = document.getElementById('voice-label');
    const voiceStatus = document.getElementById('voice-status');
    const textarea = document.getElementById('description-field');

    if (!voiceBtn || !textarea) return;

    if (!SpeechRecognition) {
      voiceBtn.style.display = 'none';
      return;
    }

    let recognition = null;
    let isRecording = false;
    let currentLang = LANGUAGES[0];

    // Add language picker
    const langSelect = document.createElement('select');
    langSelect.className = 'voice-lang-select';
    langSelect.setAttribute('aria-label', 'Voice language');
    LANGUAGES.forEach(lang => {
      const opt = document.createElement('option');
      opt.value = lang.code;
      opt.textContent = lang.label;
      langSelect.appendChild(opt);
    });
    voiceBtn.parentNode.insertBefore(langSelect, voiceBtn.nextSibling);
    langSelect.addEventListener('change', () => {
      currentLang = LANGUAGES.find(l => l.code === langSelect.value) || LANGUAGES[0];
    });

    function startRecording() {
      recognition = new SpeechRecognition();
      recognition.lang = currentLang.code;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.continuous = false;

      isRecording = true;
      voiceBtn.classList.add('recording');
      voiceIcon.textContent = '🔴';
      voiceLabel.textContent = 'Listening… tap to stop';
      if (voiceStatus) { voiceStatus.textContent = ''; voiceStatus.hidden = false; }

      let finalTranscript = '';

      recognition.onresult = (e) => {
        let interim = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
          const t = e.results[i][0].transcript;
          if (e.results[i].isFinal) finalTranscript += t;
          else interim += t;
        }
        if (voiceStatus) voiceStatus.textContent = interim || finalTranscript;
      };

      recognition.onend = () => {
        isRecording = false;
        voiceBtn.classList.remove('recording');
        voiceIcon.textContent = '🎤';
        voiceLabel.textContent = 'Speak your description';

        if (finalTranscript) {
          const current = textarea.value.trim();
          textarea.value = current ? current + ' ' + finalTranscript : finalTranscript;
          textarea.dispatchEvent(new Event('input'));
          if (voiceStatus) voiceStatus.textContent = '✓ Added to description';
        } else {
          if (voiceStatus) voiceStatus.textContent = 'No speech detected. Try again.';
        }
      };

      recognition.onerror = (e) => {
        let msg = 'Could not record. ';
        if (e.error === 'not-allowed') msg += 'Please allow microphone access.';
        else if (e.error === 'no-speech') msg += 'No speech detected.';
        else msg += e.error;
        if (voiceStatus) voiceStatus.textContent = msg;
        isRecording = false;
        voiceBtn.classList.remove('recording');
        voiceIcon.textContent = '🎤';
        voiceLabel.textContent = 'Speak your description';
      };

      recognition.start();
    }

    function stopRecording() {
      if (recognition) recognition.stop();
    }

    voiceBtn.addEventListener('click', () => {
      if (isRecording) stopRecording();
      else startRecording();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
