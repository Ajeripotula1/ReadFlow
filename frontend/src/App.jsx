import { BrowserRouter, Routes, Route } from "react-router-dom"
import './App.css'
import Login from "./pages/Login/Login"
import Home from "./pages/Home/Home"
import PrivateRoute from "./components/PrivateRoute"
import ReadingList from "./pages/ReadingList/ReadingList"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Login/>}/>
        {/* Protected route: Home */}
        <Route 
          path="/home" 
          element={
          <PrivateRoute>
            <Home/>
          </PrivateRoute>
          }/>

         <Route 
          path="/reading-list" 
          element={
          <PrivateRoute>
            <ReadingList/>
          </PrivateRoute>
          }/>
      </Routes>
    </BrowserRouter>
  )
}

export default App
