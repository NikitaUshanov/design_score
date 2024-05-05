# Install python image in container
FROM python:3.7

RUN apt-get update && \
    apt-get -y install netcat-openbsd && \
    apt-get -y install netcat-traditional && \
    apt-get clean && \
    apt-get install -y python3-opencv

RUN apt-get update && apt-get install -y wget gnupg2 software-properties-common

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

RUN CHROME_VERSION=$(google-chrome --version | cut -f 3 -d ' ' | cut -d '.' -f 1) \
    && CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
    && wget -q --continue -P /chromedriver "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" \
    && unzip /chromedriver/chromedriver* -d /usr/local/bin/

# Установка дополнительных зависимостей для работы Selenium
RUN apt-get install -yqq unzip \
    && apt-get clean

# Create and set the working directory
RUN mkdir -p /app/backend
WORKDIR /app/backend

# Copy the requirements to the container
COPY requirements.txt /app/backend/

# Install dependencies
RUN pip3 install -r ./requirements.txt

# Copy the server files to the container
COPY . /app/backend/

WORKDIR /app/backend/src

CMD [ "python", "-u", "app.py"]
