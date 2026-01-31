# k8s image volume vs multi-stage build sample

Sample NestJS + TypeScript app (ESLint, Prettier) to compare CI build time between:

1. **Multi-stage build**: single image built with `Dockerfile.multistage`
2. **Image volume**: runtime = `node:20-alpine`, script = separate image with `dist/` only, mounted as volume

## Local verification

```bash
# Build multi-stage image
docker build -f Dockerfile.multistage -t k8s-image-volume-sample:multistage .
docker run --rm -p 3000:3000 k8s-image-volume-sample:multistage
# curl http://localhost:3000/
```

## Image volume (Kubernetes)

Requires Kubernetes 1.31+ with ImageVolume feature. Build and push the script image, then:

```bash
kubectl apply -f pod-image-volume.yaml
```
