FROM node:18.2

EXPOSE 8080

WORKDIR /app

COPY package.json ./
COPY yarn.lock ./

RUN yarn

COPY ./code .
COPY . .

CMD ["node", "server.js"]
