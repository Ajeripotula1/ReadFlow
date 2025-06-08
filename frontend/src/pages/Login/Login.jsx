import React, {useState} from 'react'
import { Form, useNavigate } from 'react-router-dom'
import {useAuth} from "../../context/AuthContext"
import axios from 'axios'
import './Login.css'

const Login = () => {

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  // const [error, setError] = useState('');
  // const[loading, setLoading] = useState('');

  const{ login } = useAuth(); // Login function from context
  const navigate = useNavigate()  // For redirecting user

  const handleLogin = async (e) =>{
    e.preventDefault();
    console.log(username, password)
    // 1. need to set up how i'm storing token
    // 2. do axios request to post to log in endpoint
    try{
      const response = await axios.post(
        "http://localhost:8000/token",
        new URLSearchParams({
          username: username,
          password: password
        }),
        {
          "headers": {
            "Content-Type": "application/x-www-form-urlencoded"
          },
        }
      )
      console.log("Login successful:", response.data)
      // Save token and mark user as logged in
      login(response.data.access_token)
      // redirect to dashboard/home
      navigate("/home")
    } catch(error) {
      alert("Login Failed, please check your credentials.")
      console.error("Login failed: ", error.response?.data||error.message)
    }
    // 3. handle the output
    // 4. how will i know the user it authenticated? 
  }
  return (
    <div className='container'>
      <h1>Welcome To ReadFlow</h1>
      <h2>Log In or Register to get started!</h2>
        <form onSubmit={handleLogin}>
          <input 
            type="text"
            placeholder="Username"
            value={username} //what we will store value as
            onChange={e=> setUsername(e.target.value)} //
          />
          <input 
            type="password"
            placeholder="Password"
            value={password} 
            onChange={e=>setPassword(e.target.value)}
          />
          <button type='submit'>Login</button>
        </form>
    </div>
  )
}

export default Login