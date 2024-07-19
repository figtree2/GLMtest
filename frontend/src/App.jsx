import React from 'react'
import Header from './components/Header'
import Chatscreen from './screens/chatscreen'
import Admin from './screens/admin'
import { Container } from 'react-bootstrap'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Provider } from 'react-redux'
import store from './redux/store'

 
function App() {
  return (
    <Provider store = {store}> 
      <BrowserRouter>
      <Header />
      <main className = "py-3">
        <Container fluid>
        <Routes>
          <Route path = '/' element = {<Chatscreen/>} exact/>
          <Route path = '/admin' element = {<Admin />} exact/>
        </Routes>
        </Container>
      </main>
    </BrowserRouter>
    </Provider>
  )
}

export default App