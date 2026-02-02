/**
 * Real-World React Application
 * Simulates actual React code a user might write
 *
 * Expected features: arrow-functions, async-functions, const, let,
 * template-literals, es6, promises, fetch, abortcontroller,
 * queryselector, classlist, namevalue-storage, json, es5
 */

import React, { useState, useEffect, useCallback } from 'react';

// Custom hook for data fetching
const useFetch = (url) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        const fetchData = async () => {
            try {
                const response = await fetch(url, { signal: controller.signal });
                if (!response.ok) throw new Error('Network error');
                const result = await response.json();
                setData(result);
            } catch (err) {
                if (err.name !== 'AbortError') {
                    setError(err.message);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        return () => controller.abort();
    }, [url]);

    return { data, loading, error };
};

// Main App Component
const App = () => {
    const [theme, setTheme] = useState('light');
    const [user, setUser] = useState(null);
    const { data: posts, loading } = useFetch('/api/posts');

    // Load saved theme from localStorage
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            setTheme(savedTheme);
            document.body.classList.add(savedTheme);
        }
    }, []);

    // Toggle theme
    const toggleTheme = useCallback(() => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);

        document.body.classList.remove('light', 'dark');
        document.body.classList.add(newTheme);
    }, [theme]);

    // Handle login
    const handleLogin = async (credentials) => {
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials)
            });
            const userData = await res.json();
            setUser(userData);
            sessionStorage.setItem('user', JSON.stringify(userData));
        } catch (err) {
            console.error('Login failed:', err);
        }
    };

    // Filter posts
    const filteredPosts = posts?.filter(post => post.published) || [];
    const postTitles = filteredPosts.map(post => post.title);

    return (
        <div className={`app ${theme}`}>
            <header>
                <h1>{`Welcome${user ? `, ${user.name}` : ''}`}</h1>
                <button onClick={toggleTheme}>
                    {theme === 'light' ? '🌙' : '☀️'}
                </button>
            </header>

            {loading ? (
                <p>Loading...</p>
            ) : (
                <ul>
                    {filteredPosts.map((post, index) => (
                        <li key={post.id}>{post.title}</li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default App;
