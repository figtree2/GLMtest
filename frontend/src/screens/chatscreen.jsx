import React, { useState, useEffect, useRef } from 'react'
import { Row, Col, Container, Form, Button, InputGroup, ListGroup } from 'react-bootstrap'
import { FaPaperPlane, FaPlus } from 'react-icons/fa'
import io from 'socket.io-client'
import '../styles/main.scss'
import '../styles/textbox.scss'

const socket = io('http://127.0.0.1:5000')

function App() {
  const [curId, setCurId] = useState('对话三')
  const textAreaRef = useRef(null)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [history, setHistory] = useState(() => {
    const storedHistory = localStorage.getItem('history')
    return storedHistory ? JSON.parse(storedHistory) : {};
  })  
  const chatRef = useRef(null)

  const scrollToBottom = () => {
    const chat = chatRef.current
    chat.scrollTop = chat.scrollHeight
  }

  useEffect(()=>{
    socket.on('message', (data) => {
      setMessages((prevMessages) => [...prevMessages, {type: 'backend', content: data.data}])
    })

    socket.on('history', (data) => {
      storeHistory(data.history)
    })


    scrollToBottom()

    if(textAreaRef.current) {
      textAreaRef.current.style.height = 'auto'
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`
    }



    return ()=>{
      socket.off('message')
      storeMessages(curId, messages)
    }
  
  }, [curId, messages, input])

  const storeHistory = (data) => {
    setHistory(data)
    console.log(data)
    localStorage.setItem('history', JSON.stringify(data))
  }

  const getMessages = (id) => {
    const storedData = localStorage.getItem('chats')
    if (storedData) {
      const data = JSON.parse(storedData)
      console.log(data[id])
      setMessages("")
      if(data[id]){
        setMessages(data[id])
      }
    }
  }

  const storeMessages = (id, message) => {
    const storedData = localStorage.getItem('chats')
    let data = storedData ? JSON.parse(storedData) : {};

    if(data[id]){
      delete data[id]
      data[id] = message
    }
    else{
      data[id] = message
    }

    localStorage.setItem('chats', JSON.stringify(data))
  }

  const handleSubmit = async (e) => {
    console.log(history)
    e.preventDefault()
    if(input.trim() !== ''){
      setMessages((prevMessages) => [...prevMessages, {type: 'user', content: input.trim()}])
    }
    await fetch('/api/chatbot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ input: input, store: history, id: curId })
    })
    setInput('')
  }

  const changeHistory = (id) => {
    setCurId(id)
    getMessages(id)
  }

  const renderMessages = (message) => {
    return messages.map((message, index) => {
      const isUser = message.type === 'user'
      let content = message.content

      if (isUser){
        return (
          <span key = {index} className = {`message ${isUser? 'user': 'backend'}`}>
            {content}
          </span>
        )
      }
      else{
        const elements = content.split(/(\*\*)/)
        let inBold = false;
        return elements.flatMap((part, index) => {
          if(part === "**"){
            inBold = !inBold
            return null
          }
          if(inBold){
            return <span key = {index} className = 'bold'>{part}</span>
          }
          else{
            return <span key = {index}>{part}</span>
          }
        })
      }
      
    })

  
  }


  return (
    <Container fluid>
      <Row>
        <Col xs = {12} md = {2} className = "left-column">
          <div className = "content">
            <ListGroup className = "buttons-list">
              {Object.keys(history).map((key) => (
                <ListGroup.Item key = {key}>
                  <Button variant = "primary" onClick = {() => changeHistory(key)}>
                      {key}
                  </Button>
                </ListGroup.Item>
              ))}
            </ListGroup>
          </div>
        </Col>
        <Col xs = {12} md = {10} className = "right-column">
        <div className = "container" >
      <div className = "scrollable-div" id = "chat" ref = {chatRef}>
        {renderMessages()}
      </div>
      <Form onSubmit = {handleSubmit} className = "pretty-textbox-form">
        <InputGroup>
          <Form.Control
          as = 'textarea'
          rows = {1}
          ref = {textAreaRef}
          type = 'text'
          value = {input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {if(e.key === 'Enter' && !e.shiftKey){setInput(e.target.form.requestSubmit())}}}
          placeholder = "请输入您的问题"
          className = "pretty-textbox"
           />
          <Button type = "submit" variant = "primary" className = "submit-button"><FaPaperPlane /></Button>
        </InputGroup>
      </Form>
    </div>
        </Col>
      </Row>
    </Container>
  )
}

export default App
