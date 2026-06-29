# syntax=docker/dockerfile:1

# ---- Build stage: render VitePress static site ----
FROM node:22-slim AS build
WORKDIR /app

# git is required by VitePress for lastUpdated timestamps; corepack enables pnpm
RUN apt-get update && apt-get install -y --no-install-recommends git \
  && rm -rf /var/lib/apt/lists/* \
  && corepack enable

# Install deps (cached on lockfile)
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY docs/package.json docs/package.json
COPY exercises/package.json exercises/package.json
RUN pnpm install --frozen-lockfile

# Build the docs site
COPY . .
RUN NODE_OPTIONS=--max-old-space-size=4096 pnpm build

# ---- Runtime stage: serve with nginx ----
FROM nginx:1.27-alpine AS runtime

# Static output served under the /battle-tested-patterns/ base path
COPY --from=build /app/docs/.vitepress/dist /usr/share/nginx/html/battle-tested-patterns
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost/battle-tested-patterns/ >/dev/null 2>&1 || exit 1
