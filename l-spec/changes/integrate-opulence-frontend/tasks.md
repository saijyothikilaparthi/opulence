## 1. Directory Setup & File Cleanup

- [x] 1.1 Move `Opulence/frontend` to `/home/sai_jyothi/gift-backend/frontend` and `Opulence/README.md` to `/home/sai_jyothi/gift-backend/README.md`.
- [x] 1.2 Delete directory `Opulence/`.
- [x] 1.3 Remove sample demo files (`demo/customer.html`, `demo/enquiry.html`, `demo/individual.html`, `demo/corporate.html`, `demo/customized.html`) keeping `demo/admin.html`.

## 2. FastAPI Mount & JS API Wiring

- [x] 2.1 Mount `frontend/` static files in `app/main.py` at `/` or `/site`.
- [x] 2.2 Update `frontend/js/main.js` to connect enquiry modal to `POST /api/enquiries`.
- [x] 2.3 Update `frontend/js/main.js` to fetch and render active seasonal banner (`GET /api/banners/active`) in `index.html`.
- [x] 2.4 Update `frontend/js/main.js` to fetch and render gallery work photos (`GET /api/gallery`) in `index.html`.
