import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { FaFilm, FaStar, FaRobot } from 'react-icons/fa';
import './HomePage.css';

const HomePage = () => {
  const { user } = useAuth();

  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            <FaFilm /> Discover Your Next Favorite Movie
          </h1>
          <p className="hero-subtitle">
            Powered by Machine Learning & Big Data Analytics
          </p>
          <p className="hero-description">
            Get personalized movie recommendations based on your unique taste using
            collaborative filtering, ALS (Alternating Least Squares) algorithm, and Apache Spark technology
          </p>
          {user ? (
            <div className="hero-actions">
              <Link to="/movies" className="btn btn-primary btn-lg">
                Browse Movies
              </Link>
              <Link to="/recommendations" className="btn btn-secondary btn-lg">
                My Recommendations
              </Link>
            </div>
          ) : (
            <div className="hero-actions">
              <Link to="/register" className="btn btn-primary btn-lg">
                Get Started
              </Link>
              <Link to="/login" className="btn btn-secondary btn-lg">
                Login
              </Link>
            </div>
          )}
        </div>
      </section>

      <section className="features-section">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <FaStar />
              </div>
              <h3>Rate Movies</h3>
              <p>
                Rate movies you've watched to help our system understand your preferences
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <FaRobot />
              </div>
              <h3>ML Algorithm</h3>
              <p>
                Our ALS algorithm analyzes patterns across thousands of users to learn your taste
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <FaFilm />
              </div>
              <h3>Get Recommendations</h3>
              <p>
                Receive personalized movie suggestions tailored specifically for you
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-card">
              <h3>6,000+</h3>
              <p>Movies</p>
            </div>
            <div className="stat-card">
              <h3>100K+</h3>
              <p>Ratings</p>
            </div>
            <div className="stat-card">
              <h3>21K+</h3>
              <p>Active Users</p>
            </div>
            <div className="stat-card">
              <h3>{"< 1s"}</h3>
              <p>Response Time</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
