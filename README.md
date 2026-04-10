# InstaSaver

InstaSaver is a modern full-stack web app for downloading Instagram Reels and Posts through two separate workflows.

## Stack

- Frontend: React (Vite), Tailwind CSS, Axios, React Router, React Hot Toast
- Backend: FastAPI, yt-dlp

## Features

- Separate Reel and Post tools
- URL/input validation before API request
- Preview before download
- Post gallery with per-item downloads
- Loading spinner and progress feedback
- Toast notifications for success/error
- Download history persisted in localStorage
- Basic per-IP rate limiting on API
- Responsive dark-themed UI with subtle gradients

## Project Structure

```txt
instasever/
  backend/
    app/
      core/
      routers/
      schemas/
      services/
      main.py
    requirements.txt
    .env.example
  frontend/
    public/
    src/
      components/
      pages/
      services/
      utils/
    package.json
    .env.example
```

## Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

API base URL: `http://localhost:8000`

### Endpoints

- `POST /api/download/reel`
- `POST /api/download/post`
- `GET /api/download/file?url=<media_url>&filename=<name>`

Request samples:

```json
{ "url": "https://www.instagram.com/reel/xxxx/" }
```

```json
{ "url": "https://www.instagram.com/p/xxxx/" }
```

## Frontend Setup (Vite + Tailwind)

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend default URL: `http://localhost:5173`


## Notes

- Private or unavailable Instagram content returns user-friendly error messages.
- Downloading private or restricted posts/reels may require authentication.
- This app streams direct media links from yt-dlp extraction and does not host Instagram media.
