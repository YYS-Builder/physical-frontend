import React from 'react';
import { useSelector } from 'react-redux';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import { RootState } from '../store';

const Home: React.FC = () => {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          pt: 8,
          pb: 6,
          textAlign: 'center',
        }}
      >
        <Typography
          component="h1"
          variant="h2"
          color="text.primary"
          gutterBottom
        >
          Welcome to Reader
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          A powerful document management and reading analytics platform.
          Organize your documents, track your reading progress, and gain insights
          into your reading habits.
        </Typography>
        <Box sx={{ mt: 4 }}>
          {!isAuthenticated ? (
            <Button
              component={RouterLink}
              to="/register"
              variant="contained"
              size="large"
              sx={{ mr: 2 }}
            >
              Get Started
            </Button>
          ) : (
            <Button
              component={RouterLink}
              to="/collections"
              variant="contained"
              size="large"
            >
              View Collections
            </Button>
          )}
        </Box>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" gutterBottom>
                Document Management
              </Typography>
              <Typography color="text.secondary">
                Organize your documents into collections, add tags, and easily
                find what you're looking for.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={RouterLink} to="/collections">
                Learn More
              </Button>
            </CardActions>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" gutterBottom>
                Reading Analytics
              </Typography>
              <Typography color="text.secondary">
                Track your reading progress, analyze your reading habits, and
                get insights into your reading patterns.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={RouterLink} to="/analytics">
                Learn More
              </Button>
            </CardActions>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" gutterBottom>
                AI Integration
              </Typography>
              <Typography color="text.secondary">
                Leverage AI to process and analyze your documents, extract
                key information, and get smart recommendations.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={RouterLink} to="/collections">
                Learn More
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Home; 