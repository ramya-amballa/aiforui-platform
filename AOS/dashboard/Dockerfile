# Build from the repository root, not this directory, so the image can
# see the whole AOS/ tree the dashboard invokes as subprocesses:
#
#   docker build -f AOS/dashboard/Dockerfile -t aos-command-center .
#   docker run -p 8501:8501 aos-command-center
#
# AOS_ROOT is set explicitly so utils/paths.py resolves runtime scripts
# and output files correctly regardless of where the image places AOS/.

FROM python:3.11-slim

WORKDIR /app

COPY AOS/dashboard/requirements.txt ./dashboard-requirements.txt
RUN pip install --no-cache-dir -r dashboard-requirements.txt

COPY AOS/ ./AOS/

ENV AOS_ROOT=/app/AOS
ENV PYTHONUNBUFFERED=1

WORKDIR /app/AOS/dashboard

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
