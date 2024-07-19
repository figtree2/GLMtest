import React, { useState, useEffect, useRef } from 'react'
import { Provider, useDispatch } from 'react-redux'
import { Row, Col, Container, Form, Button, InputGroup, ListGroup, Modal } from 'react-bootstrap'
import io from 'socket.io-client'
import '../styles/admin.scss'


const socket = io('http://127.0.0.1:5000')


function Admin() {
    const dispatch = useDispatch()

    const [vecs, setVecs] = useState([])

    const data = ['添加数据', '设定数据库']


    useEffect(() => {
        socket.emit('getVecs')

        socket.on('vectors', (data) => {
            setVecs(data)
        })

        return () => {
            socket.off('vectors')
            socket.off('error')
        }
    }, [])

  

  return (
        <Container fluid className = ".admin-container"> 
        <Row>
            <Col xs = {12} md = {4} className = "left">
            <ListGroup className = "buttons-list">
              {data.map((key) => (
                <ListGroup.Item key = {key}>
                  <Button variant = "primary">
                      {key}
                  </Button>
                </ListGroup.Item>
              ))}
            </ListGroup>
            </Col>
            <Col xs = {12} md = {8} className = "right">

            </Col>
        </Row>
    </Container>
  )
}

export default Admin