import React from 'react'

const BookCard = ({book, index}) => {
  return (
     <div key={index} className="book-card">
        <img src={book.image_url} alt={book.title} style={{ width: '100%', height: 'auto', borderRadius: '4px' }} />
        <h3>{book.title}</h3>
        <p>by {book.author}</p>
    </div>
  )
}

export default BookCard