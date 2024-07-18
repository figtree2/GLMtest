import React from 'react'
import Header from './components/Header'
import Chatscreen from './screens/chatscreen'
import Admin from './screens/admin'
import { Container } from 'react-bootstrap'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

 
function App() {
  return (
    <BrowserRouter>
      <Header />
      <main className = "py-3">
        <Routes>
          <Route path = '/' element = {<Chatscreen/>} exact/>
          <Route path = '/admin' element = {<Admin />} exact/>
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App