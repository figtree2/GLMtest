import React, { useState, useEffect, useRef } from 'react'
import { Row, Col, Container, Form, Button, InputGroup, ListGroup, Modal } from 'react-bootstrap'
import { FaPaperPlane, FaPlus } from 'react-icons/fa'
import io from 'socket.io-client'
import '../styles/main.scss'
import '../styles/textbox.scss'

const socket = io('http://127.0.0.1:5000')

function App() {
  const [showModal, setShowModal] = useState(false)
  const [addinput, setAddInput] = useState('')
  const [curId, setCurId] = useState('对话一')
  const textAreaRef = useRef(null)
  const [input, setInput] = useState('')
  const initMessages = () => {
    const storedData = localStorage.getItem('chats')
    if(storedData) {
      const data = JSON.parse(storedData)
      if(data[curId]){
        return data[curId]
      }
    }
    return []
  }
  const [messages, setMessages] = useState(initMessages)
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

    storeMessages(curId, messages)

    return ()=>{
      socket.off('message')
    }
  
  }, [messages, input, curId])

  useEffect(() => {
    getMessages(curId)
  }, [curId])

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
      setMessages([])
      if(data[id]){
        setMessages(data[id])
      }
    }
  }

  const getChats = () => {
    const storedData = localStorage.getItem('chats')
    let data = storedData ? JSON.parse(storedData) : {};
    return data
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

  const handleCreate = async (e) => {
    e.preventDefault()
    const storedData = localStorage.getItem('chats')
    let data = storedData ? JSON.parse(storedData) : {};


    if(addinput === ''){
      setAddInput('')
      return 
    }
    else if(data[addinput]){
      setCurId(addinput)
      handleCloseModal()
      getMessages(addinput)
      setAddInput('')
      return
    }
    else{
      data[addinput] = ""
      setCurId(addinput)
      handleCloseModal()
      getMessages(addinput)
      setAddInput('')
      return
    }
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

  const handleShowModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);
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
          <Row className = "row-bottom">
            <Button variant = 'primary' onClick = {handleShowModal}><FaPlus /></Button>
          </Row>
        </Col>
        <Col xs = {12} md = {10} className = "right-column">
            <Container fluid>
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
            </Container>
        </Col>
      </Row>

      <Modal show = {showModal} onHide = {handleCloseModal}>
          <Modal.Header>
            <Modal.Title>创造新对话界面</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form onSubmit = {handleCreate} className = "pretty-textbox-form">
              <InputGroup>
              <Form.Control 
              as = 'textarea'
              rows = {1}
              ref = {textAreaRef}
              type = 'text'
              value = {addinput}
              onChange={(e) => setAddInput(e.target.value)}
              onKeyDown={(e) => {if(e.key === 'Enter' && !e.shiftKey){setAddInput(e.target.form.requestSubmit())}}}
              placeholder = "请输入对话名称"
              className = "pretty-textbox2"
              />
              </InputGroup>
            </Form>
          </Modal.Body>
      </Modal>
    </Container>
  )
}

export default App
