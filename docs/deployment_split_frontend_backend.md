# Split Deployment: Frontend, Backend, and DigitalOcean MySQL

This project is now set up for separate deployment:

- Frontend: static React/Vite build on any web server.
- Backend: FastAPI API server on a backend server.
- Database: DigitalOcean Managed MySQL.

## Backend

Configure `backend/.env` on the backend server.

Use either a full database URL:

```env
DATABASE_URL=mysql+pymysql://doadmin:password@db-mysql-region-do-user-000000-0.b.db.ondigitalocean.com:25060/ai_hrms?charset=utf8mb4
```

Or individual values:

```env
MYSQL_USER=doadmin
MYSQL_PASSWORD=your_password
MYSQL_SERVER=db-mysql-region-do-user-000000-0.b.db.ondigitalocean.com
MYSQL_PORT=25060
MYSQL_DB=ai_hrms
MYSQL_SSL_CA=/path/to/ca-certificate.crt
```

Set CORS to the real frontend URL:

```env
BACKEND_PUBLIC_URL=https://api.yourdomain.com
FRONTEND_PUBLIC_URL=https://hrms.yourdomain.com
BACKEND_CORS_ORIGINS=["https://hrms.yourdomain.com"]
```

Run the backend API behind HTTPS and route all API traffic under:

```text
https://api.yourdomain.com/api/v1
```

Uploads are served from:

```text
https://api.yourdomain.com/uploads
```

## Frontend

Build once:

```bash
npm run build
```

Deploy `frontend/dist` to the frontend server. Then edit this deployed file:

```text
app-config.js
```

For split frontend/backend servers:

```js
window.__AI_HRMS_CONFIG__ = {
  apiBaseUrl: "https://api.yourdomain.com/api/v1",
  uploadsBaseUrl: "https://api.yourdomain.com",
};
```

For same-origin deployments with a reverse proxy:

```js
window.__AI_HRMS_CONFIG__ = {
  apiBaseUrl: "",
  uploadsBaseUrl: "",
};
```

In same-origin mode, proxy these paths from the frontend domain to the backend:

```text
/api/*     -> backend server
/uploads/* -> backend server
```

## Local Development

Frontend dev proxy defaults to `http://localhost:8001`. Override it in `frontend/.env`:

```env
VITE_DEV_API_PROXY_TARGET=http://localhost:8001
```
