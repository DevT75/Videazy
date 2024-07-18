import React from 'react'
import Layout from './components/Layout'
import { Home } from './components/Home'
import StaggerAnimation from './components/Stagger'

const App = () => {
  return (<>
    {/* <StaggerAnimation/> */}
    <Layout>
      <Home/>
    </Layout>
    </>
  )
}

export default App
