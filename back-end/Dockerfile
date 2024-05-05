# Install python image in container
FROM python:3.7

RUN apt-get update && \
    apt-get -y install netcat-openbsd && \
    apt-get -y install netcat-traditional && \
    apt-get clean && \
    apt-get install -y python3-opencv

RUN apt-get install -y wget xvfb unzip

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable

# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_VERSION 2.19
ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR

# Download and install Chromedriver
RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

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
