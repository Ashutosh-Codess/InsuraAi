# InsuraAI

AI Powered Insurance Management Platform

## Run locally

Start the API before opening the frontend (both portals use it for sign-in):

```powershell
.\start-backend.ps1
```

Then serve the `frontend` folder (for example with Live Server) and open the
customer or agent portal. The local demo accounts are:

- `customer@insuramind.local` / `password123`
- `agent@insuramind.local` / `password123`

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- OpenCV
- AI Modules
- Docker
