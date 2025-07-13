FROM nginx:alpine

RUN mkdir /etc/nginx/templates
COPY ./templates/nginx.conf.template /etc/nginx/templates
RUN envsubst < /etc/nginx/templates/nginx.conf.template > /etc/nginx/conf.d/nginx.conf
CMD ["nginx", "-g", "daemon off;"]