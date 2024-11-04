FROM python:3.12-bookworm AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN /opt/venv/bin/python -m pip install --upgrade pip
COPY ./requirements-prod.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.12-bookworm

RUN useradd -d /home/user -m -u 1000 user
USER user
WORKDIR /home/user

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /home/user

ENTRYPOINT ["./start.sh"]