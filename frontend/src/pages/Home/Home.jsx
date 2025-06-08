import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext"; // For logout
import axios from "axios";
import BookCard from "../../components/BookCard";
import "./Home.css"

const Home = () => {
  const { logout } = useAuth(); // Use logout function from context
  const [trending, setTrending] = useState([]);

  // On mount fetch trending
  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const res = await axios.get("http://localhost:8000/trending");
        console.log(res);
        setTrending(res.data.books);
      } catch (error) {
        console.log("Error fetching trending books", error.message);
      }
    };
    fetchTrending(); // run this on mount 
  }, []);

  return (
    <div>
      <div style={{display: "flex", justifyContent: "flex-end", padding: '0.5rem'}}>
         <button onClick={logout} style ={{padding:"5px"}}>Logout</button>
      </div>
      <h1>Welcome to ReadFlow!</h1>
      <h2>Trending this week</h2>
     <div className="trending">
        {trending.length > 0 ? (
          trending.map((book, index) => (
           <BookCard key={index} book={book}/>
          ))
        ) : (
          <p>No trending books found.</p>
        )}
      </div>
    </div>
  );
};

export default Home;
