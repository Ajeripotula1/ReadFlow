import { createContext, useContext, useState } from "react";

// Used by component to get login/logout/token info 
// Create a new context to share auth data across the app
// Context: provides a way to pass data through the component tree without prop drilling
// Consider it global state 
const AuthContext = createContext();

// Auth provider will wrap your entire app and make auth data accessible ot all components 
export const AuthProvider = ({ children }) => {
    // State to hold JWT token; initialize from localStorage to persist after refresh
    const [token,setToken] = useState(localStorage.getItem("token") || null);

    // Login function stores token in both state and localStorage
    const login = (token) => {
        setToken(token);
        localStorage.setItem("token",token); // Save to brower storage
    }
    
    const logout = () => {
        setToken(null);
        localStorage.removeItem("token")
    };

    const isAuthenticated = !!token;
    // Provide the token, auth status, and login/logout function to all children
    return (
        <AuthContext.Provider value={{ token, isAuthenticated,login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
export const useAuth = () => useContext(AuthContext)
