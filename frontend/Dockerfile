# Frontend Dockerfile
FROM node:20

# Set the working directory
WORKDIR /frontend

# Copy the package.json and yarn.lock
COPY ./package.json ./
COPY ./yarn.lock ./

# Install Yarn and dependencies
RUN yarn install

# Copy the rest of the frontend code
COPY . .

# Expose the port the frontend runs on
EXPOSE 5173

RUN groupadd -g 1001 frontend \
    && useradd -u 1001 -g frontend -s /bin/bash -m frontend \
    && chown -R frontend:frontend /frontend \
    && chmod -R 777 /frontend

# Command to start the frontend
CMD ["yarn", "dev"]
