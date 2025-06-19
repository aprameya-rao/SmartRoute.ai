// services/evApi.js
const API_BASE_URL = 'http://localhost:8000';

export const optimizeEvRoute = async (formData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/optimize-route`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    // Check if response is ok
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
    
  } catch (error) {
    console.error('API Error:', error);
    
    // Re-throw with more context
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the backend server. Please ensure the server is running.');
    }
    
    throw error;
  }
};