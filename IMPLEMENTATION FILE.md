You are an expert full-stack html/flask developer.  
Your ONLY job right now is to REBUILD my webapp from the current codebase so it is 100% functional, beautiful, and production-ready.

BEFORE YOU WRITE A SINGLE LINE OF CODE, DO THESE 3 THINGS:
1. Open and read the entire README.md — understand the app’s purpose, target users, and core value proposition.
2. Open server.py — map every Flask route, every SQLAlchemy model, and every database table.
3. Open the frontend folder — note every html page, and CSS file that already exists.

NOW FOLLOW THESE 5 INSTRUCTIONS EXACTLY (in order):

1. AUTHENTICATION & DASHBOARD
   - Guarantee /signup and /signin pages are pixel-perfect, mobile-responsive, and use Flask API endpoints (NO JavaScript backend calls).
   - Build a protected Dashboard with a collapsible sidebar containing these menu items (add icons):
        • Home        • Projects      • Users
        • Files       • Analytics     • Settings
        • Logout
   - Use the same color palette and typography as popular SaaS apps (Tailwind + Heroicons is perfect).

2. REPLACE EVERY JAVASCRIPT BACKEND CALL
   - Search the entire frontend for fetch/axios calls that hit Supabase, Firebase, or any non-local backend.
   - DELETE them.
   - Replace 1-to-1 with calls to the existing Flask routes in server.py (e.g., POST /api/login, GET /api/projects).
   - Add proper error handling and loading spinners.

3. CREATIVE ENHANCEMENTS
   - Add any missing pages/files the README implies (e.g., “Create Project” modal, file uploader, dark mode toggle).
   - Create a global CSS file (src/index.css) with reusable Tailwind @apply classes.
   - Add a toast notification system (react-hot-toast or similar).
   - Make the UI feel instantly familiar — copy the layout rhythm of Notion, Linear, or Vercel.

4. DATABASE INTEGRITY
   - Run the existing migrations (if any) or create db.init() in server.py.
   - Write a quick sanity-check script (print all tables + 3 sample rows) and run it.
   - Fix any foreign-key, unique-constraint, or nullable errors you find.

5. FINAL POLISH & HAND-OFF
   - Run the app locally (flask run + npm run dev) and take 3 screenshots: Login, Dashboard, one feature page.
   - Create a new file QUICK_START.md with exact terminal commands to start backend + frontend.

WHEN YOU ARE 100% DONE:
- Paste the FULL updated file tree.
- Paste ONLY the files you changed/added (diff style).
- Ask me EXACTLY 3 questions so you can make it even better (e.g., “Do you want file uploads stored on disk or S3?”).

Start NOW. No confirmations, no chit-chat — just execute.