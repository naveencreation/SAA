# Frontend Dockerfile
# Next.js (build + runtime)
FROM node:22.22.0-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM node:22.22.0-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# copy standalone output
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
