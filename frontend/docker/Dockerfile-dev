
FROM node:23.11.0-slim

WORKDIR /app
COPY package.json package-lock.json .
RUN npm install
CMD ["npm", "run", "dev:docker"]

# Production stage
#FROM nginx:alpine
#COPY --from=builder /app/dist /usr/share/nginx/html
#EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]
