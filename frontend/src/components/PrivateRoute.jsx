import { Navigate } from "react-router-dom"; // Redirect tool
import { useAuth } from "../context/AuthContext"; // Access auth state

const PrivateRoute = ({ children }) => {
    const { isAuthenticated } = useAuth(); // check if user is logged in

    // If authenticated, render the children
    // If not, redirect to login page
    return isAuthenticated ? children: <Navigate to="/"/>
};

export default PrivateRoute