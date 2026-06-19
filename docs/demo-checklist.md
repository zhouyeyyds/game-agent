# Demo Checklist

1. `docker compose up -d mysql minio`
2. Run backend on `http://localhost:18000` and frontend on `http://localhost:5173`.
3. Run backend seed script.
4. Open Home and verify published games load from API.
5. Click a game and verify Play fetches remote manifest.
6. Show Runtime Info panel with manifest URL and storage prefix.
7. Login with `demo@example.com / password123`.
8. Open Create page and explain upcoming LangGraph generation flow.
9. Open MinIO console and verify `games/.../manifest.json` objects exist.
