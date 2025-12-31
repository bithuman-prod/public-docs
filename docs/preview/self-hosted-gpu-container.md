# Self-Hosted GPU Avatar Container

> **Preview Feature: Deploy GPU Avatar Workers on Your Infrastructure**
> Run production-grade GPU avatar generation on your own cloud infrastructure with full control over scaling, costs, and data privacy.
>
> **Pricing**: 2 credits per minute while using the GPU container.

## Overview

The self-hosted GPU avatar container (`docker.io/bithumanhubs/gpu-avatar-worker:latest`) enables you to deploy production-grade avatar generation on your own GPU infrastructure. This provides:

- **Full Control**: Complete control over deployment, scaling, and configuration
- **Cost Optimization**: Pay only for the GPU resources you use
- **Data Privacy**: Avatar images and audio never leave your infrastructure
- **Customization**: Extend the worker with custom logic and integrations

### Features

- **Real-time Avatar Generation**: Generate expressive talking avatars from single reference images
- **Natural Speech Synthesis**: Synchronized lip-sync and facial expressions driven by audio input
- **Emotion Recognition**: Automatic emotion detection from speech with 7 basic emotions supported
- **Smooth Motion**: Fluid, natural-looking animations optimized for real-time streaming
- **WebRTC Streaming**: Direct video streaming to browsers with low latency

## Quick Start

### Pull and Run

```bash
# Pull the latest image
docker pull docker.io/bithumanhubs/gpu-avatar-worker:latest

# Run with GPU support
docker run --gpus all -p 8089:8089 \
    -v /path/to/model-storage:/persistent-storage/avatar-model \
    -e AVATAR_MODEL_DIR=/persistent-storage/avatar-model \
    docker.io/bithumanhubs/gpu-avatar-worker:latest
```

### Verify Deployment

```bash
# Health check
curl http://localhost:8089/health

# Should return: {"status": "ok", "active_workers": 0}
```

## Container Architecture

### Components

The container includes:

- **Avatar Generation Engine**: High-quality talking avatar generation from reference images
- **Audio Processing Pipeline**: Audio feature extraction and emotion recognition
- **WebRTC Streaming Framework**: Real-time video streaming to browsers
- **HTTP API Server**: RESTful API for worker management and requests
- **Preset Avatar Cache**: Optional pre-encoded avatar storage for fast startup

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/launch` | POST | Launch a new avatar worker |
| `/health` | GET | Health check status |
| `/ready` | GET | Readiness check |

## Performance Characteristics

### Startup Behavior

The container exhibits different startup times depending on configuration:

| Configuration | Time to First Frame | Description |
|---------------|---------------------|-------------|
| **Long-running + PRESET_AVATARS_DIR** | ~4 seconds | Avatar images pre-processed, minimal GPU initialization |
| **Long-running + No Cache** | ~6 seconds | Avatar processing on first request, GPU initialization |
| **Cold Start** | ~30-40 seconds | Full avatar engine initialization |

### Long-Running Containers

**Recommended for production deployments.** Containers stay running and handle multiple requests.

**With PRESET_AVATARS_DIR configured:**
- Avatar engine initialized at startup (~30s one-time)
- Avatar images pre-processed for instant loading
- First frame in ~4 seconds for preset avatars
- Subsequent frames at ~25 FPS

**Without PRESET_AVATARS_DIR:**
- Avatar engine initialized at startup (~30s one-time)
- Avatar processing on first request (~2s overhead)
- First frame in ~6 seconds
- Subsequent requests use in-memory cache

### Cold Start Containers

**Recommended for cost-optimized deployments.** Each request gets a fresh container.

**Characteristics:**
- Container starts from scratch (~30s initialization time)
- Container handles one request then terminates
- No persistent state between requests
- Higher latency per request, lower idle costs

## PRESET_AVATARS_DIR Configuration

### Directory Structure

The preset avatar directory stores avatar images for instant loading:

```
/persistent-storage/preset-avatars/
├── avatar_001/
│   └── face.jpg          # Image file (avatar_001 is the avatar_id)
├── avatar_002/
│   └── portrait.png      # Image file (avatar_002 is the avatar_id)
└── avatar_003/
    └── avatar.webp       # Image file (avatar_003 is the avatar_id)
```

**Key points:**
- Each subdirectory name becomes the `avatar_id` for that avatar
- Each subdirectory contains one image file (.jpg, .jpeg, .png, or .webp)
- The system automatically finds and uses the first image file in each directory
- Image features are pre-encoded and cached in memory at container startup

### Supported Image Formats

- `.jpg` / `.jpeg` - JPEG format (recommended)
- `.png` - PNG format
- `.webp` - WebP format

### Mounting Preset Directory

```bash
docker run --gpus all -p 8089:8089 \
    -v /path/to/model-storage:/persistent-storage/avatar-model \
    -v /path/to/preset-avatars:/persistent-storage/preset-avatars \
    -e AVATAR_MODEL_DIR=/persistent-storage/avatar-model \
    -e PRESET_AVATARS_DIR=/persistent-storage/preset-avatars \
    docker.io/bithumanhubs/gpu-avatar-worker:latest
```

### Using Preset Avatars

Preset avatars are automatically pre-processed at container startup for instant loading.

**To set up preset avatars:**

1. **Organize avatar images** in the preset directory structure:
   ```
   /persistent-storage/preset-avatars/
   ├── avatar_001/
   │   └── face.jpg
   ├── avatar_002/
   │   └── portrait.png
   └── avatar_003/
       └── avatar.webp
   ```

2. **Mount the directory** when starting the container:
   ```bash
   -v /path/to/preset-avatars:/persistent-storage/preset-avatars \
   -e PRESET_AVATARS_DIR=/persistent-storage/preset-avatars
   ```

3. **Use avatar IDs** in your requests:
   - Specify `avatar_id: "avatar_001"` to use that preset avatar
   - The container will load the pre-encoded features instantly

**Benefits of preset avatars:**
- ~4s startup time vs ~6s for on-demand encoding
- Consistent performance across requests
- Reduced GPU utilization during runtime
- Ideal for frequently used avatar designs

**Image requirements:**
- High-quality portrait images (512x512 recommended)
- Front-facing photos with visible faces
- Good lighting and neutral expression
- File size under 10MB for optimal performance

## Cloud Deployment Guides

### AWS ECS with Fargate

AWS ECS (Elastic Container Service) with Fargate provides serverless GPU container hosting with automatic scaling.

#### Prerequisites

- AWS Account with ECS and EC2 access
- NVIDIA GPU-enabled EC2 capacity (for Fargate with GPU)
- Application Load Balancer (for public access)

#### Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "gpu-avatar-worker",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "8192",
  "memory": "16384",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "gpu-avatar-worker",
      "image": "docker.io/bithumanhubs/gpu-avatar-worker:latest",
      "cpu": 8192,
      "memory": 15360,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8089,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AVATAR_MODEL_DIR",
          "value": "/persistent-storage/avatar-model"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "model-storage",
          "containerPath": "/persistent-storage/avatar-model",
          "readOnly": true
        },
        {
          "sourceVolume": "preset-avatars",
          "containerPath": "/persistent-storage/preset-avatars",
          "readOnly": true
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/gpu-avatar-worker",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      },
      "resourceRequirements": [
        {
          "type": "GPU",
          "value": "1"
        }
      ],
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8089/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 120
      }
    }
  ],
  "volumes": [
    {
      "name": "model-storage",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-xxxxxxxx",
        "rootDirectory": "/avatar-model"
      }
    },
    {
      "name": "preset-avatars",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-xxxxxxxx",
        "rootDirectory": "/preset-avatars"
      }
    }
  ]
}
```

#### Scaling Strategy

**For Long-Running Containers (Recommended for Production):**

```json
{
  "name": "gpu-avatar-worker-scaling",
  "policyType": "TargetTrackingScaling",
  "targetTrackingScalingPolicyConfiguration": {
    "targetValue": 70.0,
    "predefinedMetricSpecification": {
      "predefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "scaleOutCooldown": 300,
    "scaleInCooldown": 300,
    "disableScaleIn": false
  },
  "minCapacity": 1,
  "maxCapacity": 10
}
```

**For Cold Start Containers (Cost-Optimized):**

```json
{
  "name": "gpu-avatar-worker-scaling",
  "policyType": "StepScaling",
  "stepScalingPolicyConfiguration": {
    "adjustmentType": "ChangeInCapacity",
    "stepAdjustments": [
      {
        "scalingAdjustment": 1,
        "metricIntervalLowerBound": 0,
        "metricIntervalUpperBound": 5
      }
    ],
    "cooldown": 60
  },
  "minCapacity": 0,
  "maxCapacity": 30
}
```

#### Recommended GPU Types

| GPU Type | vCPU | Memory | Use Case | Hourly Cost (us-east-1) |
|----------|------|--------|----------|--------------------------|
| **g4dn.xlarge** | 4 | 16 GB | Development, testing | ~$0.53 |
| **g4dn.2xlarge** | 8 | 32 GB | Low-traffic production | ~$0.75 |
| **g5.xlarge** | 4 | 16 GB | Production (Ampere) | ~$1.01 |
| **g5.2xlarge** | 8 | 32 GB | High-traffic production | ~$1.51 |
| **g5.4xlarge** | 16 | 64 GB | High-concurrency | ~$2.20 |
| **p3.2xlarge** | 8 | 61 GB | Maximum performance | ~$3.82 |

**Recommendation:** Use `g5.xlarge` for production. It provides an NVIDIA A10G GPU with excellent performance/cost ratio.

#### Deploy Task

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
    --cluster gpu-avatar-cluster \
    --service-name gpu-avatar-worker \
    --task-definition gpu-avatar-worker \
    --desired-count 1 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
    --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:region:account-id:targetgroup/name,id,containerName=gpu-avatar-worker,containerPort=8089

# Configure auto scaling
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/gpu-avatar-cluster/gpu-avatar-worker \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 1 \
    --max-capacity 10

aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/gpu-avatar-cluster/gpu-avatar-worker \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name gpu-avatar-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### AWS Lambda with Container Image (Cold Start Strategy)

For true serverless scaling, use AWS Lambda with container image support.

**Limitations:**
- Maximum 15 minutes execution time
- No GPU support currently (CPU only for non-GPU workloads)
- 10 GB container image size limit

**Note:** GPU avatar generation requires GPU support, so Lambda is not recommended for this workload.

### Alternative Cloud Platforms

#### Google Cloud Run (GPU)

```yaml
# cloud-run-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: gpu-avatar-worker
spec:
  template:
    spec:
      containers:
      - image: docker.io/bithumanhubs/gpu-avatar-worker:latest
        ports:
        - containerPort: 8089
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            cpu: "8"
            memory: "12Gi"
        env:
        - name: AVATAR_MODEL_DIR
          value: "/persistent-storage/avatar-model"
        volumeMounts:
        - name: model-storage
          mountPath: /persistent-storage/avatar-model
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-storage-pvc
```

**Scaling:**

```bash
# Deploy with minimum instances (for long-running)
gcloud run deploy gpu-avatar-worker \
    --image docker.io/bithumanhubs/gpu-avatar-worker:latest \
    --platform managed \
    --region us-central1 \
    --cpu 8 \
    --memory 12Gi \
    --accelerator nvidia.com/gpu=1 \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 3600

# Or scale to zero (for cold start)
gcloud run deploy gpu-avatar-worker \
    --min-instances 0 \
    --max-instances 100
```

#### Azure Container Instances

```bash
az container create \
    --resource-group gpu-avatar-rg \
    --name gpu-avatar-worker \
    --image docker.io/bithumanhubs/gpu-avatar-worker:latest \
    --cpu 8 \
    --memory 12 \
    --gpu-count 1 \
    --gpu-sku K80 \
    --ports 8089 \
    --environment-variables \
        AVATAR_MODEL_DIR=/persistent-storage/avatar-model \
    --azure-file-volume-account-name mystorageaccount \
    --azure-file-volume-share-name model-storage \
    --azure-file-volume-mount-path /persistent-storage/avatar-model
```

## Troubleshooting

### Container won't start

**Symptom:** Container exits immediately

**Solutions:**
1. Check GPU availability: `nvidia-smi`
2. Verify storage volume mount
3. Check logs: `docker logs <container-id>`

### High first frame latency

**Symptom:** First frame takes >10 seconds

**Solutions:**
1. Configure PRESET_AVATARS_DIR for pre-processed avatars
2. Use long-running containers instead of cold start
3. Increase GPU memory allocation
4. Check avatar engine initialization in logs

### Out of memory errors

**Symptom:** GPU out of memory errors

**Solutions:**
1. Increase container memory limit
2. Reduce audio buffer configuration
3. Use larger GPU instance
4. Limit concurrent requests per container

### Slow encoding performance

**Symptom:** Avatar processing takes >2 seconds

**Solutions:**
1. Pre-process avatars into PRESET_AVATARS_DIR
2. Use GPU with more compute cores
3. Optimize image size before upload
4. Check GPU utilization with `nvidia-smi`

## Next Steps

- **Integration Guide**: See [Custom GPU Endpoint Integration](https://github.com/bithuman-prod/public-docs/tree/main/examples/cloud/expression#%EF%B8%8F-example-3-custom-gpu-endpoint)
- **LiveKit Plugins**: Install required `livekit-plugins-bithuman` package
- **Monitoring**: Set up CloudWatch dashboards and alerts
- **Scaling**: Configure auto-scaling policies based on traffic patterns

## Additional Resources

- [Docker Hub Image](https://hub.docker.com/r/bithumanhubs/gpu-avatar-worker)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [AWS ECS GPU Documentation](https://docs.aws.amazon.com/ecs/latest/userguide/task_definition_parameters.html)
- [GPU Instance Pricing](https://aws.amazon.com/ec2/instance-types/)

## Changelog

### Version 1.0.0 (Latest)
- Initial public release
- Real-time avatar generation from single images
- Preset avatar caching for fast startup
- WebRTC streaming support
- Multi-cloud deployment support (AWS, GCP, Azure)
