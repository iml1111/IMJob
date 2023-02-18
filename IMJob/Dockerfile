FROM python:3.10-alpine3.16 as base

COPY ./ /home/IMJob/
WORKDIR /home/IMJob/

RUN apk update && \
    apk add --update --no-cache alpine-sdk gcc libffi-dev && \
    pip install --upgrade pip && \
    pip wheel --wheel-dir=/home/IMJob/wheels -r requirements.txt

FROM python:3.10-alpine3.16

COPY --from=base /home/IMJob/ /home/IMJob/
WORKDIR /home/IMJob/

RUN apk update && \
	apk add --update --no-cache bash curl && \
	pip install --no-index --find-links=/home/IMJob/wheels -r requirements.txt && \
	rm -rf /home/IMJob/wheels && chmod +x /home/IMJob/main.py

CMD ["./main.py", "run", "Job:HelloWorld"]