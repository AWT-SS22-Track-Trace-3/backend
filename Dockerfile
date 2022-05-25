FROM node:18.2

EXPOSE 8080

WORKDIR /app

COPY package*.json ./

RUN yarn

COPY . .

CMD ["node", "server.js"]
