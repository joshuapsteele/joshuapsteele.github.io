FROM python:3.13-slim
WORKDIR /app
COPY app.py index.html app.js style.css ./
RUN mkdir /data && chown 10001:10001 /data
USER 10001:10001
ENV PYTHONUNBUFFERED=1 RECYCLER_DB=/data/recycler.sqlite3
EXPOSE 8787
CMD ["python", "app.py", "serve", "--host", "0.0.0.0"]
