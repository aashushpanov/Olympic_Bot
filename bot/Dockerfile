FROM nickgryg/alpine-pandas

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 12000:12000

CMD [ "python", "./bot.py" ]