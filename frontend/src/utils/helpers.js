// Helper utility functions

export const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

export const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getGenreColor = (genre) => {
  const colors = {
    Action: '#ff6b6b',
    Comedy: '#ffd93d',
    Drama: '#6bcf7f',
    Horror: '#8b5cf6',
    Romance: '#f472b6',
    'Sci-Fi': '#06b6d4',
    Thriller: '#ef4444',
    default: '#6b7280'
  };
  return colors[genre] || colors.default;
};

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password) => {
  return password.length >= 6;
};
