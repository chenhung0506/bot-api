FROM python:3.7-alpine
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD ./module /usr/src/app
# EXPOSE 3000
RUN apk add bash
RUN apk add curl
RUN apk add -U tzdata
RUN echo "Asia/Taipei" > /etc/timezone
RUN ls /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt
HEALTHCHECK --interval=5s --timeout=5s --retries=5 CMD curl -f "http://localhost:${PORT}/healthcheck" || exit 1 
CMD ["python", "server.py"]