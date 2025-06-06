# Node.js base image for building the React app
FROM node:18-alpine as build

# Update build stage packages first (less critical but good practice)
RUN apk update && apk upgrade --no-cache

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app's source code
COPY frontend/ ./

# Build the app for production
RUN npm run build

# Nginx base image for serving the built React app
FROM nginx:stable-alpine

# Update packages in the final Nginx stage to patch vulnerabilities
# This is the critical step for fixing the reported CVEs
RUN apk update && apk upgrade --no-cache

# Copy the build output from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"] 