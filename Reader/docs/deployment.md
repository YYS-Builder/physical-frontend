# Deployment Guide

This guide provides instructions for deploying the Reader application using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Git

## Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/reader.git
   cd reader
   ```

2. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```

3. Update the environment variables in `.env`:
   - Set `JWT_SECRET` to a secure random string
   - Configure other environment variables as needed

## Deployment Steps

1. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

2. Verify the services are running:
   ```bash
   docker-compose ps
   ```

3. Check the logs:
   ```bash
   docker-compose logs -f
   ```

## Accessing the Application

- Frontend: http://localhost
- Backend API: http://localhost/api
- Database: localhost:5432
- Redis: localhost:6379

## Maintenance

### Updating the Application

1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Rebuild and restart the containers:
   ```bash
   docker-compose up -d --build
   ```

### Backup and Restore

1. Backup the database:
   ```bash
   docker-compose exec db pg_dump -U postgres reader > backup.sql
   ```

2. Restore the database:
   ```bash
   cat backup.sql | docker-compose exec -T db psql -U postgres reader
   ```

### Monitoring

- Use Docker's built-in monitoring:
  ```bash
  docker stats
  ```

- Check container logs:
  ```bash
  docker-compose logs -f [service_name]
  ```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Ensure no other services are using ports 80, 8000, 5432, or 6379
   - Modify port mappings in `docker-compose.yml` if needed

2. **Database Connection Issues**
   - Check if the database container is running
   - Verify database credentials in `.env`
   - Check database logs: `docker-compose logs db`

3. **Application Errors**
   - Check application logs: `docker-compose logs backend`
   - Verify environment variables
   - Ensure all required services are running

### Health Checks

1. Check backend health:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check frontend health:
   ```bash
   curl http://localhost
   ```

## Security Considerations

1. **Update Default Credentials**
   - Change default database credentials
   - Update JWT secret
   - Set strong passwords for all services

2. **Network Security**
   - Configure firewalls
   - Use HTTPS in production
   - Restrict access to management ports

3. **Regular Updates**
   - Keep Docker images updated
   - Apply security patches
   - Monitor for vulnerabilities

## Scaling

### Horizontal Scaling

1. Scale backend services:
   ```bash
   docker-compose up -d --scale backend=3
   ```

2. Configure load balancing (requires additional setup)

### Vertical Scaling

1. Adjust resource limits in `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

## Production Considerations

1. **Use a Reverse Proxy**
   - Configure Nginx or Traefik
   - Enable SSL/TLS
   - Set up proper caching

2. **Monitoring and Logging**
   - Set up centralized logging
   - Configure monitoring tools
   - Enable alerting

3. **Backup Strategy**
   - Regular database backups
   - Volume backups
   - Disaster recovery plan

4. **Security Hardening**
   - Regular security audits
   - Vulnerability scanning
   - Access control 