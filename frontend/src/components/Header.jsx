import React from 'react'
import { Navbar, Nav, Container, Row, NavDropdown } from 'react-bootstrap'
import { LinkContainer } from 'react-router-bootstrap'


function Header() {

  return (
    <header >
        <Navbar collapseOnSelect expand="lg" className="bg-body-tertiary">
      <Container fluid>
        <LinkContainer to = "/">
        <Navbar.Brand  href="#home">海普瑞的chatbot</Navbar.Brand>
        </LinkContainer>
        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        <Navbar.Collapse id="responsive-navbar-nav">
          <Nav className="me-auto">
            <LinkContainer to = "/admin">
              <Nav.Link  href="#features">Admin</Nav.Link>
            </LinkContainer>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
    </header>
  )
}

export default Header