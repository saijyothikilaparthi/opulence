/* Opulence — site behaviour: mobile menu, work-gallery tiles, enquiry modal, API integration. */
(function () {
  'use strict';

  var API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port !== '8000'
    ? 'http://127.0.0.1:8000'
    : window.location.origin;

  /* ---------------- Mobile menu ---------------- */
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.menu-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    header.addEventListener('click', function (e) {
      if (e.target.closest('.site-nav a, .site-header__cta a')) closeMenu();
    });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', function (mq) {
      if (mq.matches) closeMenu();
    });
  }
  function closeMenu() {
    if (!header || !toggle) return;
    header.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open menu');
  }

  /* ---------------- Fetch Active Banner / Announcement ---------------- */
  function loadActiveBanner() {
    // Banner functionality removed as requested
  }
  loadActiveBanner();

  /* ---------------- Fetch Carousel Gallery ---------------- */
  function loadCarouselGallery() {
    var carouselViewport = document.getElementById('carouselViewport');
    if (!carouselViewport) return;

    fetch(API_BASE + '/api/gallery')
      .then(function (res) { return res.json(); })
      .then(function (json) {
        if (json.success && Array.isArray(json.data) && json.data.length > 0) {
          // Clear existing slides
          carouselViewport.innerHTML = '';
          
          // Add new slides
          json.data.forEach(function (item, idx) {
            var imgUrl = item.image_url.startsWith('http') ? item.image_url : (API_BASE + item.image_url);
            var slide = document.createElement('div');
            slide.className = 'hero-slide' + (idx === 0 ? ' active' : '');
            slide.setAttribute('data-index', idx);
            slide.setAttribute('data-title', item.title || 'Gift Hamper');
            slide.setAttribute('data-category', item.category || 'Bespoke Work');
            slide.setAttribute('data-desc', item.description || 'Custom Designed');
            slide.setAttribute('data-link', '#work');
            slide.setAttribute('aria-roledescription', 'slide');
            slide.setAttribute('aria-label', (idx + 1) + ' of ' + json.data.length);
            
            slide.innerHTML = 
              '<img src="' + imgUrl + '" alt="' + (item.title || 'Work photo') + '" class="w-full h-full object-cover object-center" draggable="false"/>' +
              '<div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/25 to-transparent"></div>';
            
            carouselViewport.appendChild(slide);
          });

          // Re-initialize carousel logic if needed (assuming it's handled elsewhere or needs to be triggered)
          // For now, just updating the DOM is sufficient if the carousel script handles dynamic content
        }
      })
      .catch(function (err) {
        console.log('Carousel fetch error:', err);
      });
  }
  loadCarouselGallery();
  function loadWorkGallery() {
    var gallery = document.querySelector('.gallery');
    if (!gallery) return;

    // Get category from data attribute if it exists
    var category = gallery.getAttribute('data-category');
    var url = API_BASE + '/api/gallery';
    if (category) {
      url += '?category=' + encodeURIComponent(category);
    }

    fetch(url)
      .then(function (res) { return res.json(); })
      .then(function (json) {
        if (json.success && Array.isArray(json.data) && json.data.length > 0) {
          var cols = gallery.querySelectorAll('.gallery__col');
          if (cols.length === 0) return;

          // Populate uploaded work items into gallery columns
          json.data.forEach(function (item, idx) {
            var colIndex = idx % cols.length;
            var imgUrl = item.image_url.startsWith('http') ? item.image_url : (API_BASE + item.image_url);
            
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'tile';
            btn.style.setProperty('--h', '380');
            btn.innerHTML = 
              '<img src="' + imgUrl + '" alt="' + (item.title || 'Work photo') + '" loading="lazy">' +
              '<span class="tile__overlay">' +
                '<span class="tile__cat">' + (item.category || 'Bespoke Work') + '</span>' +
                '<span class="tile__title">' + (item.title || 'Gift Hamper') + '</span>' +
                '<span class="tile__meta"><span>' + (item.description || 'Custom Designed') + '</span></span>' +
              '</span>';
            
            // Add click listener for touch devices
            btn.addEventListener('click', function () {
              var wasOpen = btn.classList.contains('is-open');
              document.querySelectorAll('.tile').forEach(function (t) { t.classList.remove('is-open'); });
              if (!wasOpen) btn.classList.add('is-open');
            });

            cols[colIndex].prepend(btn);
          });
        }
      })
      .catch(function (err) {
        console.log('Gallery fetch error:', err);
      });
  }
  loadWorkGallery();

  /* ---------------- Work gallery (tap to reveal on touch) ---------------- */
  var tiles = document.querySelectorAll('.tile');
  tiles.forEach(function (tile) {
    tile.addEventListener('click', function () {
      var wasOpen = tile.classList.contains('is-open');
      tiles.forEach(function (t) { t.classList.remove('is-open'); });
      if (!wasOpen) tile.classList.add('is-open');
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.tile')) document.querySelectorAll('.tile').forEach(function (t) { t.classList.remove('is-open'); });
  });

  /* ---------------- Enquiry modal ---------------- */
  var dialog = document.getElementById('enquire');
  if (!dialog || typeof dialog.showModal !== 'function') return;

  var form = dialog.querySelector('form');
  var success = dialog.querySelector('.enquiry__success');
  var successText = dialog.querySelector('[data-success-text]');
  var errorBox = dialog.querySelector('.enquiry__error');
  var submitBtn = form.querySelector('[type="submit"]');
  var typeSelect = form.querySelector('select[name="enquiry_type"]');
  var occasionInput = form.elements.occasion;
  var dateInput = form.elements.date;
  var lastTrigger = null;

  // Dynamic field toggling based on Gifting Type
  if (typeSelect) {
    typeSelect.addEventListener('change', updateFormFields);
  }

  function updateFormFields() {
    if (!typeSelect) return;
    var typeVal = typeSelect.value;
    var fCompany = form.querySelector('.fieldCompany, #fieldCompany');
    var fTheme = form.querySelector('.fieldTheme, #fieldTheme');
    var inputQty = form.querySelector('.inputQuantity, #inputQuantity');
    var helpQty = form.querySelector('.helpQuantity, #helpQuantity');
    var lblOccasion = form.querySelector('.labelOccasion, #labelOccasion');
    var inputCompany = form.querySelector('input[name="organisation"]');

    if (typeVal === 'corporate') {
      if (fCompany) fCompany.style.display = 'block';
      if (inputCompany) inputCompany.required = true;
      if (fTheme) fTheme.style.display = 'none';
      if (inputQty) {
        inputQty.min = '20';
        if (parseInt(inputQty.value) < 20) inputQty.value = '20';
      }
      if (helpQty) helpQty.style.display = 'block';
      if (lblOccasion) lblOccasion.textContent = 'Occasion / Event / Delegate Gifting';
    } else if (typeVal === 'customized') {
      if (fCompany) fCompany.style.display = 'none';
      if (inputCompany) inputCompany.required = false;
      if (fTheme) fTheme.style.display = 'block';
      if (inputQty) {
        inputQty.min = '20';
        if (parseInt(inputQty.value) < 20) inputQty.value = '20';
      }
      if (helpQty) helpQty.style.display = 'block';
      if (lblOccasion) lblOccasion.textContent = 'Occasion';
    } else {
      if (fCompany) fCompany.style.display = 'none';
      if (inputCompany) inputCompany.required = false;
      if (fTheme) fTheme.style.display = 'none';
      if (inputQty) {
        inputQty.min = '1';
        inputQty.value = '1';
      }
      if (helpQty) helpQty.style.display = 'none';
      if (lblOccasion) lblOccasion.textContent = 'Occasion';
    }
  }

  if (dateInput) dateInput.min = new Date().toISOString().slice(0, 10);

  function openEnquiry(trigger) {
    lastTrigger = trigger || null;
    closeMenu();
    resetForm();
    var preset = trigger && trigger.getAttribute('data-occasion');
    if (preset && occasionInput && !occasionInput.value) occasionInput.value = preset;
    updateFormFields();
    dialog.showModal();
    cleanedUp = false;
    document.body.classList.add('has-modal');
    var first = form.querySelector('input');
    if (first) first.focus();
  }

  function resetForm() {
    form.hidden = false;
    success.hidden = true;
    errorBox.hidden = true;
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit';
  }

  var cleanedUp = true;
  function cleanup() {
    if (cleanedUp) return;
    cleanedUp = true;
    document.body.classList.remove('has-modal');
    if (!success.hidden) form.reset();
    if (location.hash === '#enquire') history.replaceState(null, '', location.pathname + location.search);
    if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus();
  }
  function closeEnquiry() {
    if (dialog.open) dialog.close();
    cleanup();
  }
  dialog.addEventListener('close', cleanup);

  dialog.addEventListener('click', function (e) {
    if (e.target === dialog) closeEnquiry();
  });
  dialog.querySelectorAll('[data-close]').forEach(function (btn) {
    btn.addEventListener('click', closeEnquiry);
  });

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-enquire]');
    if (!trigger) return;
    e.preventDefault();
    openEnquiry(trigger);
  });

  if (location.hash === '#enquire') openEnquiry(null);

  /* Submit Enquiry to Backend REST API */
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    errorBox.hidden = true;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';

    var rawData = new FormData(form);
    
    // Parse quantity and budget into numbers
    var qty = parseInt(rawData.get('quantity')) || 1;
    var budgetVal = parseFloat((rawData.get('budget') || '').toString().replace(/[^0-9.]/g, '')) || null;
    var orgName = (rawData.get('organisation') || '').toString().trim();

    var payload = {
      enquiry_type: typeSelect ? typeSelect.value : (qty >= 20 ? 'corporate' : 'individual'),
      name: (rawData.get('name') || '').toString().trim(),
      phone: (rawData.get('phone') || '').toString().trim(),
      email: (rawData.get('email') || '').toString().trim() || null,
      company_name: orgName || null,
      occasion: (rawData.get('occasion') || '').toString().trim() || null,
      quantity: qty,
      budget: budgetVal,
      required_date: rawData.get('date') || null,
      theme: (rawData.get('theme') || '').toString().trim() || null,
      file_url: (rawData.get('file_url') || '').toString().trim() || null,
      personalize_hamper: (rawData.get('personalize_hamper') || '').toString().trim() || null,
      customization_details: "Designation: " + (rawData.get('designation') || '') + " | Loves: " + (rawData.get('loves') || '') + " | Note: " + (rawData.get('note') || '') + " | Delivery: " + (rawData.get('delivery') || '')
    };

    fetch(API_BASE + '/api/enquiries', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (json) {
        if (json.success) {
          showSuccess();
        } else {
          throw new Error(json.message || 'Submission error');
        }
      })
      .catch(function (err) {
        console.error('Enquiry submission error:', err);
        errorBox.hidden = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit';
      });
  });

  function showSuccess(text) {
    if (text) successText.textContent = text;
    form.hidden = true;
    success.hidden = false;
    var done = success.querySelector('[data-close]');
    if (done) done.focus();
  }
})();
