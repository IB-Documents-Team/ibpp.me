FROM python:3.8

WORKDIR /web

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Application entrypoint
CMD [ "python3", "app.py" ]