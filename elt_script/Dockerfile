FROM python:3.8-slim

# Install PostgreSQL command-line tools
RUN apt-get update && apt-get install -y postgresql-client cron curl unzip gnupg && rm -rf /var/lib/apt/lists/*
RUN pip install selenium
RUN pip install pandas

# Set working directory
WORKDIR /opt/airflow/elt_script

# Copy the script into the container
COPY scraper.py /opt/airflow/elt_script/

RUN chmod +x scraper.py

RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
   mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
   curl -sS -o /tmp/chromedriver_linux64.zip https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.76/linux64/chromedriver-linux64.zip && \
   unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
   rm /tmp/chromedriver_linux64.zip && \
   chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver-linux64/chromedriver && \
   ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
# RUN CHROMEDRIVER_VERSION=125.0.6422.60 && \
#    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
#    curl -sS -o /tmp/chromedriver_linux64.zip https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chrome-linux64.zip && \
#    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
#    rm /tmp/chromedriver_linux64.zip && \
#    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
#    ls -l /opt/chromedriver-$CHROMEDRIVER_VERSION && \ 
#    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver && \
#    ls -l /usr/local/bin/chromedriver               

# Install Google Chrome
# RUN curl -sS -o – https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add – && \
#    echo “deb http://dl.google.com/linux/chrome/deb/ stable main” >> /etc/apt/sources.list.d/google-chrome.list && \
#    apt-get -yqq update && \
#    apt-get -yqq install google-chrome-stable && \
#    rm -rf /var/lib/apt/lists/*
# Install Google Chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -yqq update && \
    apt-get -yqq install google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# RUN apt-get update && apt-get install -y \
#   unzip \
#   curl \
#   gnupg \
#   && rm -rf /var/lib/apt/lists/*
 

RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add

RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

RUN apt-get -y update

RUN apt-get install -y google-chrome-stable


# # Copy the wrapper script and the ELT script
# COPY start.sh /app/start.sh
# COPY scraper.py .

# # Set the working directory
# WORKDIR /app

# # Add the cron job
# # This example runs the script every day at 3am.
# # Adjust the cron timing as needed.
# RUN echo "0 12 * * * python /app/scraper.py" | crontab -


# Set the default command to run the ELT script
# CMD ["python", "scraper.py"]